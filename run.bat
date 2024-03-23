@echo off

REM Check if Pygame is installed
python -c "import pygame" >nul 2>&1
if not %errorlevel% equ 0 (
    pip install -r requirements.txt
) else (
    REM Check if Colorama is installed
    python -c "import colorama" >nul 2>&1
    if not %errorlevel% equ 0 (
        pip install -r requirements.txt
    )
)

python src/main.py
