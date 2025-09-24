#!/bin/bash

PURPLE="\033[35m"
YELLOW="\033[33m"
RESET="\033[0m"

echo "Starting wrld.."

if ! python3 --version >/dev/null 2>&1; then
    echo "[${PURPLE}wrld${RESET}] Python3 not found. Please install Python 3."
    exit 1
fi

if [ -f "requirements.txt" ]; then
    echo -e "[${PURPLE}wrld${RESET}] Installing dependencies..."
    python3 -m pip install --upgrade -r requirements.txt
else
    echo -e "[${PURPLE}wrld${RESET}] requirements.txt not found. Skipping dependency installation.."
    :
fi

if [ ! -f ".env" ]; then
    echo -e "[${PURPLE}wrld${RESET}] .env file not found. Quitting wrld.."
    read -p "Press Enter to exit"
    exit 1
fi

if [ -f "main.py" ]; then
    clear
    echo -e "${YELLOW}999 forever${RESET}"
    python3 main.py
    read -p "Press Enter to exit"
else
    echo -e "[${PURPLE}wrld${RESET}] main.py not found. Quitting wrld.."
    read -p "Press Enter to exit"
    exit 1
fi