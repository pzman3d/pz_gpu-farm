@echo off
cd /d "%~dp0"
rem Change the port here, then save and run this file.
set "PORT=9090"

set "GPU_FARM_PORT=%PORT%"
echo PZ GPU FARM  http://127.0.0.1:%PORT%
python -u server.py
if errorlevel 1 pause
