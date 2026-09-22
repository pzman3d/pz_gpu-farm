#!/usr/bin/env python3
"""exe-link: tray + GUI helper so the farm dashboard can start/stop local files."""

from __future__ import annotations

import json
import os
import socket
import threading
import time
import tkinter as tk
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Callable
from urllib.parse import parse_qs, unquote, urlparse

from batutil import (
    APP_NAME,
    APP_TITLE,
    TOKEN,
    bat_path_text,
    launch_bat,
    list_bat_dir,
    load_agent_lang,
    load_agent_port,
    parse_port,
    save_agent_lang,
    save_agent_port,
)

HOST = os.environ.get("GPU_FARM_AGENT_HOST", "0.0.0.0")
CURRENT_PORT = load_agent_port()
PORT_CHANGE_CB: Callable[[int], None] | None = None
GUI: "LinkGui | None" = None

TEXTS = {
    "zh": {
        "title": APP_TITLE,
        "hint": "縮小或關閉視窗會收到右下角系統托盤。雙擊圖示可再打開。",
        "port": "Port",
        "update": "更新",
        "listening": "監聽中",
        "updated": "已更新並重新監聽",
        "show": "顯示",
        "quit": "結束",
        "no_tray": "未安裝托盤元件",
        "listen_fail": "無法監聽這個 Port",
        "bad_token": "exe-link token 不正確",
        "need_json": "請提供 JSON 內容",
        "bad_json": "JSON 格式不正確",
        "bad_action": "動作不正確",
    },
    "en": {
        "title": APP_TITLE,
        "hint": "Minimize or close this window to hide it in the system tray. Double-click the icon to show it again.",
        "port": "Port",
        "update": "Update",
        "listening": "Listening",
        "updated": "Updated and listening again",
        "show": "Show",
        "quit": "Quit",
        "no_tray": "Tray component not installed",
        "listen_fail": "Could not listen on this port",
        "bad_token": "Invalid exe-link token",
        "need_json": "JSON body required",
        "bad_json": "Invalid JSON",
        "bad_action": "Invalid action",
    },
}


def current_lang() -> str:
    if GUI is not None:
        return GUI.lang
    return load_agent_lang()


def tr(key: str) -> str:
    lang = current_lang()
    table = TEXTS.get(lang) or TEXTS["zh"]
    return table.get(key) or TEXTS["zh"][key]


class ReuseHTTPServer(ThreadingHTTPServer):
    allow_reuse_address = True
    daemon_threads = True


class AgentHandler(BaseHTTPRequestHandler):
    server_version = "pz-gpu-farm-exe-link/1.1"

    def log_message(self, fmt: str, *args: Any) -> None:
        path = args[0] if args else ""
        if isinstance(path, str) and path.startswith("GET /health"):
            return
        super().log_message(fmt, *args)

    def _send(self, status: int, body: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _send_json(self, status: int, payload: Any) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self._send(status, body, "application/json; charset=utf-8")

    def _authorized(self) -> bool:
        if not TOKEN:
            return True
        if self.headers.get("X-GPU-Farm-Token") == TOKEN:
            return True
        self._send_json(401, {"error": tr("bad_token")})
        return False

    def _read_json(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length", "0") or 0)
        if length <= 0:
            return {}
        if length > 64 * 1024:
            raise ValueError(tr("need_json"))
        raw = self.rfile.read(length)
        if not raw.strip():
            return {}
        data = json.loads(raw.decode("utf-8"))
        if not isinstance(data, dict):
            raise ValueError(tr("bad_json"))
        return data

    def do_GET(self) -> None:  # noqa: N802
        path = self.path.split("?", 1)[0]
        if path == "/health":
            self._send_json(
                200,
                {
                    "ok": True,
                    "role": "exe-link",
                    "hostname": socket.gethostname(),
                    "port": CURRENT_PORT,
                    "title": APP_TITLE,
                    "lang": current_lang(),
                },
            )
            return
        if path == "/api/files":
            if not self._authorized():
                return
            query = parse_qs(urlparse(self.path).query)
            try:
                listing = list_bat_dir(unquote(query.get("dir", [""])[0] or ""))
            except ValueError as exc:
                self._send_json(400, {"error": str(exc)})
                return
            self._send_json(200, listing)
            return
        self._send_json(404, {"error": "not found"})

    def do_POST(self) -> None:  # noqa: N802
        path = self.path.split("?", 1)[0]
        if path == "/api/port":
            if not self._authorized():
                return
            try:
                payload = self._read_json()
                port = parse_port(payload.get("port"))
            except ValueError as exc:
                self._send_json(400, {"error": str(exc)})
                return
            except json.JSONDecodeError:
                self._send_json(400, {"error": tr("bad_json")})
                return
            self._send_json(200, {"ok": True, "port": port})
            if PORT_CHANGE_CB:
                PORT_CHANGE_CB(port)
            return
        if path != "/api/run":
            self._send_json(404, {"error": "not found"})
            return
        if not self._authorized():
            return
        try:
            payload = self._read_json()
            action = str(payload.get("action") or "start")
            if action not in {"start", "stop"}:
                raise ValueError(tr("bad_action"))
            result = launch_bat(
                bat_path_text(str(payload.get("path") or "")),
                action,
                str(payload.get("args") or ""),
            )
        except ValueError as exc:
            self._send_json(400, {"error": str(exc)})
            return
        except json.JSONDecodeError:
            self._send_json(400, {"error": tr("bad_json")})
            return
        self._send_json(200, result)


class HttpService:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self.httpd: ReuseHTTPServer | None = None
        self.thread: threading.Thread | None = None
        self.port = CURRENT_PORT

    def start(self, port: int | None = None) -> None:
        with self._lock:
            if port is not None:
                self.port = parse_port(port)
            self._stop_locked()
            httpd = ReuseHTTPServer((HOST, self.port), AgentHandler)
            thread = threading.Thread(target=httpd.serve_forever, name="exe-link-http", daemon=True)
            thread.start()
            self.httpd = httpd
            self.thread = thread
            global CURRENT_PORT
            CURRENT_PORT = self.port

    def stop(self) -> None:
        with self._lock:
            self._stop_locked()

    def _stop_locked(self) -> None:
        httpd = self.httpd
        self.httpd = None
        if httpd is None:
            return
        threading.Thread(target=httpd.shutdown, daemon=True).start()
        time.sleep(0.15)
        try:
            httpd.server_close()
        except OSError:
            pass


HTTP = HttpService()


def apply_port(port: int, from_http: bool = False) -> None:
    port = parse_port(port)
    save_agent_port(port)

    def restart() -> None:
        HTTP.start(port)
        if GUI is not None:
            GUI.root.after(0, lambda: GUI.set_port(port, GUI.t("updated")))

    if from_http:
        threading.Thread(target=lambda: (time.sleep(0.25), restart()), daemon=True).start()
    else:
        restart()


def make_tray_image():
    from PIL import Image, ImageDraw

    image = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((4, 4, 60, 60), 16, fill=(182, 227, 53, 255))
    draw.ellipse((22, 22, 42, 42), fill=(12, 17, 23, 255))
    return image


class LinkGui:
    def __init__(self) -> None:
        self.lang = load_agent_lang()
        self.root = tk.Tk()
        self.root.geometry("440x250")
        self.root.minsize(400, 230)
        self.root.configure(bg="#0c1117")
        self.status = tk.StringVar()
        self.port_var = tk.StringVar(value=str(CURRENT_PORT))
        self.icon = None
        self.title_label: tk.Label | None = None
        self.hint_label: tk.Label | None = None
        self.port_label: tk.Label | None = None
        self.update_btn: tk.Button | None = None
        self.lang_zh: tk.Button | None = None
        self.lang_en: tk.Button | None = None
        self._build()
        self.root.protocol("WM_DELETE_WINDOW", self.hide_to_tray)
        self.root.bind("<Unmap>", self._on_unmap)
        self.apply_lang()
        self.set_port(CURRENT_PORT, self.t("listening"))

    def t(self, key: str) -> str:
        table = TEXTS.get(self.lang) or TEXTS["zh"]
        return table.get(key) or TEXTS["zh"][key]

    def _build(self) -> None:
        header = tk.Frame(self.root, bg="#0c1117")
        header.pack(fill="x", padx=18, pady=(12, 6))
        self.title_label = tk.Label(
            header,
            fg="#b6e335",
            bg="#0c1117",
            font=("Segoe UI", 14, "bold"),
        )
        self.title_label.pack(side="left")
        lang_row = tk.Frame(header, bg="#0c1117")
        lang_row.pack(side="right")
        self.lang_zh = tk.Button(
            lang_row,
            text="中文",
            command=lambda: self.set_lang("zh"),
            relief="flat",
            padx=8,
            pady=2,
        )
        self.lang_zh.pack(side="left")
        self.lang_en = tk.Button(
            lang_row,
            text="EN",
            command=lambda: self.set_lang("en"),
            relief="flat",
            padx=8,
            pady=2,
        )
        self.lang_en.pack(side="left", padx=(4, 0))
        self.hint_label = tk.Label(
            self.root,
            fg="#8b97a6",
            bg="#0c1117",
            wraplength=400,
            justify="left",
        )
        self.hint_label.pack(anchor="w", padx=18)
        row = tk.Frame(self.root, bg="#0c1117")
        row.pack(fill="x", padx=18, pady=12)
        self.port_label = tk.Label(row, fg="#e8edf2", bg="#0c1117")
        self.port_label.pack(side="left")
        entry = tk.Entry(row, textvariable=self.port_var, width=10, relief="flat")
        entry.pack(side="left", padx=8, ipady=4)
        self.update_btn = tk.Button(
            row,
            command=self.update_port,
            bg="#b6e335",
            fg="#06210f",
            relief="flat",
            padx=12,
            pady=4,
        )
        self.update_btn.pack(side="left")
        tk.Label(self.root, textvariable=self.status, fg="#3dcc7a", bg="#0c1117", wraplength=400, justify="left").pack(
            anchor="w",
            padx=18,
            pady=8,
        )

    def _paint_lang_buttons(self) -> None:
        active = {"bg": "#243040", "fg": "#e8edf2"}
        idle = {"bg": "#18222c", "fg": "#8b97a6"}
        if self.lang_zh is not None:
            self.lang_zh.configure(**(active if self.lang == "zh" else idle))
        if self.lang_en is not None:
            self.lang_en.configure(**(active if self.lang == "en" else idle))

    def apply_lang(self) -> None:
        self.root.title(self.t("title"))
        if self.title_label is not None:
            self.title_label.configure(text=self.t("title"))
        if self.hint_label is not None:
            self.hint_label.configure(text=self.t("hint"))
        if self.port_label is not None:
            self.port_label.configure(text=self.t("port"))
        if self.update_btn is not None:
            self.update_btn.configure(text=self.t("update"))
        self._paint_lang_buttons()
        self.set_port(CURRENT_PORT, self.t("listening"))
        self.rebuild_tray_menu()

    def set_lang(self, lang: str) -> None:
        self.lang = "en" if lang == "en" else "zh"
        save_agent_lang(self.lang)
        self.apply_lang()

    def host_line(self, port: int) -> str:
        return f"http://{socket.gethostname()}:{port}"

    def set_port(self, port: int, message: str) -> None:
        self.port_var.set(str(port))
        self.status.set(f"{message}  {self.host_line(port)}")

    def update_port(self) -> None:
        try:
            port = parse_port(self.port_var.get())
            apply_port(port, from_http=False)
        except ValueError as exc:
            self.status.set(str(exc))
        except OSError as exc:
            self.status.set(str(exc) or self.t("listen_fail"))

    def hide_to_tray(self) -> None:
        self.root.withdraw()

    def _on_unmap(self, event: tk.Event) -> None:
        if event.widget is self.root and self.root.state() == "iconic":
            self.hide_to_tray()

    def show(self, icon=None, item=None) -> None:
        self.root.after(0, self._show)

    def _show(self) -> None:
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()

    def quit(self, icon=None, item=None) -> None:
        if self.icon is not None:
            try:
                self.icon.stop()
            except Exception:
                pass
        HTTP.stop()
        self.root.after(0, self.root.destroy)

    def rebuild_tray_menu(self) -> None:
        if self.icon is None:
            return
        try:
            import pystray
        except ImportError:
            return
        self.icon.title = self.t("title")
        self.icon.menu = pystray.Menu(
            pystray.MenuItem(self.t("show"), self.show, default=True),
            pystray.MenuItem(self.t("quit"), self.quit),
        )
        try:
            self.icon.update_menu()
        except Exception:
            pass

    def start_tray(self) -> None:
        try:
            import pystray
        except ImportError:
            self.status.set(f"{self.t('listening')}  {self.host_line(CURRENT_PORT)}（{self.t('no_tray')}）")
            return
        menu = pystray.Menu(
            pystray.MenuItem(self.t("show"), self.show, default=True),
            pystray.MenuItem(self.t("quit"), self.quit),
        )
        self.icon = pystray.Icon(APP_NAME, make_tray_image(), self.t("title"), menu)
        threading.Thread(target=self.icon.run, name="exe-link-tray", daemon=True).start()

    def run(self) -> None:
        self.start_tray()
        self.root.mainloop()


def main() -> None:
    global GUI, PORT_CHANGE_CB
    HTTP.start(CURRENT_PORT)
    GUI = LinkGui()
    PORT_CHANGE_CB = lambda port: apply_port(port, from_http=True)
    GUI.run()


if __name__ == "__main__":
    main()
