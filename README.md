# PZ GPU FARM

**Version 1.0.0** · 2026-09-22

[English](README.en.md)

## 介紹

PZ GPU FARM 是一套輕量 Web 工具，用來監看多台電腦的 GPU，並管理其上的 AI／Web-UI 服務。它讀取各機的 DCGM（或相容）metrics，在一個頁面掌握 GPU 使用狀況，也能連線、啟動或關閉各台機器上的服務。

---

## 更新重點

PZ GPU FARM 分為兩部分：

| | 放哪 | 做什麼 |
| --- | --- | --- |
| **PZ GPU FARM** | 公司服務端電腦 | 執行 `start.bat` 即可開啟儀表板 |
| **exe-link** | 各台 GPU 電腦 | 讓儀表板遠端啟動／強制關閉該機程式 |

在儀表板為每個 AI 服務指定啟動、終止用的 `.bat` / `.exe`。當機或需要重啟時，不必跑到那台電腦，從網頁即可處理。

**Metrics**：讀取 [NVIDIA dcgm-exporter](https://github.com/NVIDIA/dcgm-exporter) 相容的 Prometheus `/metrics`。沒有 DCGM 時，可用 [pz-nvml-dcgm-exporter](https://github.com/pzman3d/pz-nvml-dcgm-exporter) 在各 GPU 電腦快速提供相同格式。

---

## 需求

- Python 3.10+（儀表板為標準函式庫，不必 `pip install`）
- 各 GPU 電腦提供 dcgm-exporter 相容的 `/metrics`（預設 `http://<IP>:9400/metrics`；可搭配 [pz-nvml-dcgm-exporter](https://github.com/pzman3d/pz-nvml-dcgm-exporter)）
- 遠端啟動／終止：GPU 電腦需跑 exe-link（`pip install pystray pillow`；打包再加 `pyinstaller`）

## 1. 服務端：PZ GPU FARM

```bat
start.bat
```

預設 `http://127.0.0.1:9090`。改埠請編輯 `start.bat` 的 `set "PORT=9090"`。

右上角可切換 **中文 | EN**（預設英文）。用 **GROUP** 分組、**ADD GPU** 加入節點（例如 `http://192.168.1.10:9400/metrics`）。

## 2. 各 GPU 電腦：exe-link

同一台電腦上啟動／終止會直接執行；其他電腦需先跑 exe-link（預設埠 **9091**）。

```bat
cd exe-link
build.bat
```

把 `exe-link.exe` 複製到目標電腦後雙擊。或 `run.bat` 用 Python 執行。儀表板上該節點燈號變綠即為在線；點燈號可改 Port。

## 3. 啟動／終止服務

在節點扳手裡為服務指定該機上的 `.bat` / `.cmd` / `.exe` 與參數。掉線按啟動、卡住按終止，exe-link 會在該機執行。

**PIN**：只把該服務排到最前並高亮，不會啟動程式。

---

上傳 GitHub 請用 **`public/` 的內容**當儲存庫根目錄。

| 上傳 | 不要上傳 |
| --- | --- |
| `README.md`、`README.en.md`、`VERSION`、`.gitignore`、`start.bat` | `data/*.json`（內網 IP、本機路徑） |
| `server.py`、`batutil.py`、`web/` | `*.exe`（請自行 `build.bat` 或放 Releases） |
| `exe-link/` 原始碼與 `build.bat` / `run.bat` | `DEL/`、`build/`、`exe-link.json`、帳密權杖 |
| `data/.gitkeep` | |

`GPU_FARM_PORT` 預設 9090；`GPU_FARM_AGENT_PORT` 預設 9091。可選 `GPU_FARM_TOKEN`（Farm 與 exe-link 需相同）。

## 贊助 / Sponsor

[paypal.me/pzman3d](https://paypal.me/pzman3d)
