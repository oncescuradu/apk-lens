@echo off
cd /d "%~dp0"
py -3 -m pip install pyinstaller
if errorlevel 1 exit /b 1
py -3 -m PyInstaller --noconfirm --clean --onefile --windowed --name APK-Lens app.py
if errorlevel 1 pause
