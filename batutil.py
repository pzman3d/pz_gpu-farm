"""Shared BAT listing / launch helpers for the farm server and remote exe-link."""

from __future__ import annotations

import json
import os
import shlex
import socket
import stat
import string
import subprocess
import sys
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlparse
from urllib.request import Request, urlopen

ROOT = Path(sys.executable).resolve().parent if getattr(sys, "frozen", False) else Path(__file__).resolve().parent
RUN_EXTS = {".bat", ".cmd", ".exe"}
BAT_EXTS = RUN_EXTS
DEFAULT_AGENT_PORT = int(os.environ.get("GPU_FARM_AGENT_PORT", "9091"))
AGENT_PORT = DEFAULT_AGENT_PORT
AGENT_TIMEOUT = 1.5
TOKEN = os.environ.get("GPU_FARM_TOKEN", "").strip()
APP_NAME = "exe-link"
APP_TITLE = "pz gpu farm : exe-link"
MAX_ARGS_LEN = 500
CONFIG_FILE = ROOT / "exe-link.json"

_local_hosts: set[str] | None = None


def bat_path_text(raw: str) -> str:
    text = (raw or "").strip().strip('"')
    if not text:
        return ""
    if Path(text).suffix.lower() not in RUN_EXTS:
        raise ValueError("只支援 .bat、.cmd 或 .exe")
    return text


def extra_args_text(raw: str) -> str:
    text = (raw or "").strip()
    if len(text) > MAX_ARGS_LEN:
        raise ValueError("參數太長")
    parse_extra_args(text)
    return text


def parse_extra_args(raw: str) -> list[str]:
    text = (raw or "").strip()
    if not text:
        return []
    try:
        parts = shlex.split(text, posix=False)
    except ValueError as exc:
        raise ValueError("參數格式不正確，請檢查引號") from exc
    return [part for part in parts if part]


def launch_bat(raw: str, action: str = "start", extra_args: str = "") -> dict[str, Any]:
    text = bat_path_text(raw)
    if not text:
        raise ValueError("尚未設定啟動檔案" if action == "start" else "尚未設定終止檔案")
    path = Path(text).expanduser()
    if not path.is_absolute():
        path = (ROOT / path).resolve()
    else:
        path = path.resolve()
    suffix = path.suffix.lower()
    if suffix not in RUN_EXTS:
        raise ValueError("只支援 .bat、.cmd 或 .exe")
    if not path.is_file():
        raise ValueError(f"找不到檔案：{path}")
    args = parse_extra_args(extra_args)
    if os.name == "nt":
        command = [str(path), *args] if suffix == ".exe" else ["cmd.exe", "/c", str(path), *args]
        flags = subprocess.CREATE_NEW_CONSOLE
    else:
        command = [str(path), *args] if suffix == ".exe" else ["bash", str(path), *args]
        flags = 0
    try:
        proc = subprocess.Popen(command, cwd=str(path.parent), creationflags=flags)
    except OSError as exc:
        raise ValueError(str(exc) or "無法執行檔案") from exc
    return {
        "ok": True,
        "action": action,
        "pid": proc.pid,
        "path": str(path),
        "args": args,
        "hostname": socket.gethostname(),
    }


def list_bat_dir(dir_raw: str) -> dict[str, Any]:
    text = (dir_raw or "").strip().strip('"')
    if text:
        cwd = Path(text).expanduser()
        if not cwd.is_absolute():
            cwd = ROOT / cwd
        try:
            cwd = cwd.resolve()
        except OSError as exc:
            raise ValueError(str(exc) or "無法開啟資料夾") from exc
    else:
        cwd = ROOT
    if not cwd.exists() or not cwd.is_dir():
        raise ValueError("找不到這個資料夾")
    parent = "" if cwd.parent == cwd else str(cwd.parent)
    dirs: list[str] = []
    files: list[dict[str, str]] = []
    hidden_flag = getattr(stat, "FILE_ATTRIBUTE_HIDDEN", 0)
    reparse_flag = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
    try:
        for item in cwd.iterdir():
            try:
                if item.name.startswith(".") or item.name == "__pycache__":
                    continue
                attrs = getattr(item.stat(), "st_file_attributes", 0)
                if attrs & (hidden_flag | reparse_flag):
                    continue
                if item.is_dir():
                    dirs.append(item.name)
                elif item.is_file() and item.suffix.lower() in BAT_EXTS:
                    files.append({"name": item.name, "path": str(item.resolve())})
            except OSError:
                continue
    except OSError as exc:
        raise ValueError(str(exc) or "無法讀取資料夾") from exc
    dirs.sort(key=str.lower)
    files.sort(key=lambda item: item["name"].lower())
    drives = [f"{letter}:\\" for letter in string.ascii_uppercase if Path(f"{letter}:/").exists()] if os.name == "nt" else []
    return {"cwd": str(cwd), "parent": parent, "dirs": dirs, "files": files, "drives": drives}


def local_hosts() -> set[str]:
    global _local_hosts
    if _local_hosts is not None:
        return _local_hosts
    names = {"127.0.0.1", "localhost", "::1"}
    try:
        names.add(socket.gethostname().lower())
        names.add(socket.getfqdn().lower())
    except OSError:
        pass
    try:
        for info in socket.getaddrinfo(socket.gethostname(), None):
            names.add(str(info[4][0]).split("%")[0].lower())
    except OSError:
        pass
    try:
        probe = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        probe.connect(("8.8.8.8", 80))
        names.add(probe.getsockname()[0])
        probe.close()
    except OSError:
        pass
    _local_hosts = names
    return names


def is_local_host(host: str) -> bool:
    text = (host or "").strip().lower()
    if not text:
        return False
    if text.startswith("[") and text.endswith("]"):
        text = text[1:-1]
    return text in local_hosts()


def node_host(node: dict[str, Any]) -> str:
    return urlparse(str(node.get("url") or "")).hostname or ""


def parse_port(raw: Any) -> int:
    text = str(raw or "").strip()
    if not text:
        raise ValueError("請輸入 Port")
    try:
        port = int(text)
    except (TypeError, ValueError) as exc:
        raise ValueError("Port 必須是數字") from exc
    if port < 1 or port > 65535:
        raise ValueError("Port 需介於 1–65535")
    return port


def load_agent_config() -> dict[str, Any]:
    data: dict[str, Any] = {"port": DEFAULT_AGENT_PORT, "lang": "en"}
    try:
        raw = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, ValueError):
        return data
    if not isinstance(raw, dict):
        return data
    if raw.get("port") is not None:
        try:
            data["port"] = parse_port(raw.get("port"))
        except ValueError:
            pass
    lang = str(raw.get("lang") or "en").strip().lower()
    data["lang"] = "zh" if lang == "zh" else "en"
    return data


def save_agent_config(*, port: int | None = None, lang: str | None = None) -> None:
    data = load_agent_config()
    if port is not None:
        data["port"] = parse_port(port)
    if lang is not None:
        data["lang"] = "en" if str(lang).strip().lower() == "en" else "zh"
    CONFIG_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def load_agent_port() -> int:
    env = (os.environ.get("GPU_FARM_AGENT_PORT") or "").strip()
    if env:
        return parse_port(env)
    return int(load_agent_config().get("port") or DEFAULT_AGENT_PORT)


def save_agent_port(port: int) -> None:
    save_agent_config(port=port)


def load_agent_lang() -> str:
    env = (os.environ.get("GPU_FARM_LANG") or "").strip().lower()
    if env in {"en", "zh"}:
        return env
    lang = str(load_agent_config().get("lang") or "en").strip().lower()
    return "zh" if lang == "zh" else "en"


def save_agent_lang(lang: str) -> None:
    save_agent_config(lang=lang)


def agent_port_for(node: dict[str, Any]) -> int:
    raw = node.get("agent_port")
    if raw not in (None, ""):
        try:
            return parse_port(raw)
        except ValueError:
            pass
    custom = str(node.get("agent_url") or "").strip()
    if custom:
        parsed = urlparse(custom)
        if parsed.port:
            return parsed.port
    return DEFAULT_AGENT_PORT


def agent_url_for(node: dict[str, Any]) -> str:
    host = node_host(node)
    if not host:
        raise ValueError("這個節點沒有主機位址")
    return f"http://{host}:{agent_port_for(node)}"


def agent_headers() -> dict[str, str]:
    headers = {"Accept": "application/json", "User-Agent": "pz-gpu-farm/1.0"}
    if TOKEN:
        headers["X-GPU-Farm-Token"] = TOKEN
    return headers


def agent_offline_error(url: str) -> str:
    host = urlparse(url).hostname or "目標電腦"
    return (
        f"{host} 上的 exe-link 未上線，無法在那台電腦執行 BAT。"
        f"請在該電腦執行 exe-link.exe（埠 {urlparse(url).port or DEFAULT_AGENT_PORT}）。"
    )


def http_json(method: str, url: str, payload: dict[str, Any] | None = None, timeout: float = 8) -> Any:
    body = None
    headers = agent_headers()
    if payload is not None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json; charset=utf-8"
    request = Request(url, data=body, headers=headers, method=method)
    try:
        with urlopen(request, timeout=timeout) as response:
            raw = response.read().decode("utf-8")
            return json.loads(raw) if raw.strip() else {}
    except HTTPError as exc:
        raw = exc.read().decode("utf-8", "replace")
        try:
            data = json.loads(raw) if raw.strip() else {}
        except json.JSONDecodeError:
            data = {}
        raise ValueError(str(data.get("error") or raw or f"HTTP {exc.code}")) from exc
    except URLError as exc:
        raise ValueError(agent_offline_error(url)) from exc
    except TimeoutError as exc:
        raise ValueError(agent_offline_error(url)) from exc


def probe_agent(node: dict[str, Any]) -> dict[str, Any]:
    host = node_host(node)
    url = agent_url_for(node)
    port = agent_port_for(node)
    if is_local_host(host):
        return {
            "agent_status": "local",
            "agent_local": True,
            "agent_url": url,
            "agent_port": port,
            "agent_error": None,
        }
    try:
        data = http_json("GET", f"{url}/health", timeout=AGENT_TIMEOUT)
        if not data.get("ok"):
            raise ValueError(data.get("error") or "exe-link 未就緒")
        live = data.get("port")
        return {
            "agent_status": "online",
            "agent_local": False,
            "agent_url": url,
            "agent_port": parse_port(live) if live not in (None, "") else port,
            "agent_error": None,
        }
    except ValueError as exc:
        return {
            "agent_status": "offline",
            "agent_local": False,
            "agent_url": url,
            "agent_port": port,
            "agent_error": str(exc),
        }


def list_bat_dir_for_node(node: dict[str, Any], dir_raw: str) -> dict[str, Any]:
    if is_local_host(node_host(node)):
        listing = list_bat_dir(dir_raw)
        listing["scope"] = "local"
        return listing
    url = agent_url_for(node)
    query = urlencode({"dir": dir_raw or ""})
    listing = http_json("GET", f"{url}/api/files?{query}")
    if not isinstance(listing, dict):
        raise ValueError("exe-link 回傳格式不正確")
    listing["scope"] = "remote"
    return listing


def run_bat_on_node(node: dict[str, Any], raw: str, action: str, extra_args: str = "") -> dict[str, Any]:
    if is_local_host(node_host(node)):
        result = launch_bat(raw, action, extra_args)
        result["scope"] = "local"
        return result
    url = agent_url_for(node)
    result = http_json("POST", f"{url}/api/run", {"path": raw, "action": action, "args": extra_args})
    if not isinstance(result, dict):
        raise ValueError("exe-link 回傳格式不正確")
    result["scope"] = "remote"
    return result
