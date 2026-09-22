@echo off
cd /d "%~dp0"
set "PATH=%USERPROFILE%\miniconda3\Library\bin;%PATH%"
python -m pip install -q pyinstaller pystray pillow
python -m PyInstaller --noconfirm --clean --onefile --windowed --name exe-link --distpath dist --workpath build --specpath build --hidden-import pystray._win32 --hidden-import PIL --collect-all pystray --add-binary "%USERPROFILE%\miniconda3\Library\bin\tk86t.dll;." --add-binary "%USERPROFILE%\miniconda3\Library\bin\tcl86t.dll;." exe-link.py
if errorlevel 1 (
  echo Build failed.
  pause
  exit /b 1
)
copy /Y dist\exe-link.exe "%~dp0exe-link.exe" >nul
echo.
echo Created: %~dp0exe-link.exe
echo Copy this file to other GPU PCs and double-click to run.
