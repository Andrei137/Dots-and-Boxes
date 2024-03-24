@echo off

cd ..

REM Check if PyInstaller is installed
pyinstaller --version >nul 2>&1
if not %errorlevel% equ 0 (
    echo "PyInstaller is not installed. Installing..."
    pip install pyinstaller
)

pyinstaller main.spec