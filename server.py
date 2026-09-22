#!/usr/bin/env python3
"""GPU Farm dashboard: scrape DCGM / NVML exporter metrics and serve a live UI."""

from __future__ import annotations

import json
import os
import re
import socket
import threading
import time
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, unquote, urlparse
from urllib.request import Request, urlopen

from batutil import (
    agent_url_for,
    bat_path_text,
    extra_args_text,
    http_json,
    list_bat_dir,
    list_bat_dir_for_node,
    parse_port,
    probe_agent,
    run_bat_on_node,
)

ROOT = Path(__file__).resolve().parent
WEB_DIR = ROOT / "web"
DATA_DIR = ROOT / "data"
NODES_FILE = DATA_DIR / "nodes.json"
SERVICES_FILE = DATA_DIR / "services.json"
GROUPS_FILE = DATA_DIR / "groups.json"

HOST = os.environ.get("GPU_FARM_HOST", "0.0.0.0")
PORT = int(os.environ.get("GPU_FARM_PORT", "9090"))
SCRAPE_TIMEOUT = 5
SERVICE_PROBE_TIMEOUT = 1.5
MAX_BODY = 8 * 1024 * 1024

SAMPLE_RE = re.compile(
    r"^([a-zA-Z_:][a-zA-Z0-9_:]*)(?:\{([^}]*)\})?\s+([^\s]+(?:e[+-]?\d+)?)\s*(?:\d+)?\s*$"
)
LABEL_RE = re.compile(r'([a-zA-Z_][a-zA-Z0-9_]*)="((?:\\.|[^"\\])*)"')

# Longer / more specific names must come first.
GPU_SPECS: list[tuple[str, dict[str, float]]] = [
    ("RTX 5090", {"tdp": 575, "max_sm": 2617}),
    ("RTX 5080", {"tdp": 360, "max_sm": 2617}),
    ("RTX 5070 Ti", {"tdp": 300, "max_sm": 2512}),
    ("RTX 5070", {"tdp": 250, "max_sm": 2512}),
    ("RTX 4090 D", {"tdp": 425, "max_sm": 3105}),
    ("RTX 4090", {"tdp": 450, "max_sm": 3105}),
    ("RTX 4080 SUPER", {"tdp": 320, "max_sm": 2550}),
    ("RTX 4080", {"tdp": 320, "max_sm": 2505}),
    ("RTX 4070 Ti SUPER", {"tdp": 285, "max_sm": 2610}),
    ("RTX 4070 Ti", {"tdp": 285, "max_sm": 2610}),
    ("RTX 4070 SUPER", {"tdp": 220, "max_sm": 2475}),
    ("RTX 4070", {"tdp": 200, "max_sm": 2475}),
    ("RTX 4060 Ti", {"tdp": 165, "max_sm": 2535}),
    ("RTX 4060", {"tdp": 115, "max_sm": 2460}),
    ("RTX 3090 Ti", {"tdp": 450, "max_sm": 1860}),
    ("RTX 3090", {"tdp": 350, "max_sm": 1695}),
    ("RTX 3080 Ti", {"tdp": 350, "max_sm": 1665}),
    ("RTX 3080", {"tdp": 320, "max_sm": 1710}),
    ("RTX 3070 Ti", {"tdp": 290, "max_sm": 1770}),
    ("RTX 3070", {"tdp": 220, "max_sm": 1725}),
    ("RTX 3060 Ti", {"tdp": 200, "max_sm": 1665}),
    ("RTX 3060", {"tdp": 170, "max_sm": 1777}),
    ("RTX A6000", {"tdp": 300, "max_sm": 1800}),
    ("RTX A5000", {"tdp": 230, "max_sm": 1695}),
    ("RTX 6000 Ada", {"tdp": 300, "max_sm": 2505}),
    ("L40S", {"tdp": 350, "max_sm": 2520}),
    ("L40", {"tdp": 300, "max_sm": 2490}),
    ("A100", {"tdp": 400, "max_sm": 1410}),
    ("H200", {"tdp": 700, "max_sm": 1980}),
    ("H100", {"tdp": 700, "max_sm": 1980}),
    ("A40", {"tdp": 300, "max_sm": 1740}),
    ("A10", {"tdp": 150, "max_sm": 1695}),
    ("Tesla T4", {"tdp": 70, "max_sm": 1590}),
    ("V100", {"tdp": 300, "max_sm": 1530}),
]

_lock = threading.Lock()


def gpu_specs(model: str) -> dict[str, float]:
    upper = model.upper()
    for name, spec in GPU_SPECS:
        if name.upper() in upper:
            return spec
    return {"tdp": 350, "max_sm": 2100}


def load_nodes() -> list[dict[str, Any]]:
    if not NODES_FILE.exists():
        return []
    try:
        data = json.loads(NODES_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    return data if isinstance(data, list) else []


def save_nodes(nodes: list[dict[str, Any]]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    tmp = NODES_FILE.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(nodes, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(NODES_FILE)


def load_services() -> list[dict[str, Any]]:
    if not SERVICES_FILE.exists():
        return []
    try:
        data = json.loads(SERVICES_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    return data if isinstance(data, list) else []


def save_services(services: list[dict[str, Any]]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    tmp = SERVICES_FILE.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(services, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(SERVICES_FILE)


def load_groups() -> list[dict[str, Any]]:
    if not GROUPS_FILE.exists():
        return []
    try:
        data = json.loads(GROUPS_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    return data if isinstance(data, list) else []


def save_groups(groups: list[dict[str, Any]]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    tmp = GROUPS_FILE.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(groups, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(GROUPS_FILE)


def group_name_text(raw: str) -> str:
    text = (raw or "").strip()
    if not text:
        raise ValueError("請輸入 Group 名稱")
    if len(text) > 80:
        raise ValueError("名稱太長")
    return text


def group_parent_id(raw: Any, groups: list[dict[str, Any]], self_id: str = "") -> str:
    parent_id = str(raw or "").strip()
    if not parent_id:
        return ""
    by_id = {item["id"]: item for item in groups}
    if parent_id not in by_id:
        raise ValueError("找不到上層 Group")
    if self_id and parent_id == self_id:
        raise ValueError("Group 不能放到自己裡面")
    current = parent_id
    seen = {self_id} if self_id else set()
    while current:
        if current in seen:
            raise ValueError("Group 不能放到自己的子層")
        seen.add(current)
        current = str((by_id.get(current) or {}).get("parent_id") or "").strip()
    return parent_id


def next_group_sort(groups: list[dict[str, Any]], parent_id: str) -> int:
    siblings = [item for item in groups if str(item.get("parent_id") or "") == parent_id]
    if not siblings:
        return 0
    return max(int(item.get("sort") or 0) for item in siblings) + 1


def add_group(name: str, parent_id: str = "") -> dict[str, Any]:
    with _lock:
        groups = load_groups()
        parent_id = group_parent_id(parent_id, groups)
        group = {
            "id": uuid.uuid4().hex,
            "name": group_name_text(name),
            "parent_id": parent_id,
            "sort": next_group_sort(groups, parent_id),
            "created_at": int(time.time()),
        }
        groups.append(group)
        save_groups(groups)
        return group


def rename_group(group_id: str, name: str) -> dict[str, Any]:
    group_id = (group_id or "").strip()
    if not group_id:
        raise ValueError("缺少 Group id")
    with _lock:
        groups = load_groups()
        target = next((item for item in groups if item["id"] == group_id), None)
        if target is None:
            raise ValueError("找不到這個 Group")
        target["name"] = group_name_text(name)
        save_groups(groups)
        return dict(target)


def delete_group(group_id: str) -> bool:
    group_id = (group_id or "").strip()
    if not group_id:
        return False
    with _lock:
        groups = load_groups()
        target = next((item for item in groups if item["id"] == group_id), None)
        if target is None:
            return False
        parent_id = str(target.get("parent_id") or "")
        kept: list[dict[str, Any]] = []
        for item in groups:
            if item["id"] == group_id:
                continue
            if str(item.get("parent_id") or "") == group_id:
                item["parent_id"] = parent_id
            kept.append(item)
        save_groups(kept)
        nodes = load_nodes()
        changed = False
        for node in nodes:
            if str(node.get("group_id") or "") == group_id:
                node["group_id"] = parent_id
                changed = True
        if changed:
            save_nodes(nodes)
        return True


def save_group_layout(groups_layout: Any, nodes_layout: Any) -> dict[str, Any]:
    if not isinstance(groups_layout, list) or not isinstance(nodes_layout, list):
        raise ValueError("版面資料格式不正確")
    with _lock:
        groups = load_groups()
        nodes = load_nodes()
        group_ids = {item["id"] for item in groups}
        node_ids = {item["id"] for item in nodes}
        incoming_groups: dict[str, dict[str, Any]] = {}
        for raw in groups_layout:
            if not isinstance(raw, dict):
                continue
            group_id = str(raw.get("id") or "").strip()
            if group_id not in group_ids:
                continue
            incoming_groups[group_id] = raw
        if set(incoming_groups) != group_ids:
            raise ValueError("Group 清單不完整")
        proposed: list[dict[str, Any]] = []
        for group in groups:
            raw = incoming_groups[group["id"]]
            try:
                sort = int(raw.get("sort") or 0)
            except (TypeError, ValueError) as exc:
                raise ValueError("排序必須是數字") from exc
            proposed.append({**group, "parent_id": str(raw.get("parent_id") or "").strip(), "sort": sort})
        for group in proposed:
            group["parent_id"] = group_parent_id(group.get("parent_id"), proposed, group["id"])
        groups = proposed
        incoming_nodes: dict[str, dict[str, Any]] = {}
        for raw in nodes_layout:
            if not isinstance(raw, dict):
                continue
            node_id = str(raw.get("id") or "").strip()
            if node_id not in node_ids:
                continue
            incoming_nodes[node_id] = raw
        for node in nodes:
            raw = incoming_nodes.get(node["id"]) or {}
            group_id = str(raw.get("group_id") or "").strip()
            if group_id and group_id not in group_ids:
                raise ValueError("找不到這個 Group")
            try:
                sort = int(raw.get("sort") or 0)
            except (TypeError, ValueError) as exc:
                raise ValueError("排序必須是數字") from exc
            node["group_id"] = group_id
            node["sort"] = sort
        save_groups(groups)
        save_nodes(nodes)
        return {"groups": groups, "nodes": [{"id": item["id"], "group_id": item.get("group_id") or "", "sort": int(item.get("sort") or 0)} for item in nodes]}


def normalize_service_target(raw: str) -> tuple[str, str, int]:
    text = (raw or "").strip()
    if not text:
        raise ValueError("請輸入服務 IP")
    if "://" not in text:
        text = "http://" + text
    parsed = urlparse(text)
    if parsed.scheme not in {"http", "https"}:
        raise ValueError("服務 IP 格式不正確")
    if not parsed.hostname:
        raise ValueError("服務 IP 缺少主機名稱")
    if parsed.username or parsed.password:
        raise ValueError("不支援帶帳密的服務位址")
    host = parsed.hostname
    port = parsed.port or (443 if parsed.scheme == "https" else 80)
    if port < 1 or port > 65535:
        raise ValueError("連接埠不正確")
    display = host if (parsed.scheme == "http" and port == 80 and not parsed.path) else f"{host}:{port}"
    if parsed.path not in {"", "/"}:
        display = f"{host}:{port}{parsed.path}"
    return display, host, int(port)


def probe_service(host: str, port: int) -> tuple[bool, str | None]:
    try:
        with socket.create_connection((host, port), timeout=SERVICE_PROBE_TIMEOUT):
            return True, None
    except TimeoutError:
        return False, "連線逾時"
    except OSError as exc:
        return False, str(exc.strerror or exc) or "無法連線"


def snapshot_service(service: dict[str, Any]) -> dict[str, Any]:
    online, error = probe_service(service["host"], int(service["port"]))
    return {
        "id": service["id"],
        "node_id": service.get("node_id") or "",
        "name": service["name"],
        "ip": service["ip"],
        "note": service.get("note") or "",
        "host": service["host"],
        "port": service["port"],
        "start_bat": service.get("start_bat") or "",
        "stop_bat": service.get("stop_bat") or "",
        "start_args": service.get("start_args") or "",
        "stop_args": service.get("stop_args") or "",
        "status": "online" if online else "offline",
        "error": None if online else error,
    }


def run_service_bat(service_id: str, action: str) -> dict[str, Any]:
    if action not in {"start", "stop"}:
        raise ValueError("動作不正確")
    with _lock:
        services = load_services()
        service = next((item for item in services if item["id"] == service_id), None)
        if service is None:
            raise ValueError("找不到這個服務")
        bat_key = "start_bat" if action == "start" else "stop_bat"
        raw = service.get(bat_key) or ""
        extra_args = service.get("start_args" if action == "start" else "stop_args") or ""
        node_id = service.get("node_id") or ""
        node = next((item for item in load_nodes() if item["id"] == node_id), None)
    if node is None:
        raise ValueError("找不到這個電腦節點")
    if not raw:
        raise ValueError("尚未設定啟動檔案" if action == "start" else "尚未設定終止檔案")
    result = run_bat_on_node(node, raw, action, extra_args)
    result["name"] = service["name"]
    return result


def _service_fields(name: str, ip: str, note: str) -> tuple[str, str, str, str, int]:
    title = (name or "").strip()
    if not title:
        raise ValueError("請輸入服務名稱")
    if len(title) > 80:
        raise ValueError("服務名稱太長")
    blurb = (note or "").strip()
    if len(blurb) > 300:
        raise ValueError("說明太長")
    display, host, port = normalize_service_target(ip)
    return title, blurb, display, host, port


def add_service(
    node_id: str,
    name: str,
    ip: str,
    note: str,
    start_bat: str = "",
    stop_bat: str = "",
    start_args: str = "",
    stop_args: str = "",
) -> dict[str, Any]:
    node_id = (node_id or "").strip()
    if not node_id:
        raise ValueError("缺少電腦節點")
    title, blurb, display, host, port = _service_fields(name, ip, note)
    start_path = bat_path_text(start_bat)
    stop_path = bat_path_text(stop_bat)
    start_extra = extra_args_text(start_args)
    stop_extra = extra_args_text(stop_args)
    with _lock:
        nodes = load_nodes()
        if not any(item["id"] == node_id for item in nodes):
            raise ValueError("找不到這個電腦節點")
        services = load_services()
        for item in services:
            if item.get("node_id") != node_id:
                continue
            if item["host"] == host and int(item["port"]) == port:
                raise ValueError("這台電腦已經有這個服務位址")
            if item["name"].strip().lower() == title.lower():
                raise ValueError("這台電腦已經有同名的服務")
        service = {
            "id": uuid.uuid4().hex,
            "node_id": node_id,
            "name": title,
            "ip": display,
            "note": blurb,
            "host": host,
            "port": port,
            "start_bat": start_path,
            "stop_bat": stop_path,
            "start_args": start_extra,
            "stop_args": stop_extra,
            "created_at": int(time.time()),
        }
        services.append(service)
        save_services(services)
    return service


def update_service(
    service_id: str,
    name: str,
    ip: str,
    note: str,
    start_bat: str = "",
    stop_bat: str = "",
    start_args: str = "",
    stop_args: str = "",
) -> dict[str, Any]:
    service_id = (service_id or "").strip()
    if not service_id:
        raise ValueError("缺少服務 id")
    title, blurb, display, host, port = _service_fields(name, ip, note)
    start_path = bat_path_text(start_bat)
    stop_path = bat_path_text(stop_bat)
    start_extra = extra_args_text(start_args)
    stop_extra = extra_args_text(stop_args)
    with _lock:
        services = load_services()
        target = None
        for item in services:
            if item["id"] == service_id:
                target = item
                break
        if target is None:
            raise ValueError("找不到這個服務")
        node_id = target.get("node_id") or ""
        for item in services:
            if item["id"] == service_id or item.get("node_id") != node_id:
                continue
            if item["host"] == host and int(item["port"]) == port:
                raise ValueError("這台電腦已經有這個服務位址")
            if item["name"].strip().lower() == title.lower():
                raise ValueError("這台電腦已經有同名的服務")
        target["name"] = title
        target["note"] = blurb
        target["ip"] = display
        target["host"] = host
        target["port"] = port
        target["start_bat"] = start_path
        target["stop_bat"] = stop_path
        target["start_args"] = start_extra
        target["stop_args"] = stop_extra
        save_services(services)
        return dict(target)


def remove_service(service_id: str) -> bool:
    with _lock:
        services = load_services()
        kept = [item for item in services if item["id"] != service_id]
        if len(kept) == len(services):
            return False
        save_services(kept)
        nodes = load_nodes()
        changed = False
        for node in nodes:
            pins = list(node.get("pinned_service_ids") or [])
            if service_id in pins:
                node["pinned_service_ids"] = [item for item in pins if item != service_id]
                changed = True
        if changed:
            save_nodes(nodes)
        return True


def toggle_pin(node_id: str, service_id: str) -> dict[str, Any]:
    service_id = (service_id or "").strip()
    if not service_id:
        raise ValueError("缺少服務 id")
    with _lock:
        services = load_services()
        owned = [item for item in services if item["id"] == service_id and item.get("node_id") == node_id]
        if not owned:
            raise ValueError("找不到這個服務")
        nodes = load_nodes()
        for node in nodes:
            if node["id"] != node_id:
                continue
            pins = list(node.get("pinned_service_ids") or [])
            if service_id in pins:
                pins.remove(service_id)
                pinned = False
            else:
                pins.append(service_id)
                pinned = True
            node["pinned_service_ids"] = pins
            save_nodes(nodes)
            return {"pinned": pinned, "pinned_service_ids": pins}
        raise ValueError("找不到這個節點")


def normalize_url(raw: str) -> str:
    text = (raw or "").strip()
    if not text:
        raise ValueError("請輸入 DCGM metrics 網址")
    if "://" not in text:
        text = "http://" + text
    parsed = urlparse(text)
    if parsed.scheme not in {"http", "https"}:
        raise ValueError("只支援 http 或 https 網址")
    if not parsed.hostname:
        raise ValueError("網址缺少主機名稱或 IP")
    if parsed.username or parsed.password:
        raise ValueError("不支援帶帳密的網址")
    path = parsed.path or "/"
    if path in {"", "/"}:
        path = "/metrics"
    netloc = parsed.hostname
    if parsed.port:
        netloc = f"{netloc}:{parsed.port}"
    elif path == "/metrics":
        netloc = f"{netloc}:9400"
    return f"{parsed.scheme}://{netloc}{path}"


def unescape_label(value: str) -> str:
    return value.replace(r"\\", "\\").replace(r"\"", '"').replace(r"\n", "\n")


def parse_labels(blob: str | None) -> dict[str, str]:
    if not blob:
        return {}
    return {
        key: unescape_label(value)
        for key, value in LABEL_RE.findall(blob)
    }


def to_float(raw: str) -> float | None:
    try:
        value = float(raw)
    except ValueError:
        return None
    if value != value or value in {float("inf"), float("-inf")}:
        return None
    return value


def parse_prometheus(text: str) -> tuple[str, list[dict[str, Any]]]:
    exporter = "dcgm-exporter"
    by_gpu: dict[str, dict[str, Any]] = {}

    def gpu_entry(labels: dict[str, str]) -> dict[str, Any] | None:
        gpu_id = labels.get("UUID") or labels.get("gpu") or labels.get("device")
        if gpu_id is None:
            return None
        entry = by_gpu.get(gpu_id)
        if entry is None:
            entry = {
                "index": labels.get("gpu", ""),
                "uuid": labels.get("UUID", gpu_id),
                "model": labels.get("modelName", "Unknown GPU"),
                "hostname": labels.get("Hostname", ""),
                "driver": labels.get("DCGM_FI_DRIVER_VERSION", ""),
                "device": labels.get("device", ""),
                "metrics": {},
                "processes": [],
            }
            by_gpu[gpu_id] = entry
        else:
            if not entry["model"] and labels.get("modelName"):
                entry["model"] = labels["modelName"]
            if not entry["hostname"] and labels.get("Hostname"):
                entry["hostname"] = labels["Hostname"]
            if not entry["driver"] and labels.get("DCGM_FI_DRIVER_VERSION"):
                entry["driver"] = labels["DCGM_FI_DRIVER_VERSION"]
            if entry["index"] == "" and labels.get("gpu") is not None:
                entry["index"] = labels["gpu"]
        return entry

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("# Generated by "):
            exporter = line[len("# Generated by ") :].split(" (", 1)[0].strip() or exporter
            continue
        if line.startswith("#"):
            continue
        match = SAMPLE_RE.match(line)
        if not match:
            continue
        name, label_blob, value_raw = match.groups()
        value = to_float(value_raw)
        if value is None:
            continue
        labels = parse_labels(label_blob)
        entry = gpu_entry(labels)
        if entry is None:
            continue
        if name.startswith("NVML_PROCESS_"):
            pid = labels.get("pid", "")
            process = labels.get("process") or (f"pid:{pid}" if pid else "unknown")
            found = None
            for proc in entry["processes"]:
                if proc["pid"] == pid and proc["name"] == process:
                    found = proc
                    break
            if found is None:
                found = {"pid": pid, "name": process, "fb_used": 0.0, "util": 0.0}
                entry["processes"].append(found)
            if name == "NVML_PROCESS_FB_USED":
                found["fb_used"] = value
            elif name == "NVML_PROCESS_GPU_UTIL":
                found["util"] = value
            continue
        entry["metrics"][name] = value

    gpus: list[dict[str, Any]] = []
    for entry in by_gpu.values():
        metrics = entry["metrics"]
        if not metrics:
            continue
        model = entry["model"] or "Unknown GPU"
        specs = gpu_specs(model)
        used = float(metrics.get("DCGM_FI_DEV_FB_USED") or 0)
        free = float(metrics.get("DCGM_FI_DEV_FB_FREE") or 0)
        reserved = float(metrics.get("DCGM_FI_DEV_FB_RESERVED") or 0)
        total = used + free + reserved
        tdp = float(metrics.get("DCGM_FI_DEV_POWER_MGMT_LIMIT") or specs["tdp"])
        sm = float(metrics.get("DCGM_FI_DEV_SM_CLOCK") or 0)
        max_sm = float(
            metrics.get("DCGM_FI_DEV_MAX_SM_CLOCK")
            or metrics.get("DCGM_FI_MAX_SM_CLOCK")
            or max(specs["max_sm"], sm)
        )
        try:
            index = int(entry["index"]) if str(entry["index"]).strip() != "" else 0
        except ValueError:
            index = 0
        processes = [
            proc
            for proc in entry["processes"]
            if proc["fb_used"] > 1 or proc["util"] > 0
        ]
        processes.sort(key=lambda item: (item["fb_used"], item["util"]), reverse=True)
        gpus.append(
            {
                "index": index,
                "uuid": entry["uuid"],
                "model": model,
                "device": entry["device"],
                "util": metrics.get("DCGM_FI_DEV_GPU_UTIL"),
                "temp": metrics.get("DCGM_FI_DEV_GPU_TEMP"),
                "power": metrics.get("DCGM_FI_DEV_POWER_USAGE"),
                "power_limit": tdp,
                "mem_used_mib": used,
                "mem_free_mib": free,
                "mem_reserved_mib": reserved,
                "mem_total_mib": total,
                "sm_clock": sm,
                "max_sm_clock": max_sm,
                "mem_clock": metrics.get("DCGM_FI_DEV_MEM_CLOCK"),
                "hostname": entry["hostname"],
                "driver": entry["driver"],
                "processes": processes[:8],
            }
        )

    gpus.sort(key=lambda item: item["index"])
    return exporter, gpus


def scrape_url(url: str) -> dict[str, Any]:
    request = Request(url, headers={"User-Agent": "pz-gpu-farm/1.0", "Accept": "text/plain"})
    try:
        with urlopen(request, timeout=SCRAPE_TIMEOUT) as response:
            raw = response.read(MAX_BODY + 1)
            status = getattr(response, "status", 200)
    except HTTPError as exc:
        return {"ok": False, "error": f"HTTP {exc.code}", "exporter": "", "gpus": [], "hostname": "", "driver": ""}
    except URLError as exc:
        reason = getattr(exc, "reason", exc)
        return {"ok": False, "error": str(reason) or "無法連線", "exporter": "", "gpus": [], "hostname": "", "driver": ""}
    except TimeoutError:
        return {"ok": False, "error": "連線逾時", "exporter": "", "gpus": [], "hostname": "", "driver": ""}
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "error": str(exc), "exporter": "", "gpus": [], "hostname": "", "driver": ""}

    if len(raw) > MAX_BODY:
        return {"ok": False, "error": "metrics 內容過大", "exporter": "", "gpus": [], "hostname": "", "driver": ""}
    if status >= 400:
        return {"ok": False, "error": f"HTTP {status}", "exporter": "", "gpus": [], "hostname": "", "driver": ""}

    text = raw.decode("utf-8", errors="replace")
    exporter, gpus = parse_prometheus(text)
    hostname = next((gpu["hostname"] for gpu in gpus if gpu.get("hostname")), "")
    driver = next((gpu["driver"] for gpu in gpus if gpu.get("driver")), "")
    if not gpus:
        return {
            "ok": False,
            "error": "找不到 GPU metrics",
            "exporter": exporter,
            "gpus": [],
            "hostname": hostname,
            "driver": driver,
        }
    return {
        "ok": True,
        "error": None,
        "exporter": exporter,
        "gpus": gpus,
        "hostname": hostname,
        "driver": driver,
    }


def snapshot_node(node: dict[str, Any]) -> dict[str, Any]:
    started = time.time()
    scraped = scrape_url(node["url"])
    agent = probe_agent(node)
    return {
        "id": node["id"],
        "url": node["url"],
        "status": "ready" if scraped["ok"] else "offline",
        "error": scraped["error"],
        "exporter": scraped["exporter"] or "dcgm-exporter",
        "hostname": scraped["hostname"] or urlparse(node["url"]).hostname or "unknown",
        "driver": scraped["driver"],
        "gpus": scraped["gpus"],
        "latency_ms": int((time.time() - started) * 1000),
        "pinned_service_ids": list(node.get("pinned_service_ids") or []),
        "group_id": node.get("group_id") or "",
        "sort": int(node.get("sort") or 0),
        **agent,
    }


def build_snapshot() -> dict[str, Any]:
    with _lock:
        nodes = list(load_nodes())
        services = list(load_services())
        groups = list(load_groups())
    results: list[dict[str, Any]] = []
    service_results: list[dict[str, Any]] = []
    workers = min(16, max(1, len(nodes) + len(services)))
    with ThreadPoolExecutor(max_workers=workers) as pool:
        node_futures = {pool.submit(snapshot_node, node): node["id"] for node in nodes}
        service_futures = {pool.submit(snapshot_service, service): service["id"] for service in services}
        by_id = {node["id"]: node for node in nodes}
        collected: dict[str, dict[str, Any]] = {}
        for future in as_completed(node_futures):
            node_id = node_futures[future]
            try:
                collected[node_id] = future.result()
            except Exception as exc:  # noqa: BLE001
                node = by_id[node_id]
                collected[node_id] = {
                    "id": node_id,
                    "url": node["url"],
                    "status": "offline",
                    "error": str(exc),
                    "exporter": "dcgm-exporter",
                    "hostname": urlparse(node["url"]).hostname or "unknown",
                    "driver": "",
                    "gpus": [],
                    "latency_ms": 0,
                    "pinned_service_ids": list(node.get("pinned_service_ids") or []),
                    "group_id": node.get("group_id") or "",
                    "sort": int(node.get("sort") or 0),
                    **probe_agent(node),
                }
        results = [collected[node["id"]] for node in nodes if node["id"] in collected]
        service_collected: dict[str, dict[str, Any]] = {}
        for future in as_completed(service_futures):
            service_id = service_futures[future]
            try:
                service_collected[service_id] = future.result()
            except Exception as exc:  # noqa: BLE001
                original = next(item for item in services if item["id"] == service_id)
                service_collected[service_id] = {
                    "id": service_id,
                    "node_id": original.get("node_id") or "",
                    "name": original["name"],
                    "ip": original["ip"],
                    "note": original.get("note") or "",
                    "host": original["host"],
                    "port": original["port"],
                    "start_bat": original.get("start_bat") or "",
                    "stop_bat": original.get("stop_bat") or "",
                    "start_args": original.get("start_args") or "",
                    "stop_args": original.get("stop_args") or "",
                    "status": "offline",
                    "error": str(exc),
                }
        service_results = [service_collected[item["id"]] for item in services if item["id"] in service_collected]
    by_node: dict[str, list[dict[str, Any]]] = {}
    for service in service_results:
        by_node.setdefault(service.get("node_id") or "", []).append(service)
    for node in results:
        node["services"] = by_node.get(node["id"], [])
    return {"nodes": results, "groups": groups, "updated_at": int(time.time() * 1000)}


def add_node(url: str) -> dict[str, Any]:
    normalized = normalize_url(url)
    scraped = scrape_url(normalized)
    if not scraped["ok"]:
        raise ValueError(scraped["error"] or "無法讀取 metrics")
    with _lock:
        nodes = load_nodes()
        for node in nodes:
            if node["url"] == normalized:
                raise ValueError("這個網址已經加入過了")
        node = {
            "id": uuid.uuid4().hex,
            "url": normalized,
            "created_at": int(time.time()),
        }
        nodes.append(node)
        save_nodes(nodes)
    return node


def remove_node(node_id: str) -> bool:
    with _lock:
        nodes = load_nodes()
        kept = [node for node in nodes if node["id"] != node_id]
        if len(kept) == len(nodes):
            return False
        save_nodes(kept)
        services = [item for item in load_services() if item.get("node_id") != node_id]
        save_services(services)
        return True


def update_node_agent_port(node_id: str, port_raw: str) -> dict[str, Any]:
    node_id = (node_id or "").strip()
    if not node_id:
        raise ValueError("缺少節點 id")
    port = parse_port(port_raw)
    with _lock:
        nodes = load_nodes()
        target = next((item for item in nodes if item["id"] == node_id), None)
        if target is None:
            raise ValueError("找不到這個電腦節點")
        old_url = agent_url_for(target)
        target["agent_port"] = port
        host = urlparse(target["url"]).hostname or ""
        if host:
            target["agent_url"] = f"http://{host}:{port}"
        save_nodes(nodes)
        saved = dict(target)
    notice = None
    old_port = urlparse(old_url).port
    if old_port != port:
        try:
            http_json("POST", f"{old_url}/api/port", {"port": port}, timeout=4)
            time.sleep(0.45)
        except ValueError as exc:
            notice = str(exc)
    probe = probe_agent(saved)
    return {
        "ok": True,
        "id": saved["id"],
        "notice": notice,
        **probe,
        "agent_port": port,
    }


MIME = {
    ".html": "text/html; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".js": "application/javascript; charset=utf-8",
    ".json": "application/json; charset=utf-8",
    ".svg": "image/svg+xml",
    ".png": "image/png",
    ".ico": "image/x-icon",
}


class FarmHandler(BaseHTTPRequestHandler):
    server_version = "pz-gpu-farm/1.0"

    def log_message(self, fmt: str, *args: Any) -> None:
        path = args[0] if args else ""
        if isinstance(path, str) and path.startswith("GET /api/snapshot"):
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

    def _read_json(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length", "0") or 0)
        if length <= 0:
            return {}
        if length > 64 * 1024:
            raise ValueError("請提供 JSON 內容")
        raw = self.rfile.read(length)
        if not raw.strip():
            return {}
        data = json.loads(raw.decode("utf-8"))
        if not isinstance(data, dict):
            raise ValueError("JSON 格式不正確")
        return data

    def do_GET(self) -> None:  # noqa: N802
        path = self.path.split("?", 1)[0]
        if path == "/api/groups":
            with _lock:
                self._send_json(200, {"groups": load_groups()})
            return
        if path == "/api/snapshot":
            self._send_json(200, build_snapshot())
            return
        if path == "/api/nodes":
            with _lock:
                self._send_json(200, {"nodes": load_nodes()})
            return
        if path == "/api/files":
            query = parse_qs(urlparse(self.path).query)
            dir_raw = unquote(query.get("dir", [""])[0] or "")
            node_id = unquote(query.get("node_id", [""])[0] or "")
            try:
                if node_id:
                    with _lock:
                        node = next((item for item in load_nodes() if item["id"] == node_id), None)
                    if node is None:
                        raise ValueError("找不到這個電腦節點")
                    listing = list_bat_dir_for_node(node, dir_raw)
                else:
                    listing = list_bat_dir(dir_raw)
            except ValueError as exc:
                self._send_json(400, {"error": str(exc)})
                return
            self._send_json(200, listing)
            return
        if path in {"/", "/index.html"}:
            self._serve_file(WEB_DIR / "index.html")
            return
        relative = path.lstrip("/")
        target = (WEB_DIR / relative).resolve()
        if WEB_DIR.resolve() in target.parents or target == WEB_DIR.resolve():
            self._serve_file(target)
            return
        self._send_json(404, {"error": "not found"})

    def do_POST(self) -> None:  # noqa: N802
        path = self.path.split("?", 1)[0]
        try:
            payload = self._read_json()
        except ValueError as exc:
            self._send_json(400, {"error": str(exc)})
            return
        except json.JSONDecodeError:
            self._send_json(400, {"error": "JSON 格式不正確"})
            return
        try:
            if path == "/api/groups":
                group = add_group(str(payload.get("name") or ""), str(payload.get("parent_id") or ""))
                self._send_json(201, {"group": group})
                return
            if path == "/api/groups/layout":
                result = save_group_layout(payload.get("groups"), payload.get("nodes"))
                self._send_json(200, result)
                return
            if path == "/api/nodes":
                node = add_node(str(payload.get("url") or ""))
                self._send_json(201, {"node": node})
                return
            if path == "/api/services":
                service = add_service(
                    str(payload.get("node_id") or ""),
                    str(payload.get("name") or ""),
                    str(payload.get("ip") or ""),
                    str(payload.get("note") or ""),
                    str(payload.get("start_bat") or ""),
                    str(payload.get("stop_bat") or ""),
                    str(payload.get("start_args") or ""),
                    str(payload.get("stop_args") or ""),
                )
                self._send_json(201, {"service": service})
                return
            pin_prefix = "/api/nodes/"
            if path.startswith(pin_prefix) and path.endswith("/services"):
                node_id = path[len(pin_prefix) : -len("/services")].strip("/")
                if not node_id:
                    raise ValueError("缺少節點 id")
                service = add_service(
                    node_id,
                    str(payload.get("name") or ""),
                    str(payload.get("ip") or ""),
                    str(payload.get("note") or ""),
                    str(payload.get("start_bat") or ""),
                    str(payload.get("stop_bat") or ""),
                    str(payload.get("start_args") or ""),
                    str(payload.get("stop_args") or ""),
                )
                self._send_json(201, {"service": service})
                return
            if path.startswith("/api/services/") and path.endswith("/start"):
                service_id = path[len("/api/services/") : -len("/start")].strip("/")
                result = run_service_bat(service_id, "start")
                self._send_json(200, result)
                return
            if path.startswith("/api/services/") and path.endswith("/stop"):
                service_id = path[len("/api/services/") : -len("/stop")].strip("/")
                result = run_service_bat(service_id, "stop")
                self._send_json(200, result)
                return
            if path.startswith(pin_prefix) and path.endswith("/agent"):
                node_id = path[len(pin_prefix) : -len("/agent")].strip("/")
                if not node_id:
                    raise ValueError("缺少節點 id")
                result = update_node_agent_port(node_id, str(payload.get("port") or ""))
                self._send_json(200, result)
                return
            if path.startswith(pin_prefix) and path.endswith("/pin"):
                node_id = path[len(pin_prefix) : -len("/pin")].strip("/")
                if not node_id:
                    raise ValueError("缺少節點 id")
                result = toggle_pin(node_id, str(payload.get("service_id") or ""))
                self._send_json(200, result)
                return
        except ValueError as exc:
            self._send_json(400, {"error": str(exc)})
            return
        self._send_json(404, {"error": "not found"})

    def do_PUT(self) -> None:  # noqa: N802
        path = self.path.split("?", 1)[0]
        if path.startswith("/api/groups/"):
            group_id = path[len("/api/groups/") :].strip("/")
            if not group_id or "/" in group_id:
                self._send_json(400, {"error": "缺少 Group id"})
                return
            try:
                payload = self._read_json()
                group = rename_group(group_id, str(payload.get("name") or ""))
            except ValueError as exc:
                self._send_json(400, {"error": str(exc)})
                return
            except json.JSONDecodeError:
                self._send_json(400, {"error": "JSON 格式不正確"})
                return
            self._send_json(200, {"group": group})
            return
        if not path.startswith("/api/services/"):
            self._send_json(404, {"error": "not found"})
            return
        service_id = path[len("/api/services/") :].strip("/")
        if not service_id or "/" in service_id:
            self._send_json(400, {"error": "缺少服務 id"})
            return
        try:
            payload = self._read_json()
            service = update_service(
                service_id,
                str(payload.get("name") or ""),
                str(payload.get("ip") or ""),
                str(payload.get("note") or ""),
                str(payload.get("start_bat") or ""),
                str(payload.get("stop_bat") or ""),
                str(payload.get("start_args") or ""),
                str(payload.get("stop_args") or ""),
            )
        except ValueError as exc:
            self._send_json(400, {"error": str(exc)})
            return
        except json.JSONDecodeError:
            self._send_json(400, {"error": "JSON 格式不正確"})
            return
        self._send_json(200, {"service": service})

    def do_DELETE(self) -> None:  # noqa: N802
        path = self.path.split("?", 1)[0]
        if path.startswith("/api/groups/"):
            group_id = path[len("/api/groups/") :].strip("/")
            if not group_id or "/" in group_id:
                self._send_json(400, {"error": "缺少 Group id"})
                return
            if not delete_group(group_id):
                self._send_json(404, {"error": "找不到這個 Group"})
                return
            self._send_json(200, {"ok": True})
            return
        if path.startswith("/api/nodes/"):
            node_id = path[len("/api/nodes/") :].strip("/")
            if not node_id or "/" in node_id:
                self._send_json(400, {"error": "缺少節點 id"})
                return
            if not remove_node(node_id):
                self._send_json(404, {"error": "找不到這個節點"})
                return
            self._send_json(200, {"ok": True})
            return
        if path.startswith("/api/services/"):
            service_id = path[len("/api/services/") :].strip("/")
            if not service_id or "/" in service_id:
                self._send_json(400, {"error": "缺少服務 id"})
                return
            if not remove_service(service_id):
                self._send_json(404, {"error": "找不到這個服務"})
                return
            self._send_json(200, {"ok": True})
            return
        self._send_json(404, {"error": "not found"})

    def _serve_file(self, path: Path) -> None:
        if not path.is_file():
            self._send_json(404, {"error": "not found"})
            return
        data = path.read_bytes()
        content_type = MIME.get(path.suffix.lower(), "application/octet-stream")
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        self.wfile.write(data)


def migrate_orphan_services() -> None:
    with _lock:
        nodes = load_nodes()
        services = load_services()
        host_to_id = {}
        for node in nodes:
            host = urlparse(node["url"]).hostname
            if host and host not in host_to_id:
                host_to_id[host] = node["id"]
        changed = False
        kept: list[dict[str, Any]] = []
        for service in services:
            node_id = service.get("node_id")
            if not node_id:
                node_id = host_to_id.get(service.get("host") or "")
                if node_id:
                    service["node_id"] = node_id
                    changed = True
            if node_id:
                kept.append(service)
            else:
                changed = True
        if changed:
            save_services(kept)


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not NODES_FILE.exists():
        save_nodes([])
    if not SERVICES_FILE.exists():
        save_services([])
    if not GROUPS_FILE.exists():
        save_groups([])
    migrate_orphan_services()
    httpd = ThreadingHTTPServer((HOST, PORT), FarmHandler)
    print(f"GPU Farm  http://127.0.0.1:{PORT}", flush=True)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped")
    finally:
        httpd.server_close()


if __name__ == "__main__":
    main()
