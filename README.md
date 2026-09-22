# PZ GPU FARM
<img width="1886" height="937" alt="image" src="https://github.com/user-attachments/assets/c9b810b5-27d0-41ec-b6a0-2a0494bd5908" />

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
- 遠端啟動／終止：各 GPU 電腦執行編譯好的 `exe-link.exe` 即可（不必裝 Python）

## 1. 服務端：PZ GPU FARM

```bat
start.bat
```

預設 `http://127.0.0.1:9090`。改埠請編輯 `start.bat` 的 `set "PORT=9090"`。

右上角可切換 **中文 | EN**（預設英文）。用 **GROUP** 分組、**ADD GPU** 加入節點（例如 `http://192.168.1.10:9400/metrics`）。

## 2. 各 GPU 電腦：exe-link.exe

編譯完成的 **exe-link.exe** 可在各電腦直接雙擊執行，不必安裝 Python，即可與 PZ GPU FARM 連線互動。

1. 把 `exe-link.exe` 複製到目標 GPU 電腦（任意資料夾）
2. 雙擊執行；縮小或關閉會收到系統托盤
3. 預設埠 **9091**（視窗內可改；儀表板上點該節點燈號也可改）
4. Farm 加入該電腦後，exe-link 燈號變綠即已連上，之後可從網頁啟動／終止該機程式

Windows 防火牆若擋連線，請允許 9091。Farm 與 exe-link 若設了 `GPU_FARM_TOKEN`，兩邊必須相同。與 Farm 同一台電腦時，啟動／終止會直接在本機執行，不必另開 exe-link。

自行編譯（開發機需 Python）：

```bat
cd exe-link
build.bat
```

產出 `exe-link/exe-link.exe`。或用 `run.bat` 以 Python 執行原始碼。

## 3. 啟動／終止服務

在節點扳手裡為服務指定該機上的 `.bat` / `.cmd` / `.exe` 與參數。掉線按啟動、卡住按終止，exe-link 會在該機執行。

**PIN**：只把該服務排到最前並高亮，不會啟動程式。

---

## 贊助 / Sponsor

[paypal.me/pzman3d](https://paypal.me/pzman3d)


[paypal.me/pzman3d](https://paypal.me/pzman3d)
