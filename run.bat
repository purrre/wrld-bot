@echo off
title wrld bot
echo Starting wrld..

python --version >nul 2>&1
if errorlevel 1 (
    echo [[35mwrld[0m] Python not found. Please install Python 3.
    pause
    exit /b 1
)

if exist requirements.txt (
    echo [[35mwrld[0m] Installing dependencies...
    python -m pip install --upgrade -r requirements.txt
) else (
    echo [[35mwrld[0m] requirements.txt not found. Skipping dependency installation..
)

if not exist .env (
    echo [[35mwrld[0m] .env file not found. Quitting wrld..
    pause
    exit /b 1
)

if exist main.py (
    cls
    echo [33m999 forever[0m
    python main.py
    pause
) else (
    echo [[35mwrld[0m] main.py not found. Quitting wrld..
    pause
    exit /b 1
)