# PZ GPU FARM

**Version 1.0.0** · 2026-09-22

[中文](README.md)

## About

PZ GPU FARM is a lightweight web tool for watching GPUs across many PCs and managing the AI / Web-UI services on them. It reads each machine’s DCGM-compatible metrics so you can see GPU usage in one place, then open those services or start and stop them from the browser.

---

## Highlights

PZ GPU FARM has two parts:

| | Where | What it does |
| --- | --- | --- |
| **PZ GPU FARM** | Office server | Run `start.bat` to open the dashboard |
| **exe-link** | Each GPU PC | Lets the dashboard start or force-quit programs on that machine |

Assign a start/stop `.bat` / `.exe` to each AI service. If a process crashes or needs a restart, you handle it in the browser—no trip to that PC.

**Metrics**: Reads Prometheus `/metrics` in [NVIDIA dcgm-exporter](https://github.com/NVIDIA/dcgm-exporter) format. If DCGM is unavailable, [pz-nvml-dcgm-exporter](https://github.com/pzman3d/pz-nvml-dcgm-exporter) can serve the same data on each GPU PC.

---

## Requirements

- Python 3.10+ (the dashboard is stdlib only; no `pip install`)
- Each GPU PC must expose dcgm-exporter–compatible `/metrics` (default `http://<IP>:9400/metrics`; [pz-nvml-dcgm-exporter](https://github.com/pzman3d/pz-nvml-dcgm-exporter) works)
- Remote start/stop: run exe-link on that PC (`pip install pystray pillow`; add `pyinstaller` to build the exe)

## 1. Server: PZ GPU FARM

```bat
start.bat
```

Default: `http://127.0.0.1:9090`. To change the port, edit `set "PORT=9090"` in `start.bat`.

Switch **中文 | EN** in the top-right (English by default). Use **GROUP** to organize PCs and **ADD GPU** to add a node (e.g. `http://192.168.1.10:9400/metrics`).

## 2. Each GPU PC: exe-link

Start/stop on the same machine as the farm runs locally. Other PCs need exe-link first (default port **9091**).

```bat
cd exe-link
build.bat
```

Copy `exe-link.exe` to the target PC and double-click it. Or run `run.bat` with Python. The node light on the dashboard turns green when it is online; click it to change the port.

## 3. Start / stop services

In the node wrench panel, pick a `.bat` / `.cmd` / `.exe` on that PC and optional arguments. Start when the service is down; Stop when it is stuck. exe-link runs the file on that machine.

**PIN**: only sorts that service to the front and highlights it. It does not launch anything.

---

Upload the **contents of `public/`** as the repository root.

| Include | Do not upload |
| --- | --- |
| `README.md`, `README.en.md`, `VERSION`, `.gitignore`, `start.bat` | `data/*.json` (LAN IPs, local paths) |
| `server.py`, `batutil.py`, `web/` | `*.exe` (build with `build.bat`, or attach to Releases) |
| `exe-link/` sources plus `build.bat` / `run.bat` | `DEL/`, `build/`, `exe-link.json`, tokens |
| `data/.gitkeep` | |

`GPU_FARM_PORT` defaults to 9090; `GPU_FARM_AGENT_PORT` defaults to 9091. Optional `GPU_FARM_TOKEN` must match on the farm and exe-link.

## Sponsor

[paypal.me/pzman3d](https://paypal.me/pzman3d)
