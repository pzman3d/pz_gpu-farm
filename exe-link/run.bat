@echo off
cd /d "%~dp0"
python -m pip install -q -r requirements.txt
python -u exe-link.py
if errorlevel 1 pause
