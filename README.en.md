# PZ GPU FARM
<img width="1886" height="937" alt="image" src="https://github.com/user-attachments/assets/c9b810b5-27d0-41ec-b6a0-2a0494bd5908" />

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
- Remote start/stop: run the compiled `exe-link.exe` on each GPU PC (no Python install required)

## 1. Server: PZ GPU FARM

```bat
start.bat
```

Default: `http://127.0.0.1:9090`. To change the port, edit `set "PORT=9090"` in `start.bat`.

Switch **中文 | EN** in the top-right (English by default). Use **GROUP** to organize PCs and **ADD GPU** to add a node (e.g. `http://192.168.1.10:9400/metrics`).

## 2. Each GPU PC: exe-link.exe
<img width="430" height="183" alt="image" src="https://github.com/user-attachments/assets/53216749-f885-4501-8490-8f7ff286bc6b" />


The compiled **exe-link.exe** runs on each PC with a double-click—no Python install—and talks directly to PZ GPU FARM.

1. Copy `exe-link.exe` to the GPU PC (any folder)
2. Double-click it; minimize or close to hide it in the system tray
3. Default port **9091** (change it in the window, or click the node light on the dashboard)
4. After you add that PC in the farm, a green exe-link light means it is connected; start/stop files from the browser after that

Allow port 9091 in Windows Firewall if the farm cannot reach it. If `GPU_FARM_TOKEN` is set, it must match on both sides. On the same PC as the farm, start/stop runs locally—exe-link is not required there.

To build it yourself (Python on a dev machine):

```bat
cd exe-link
build.bat
```

This writes `exe-link/exe-link.exe`. Or use `run.bat` to run the Python source.

## 3. Start / stop services

In the node wrench panel, pick a `.bat` / `.cmd` / `.exe` on that PC and optional arguments. Start when the service is down; Stop when it is stuck. exe-link runs the file on that machine.

**PIN**: only sorts that service to the front and highlights it. It does not launch anything.

---

## Sponsor

[paypal.me/pzman3d](https://paypal.me/pzman3d)
