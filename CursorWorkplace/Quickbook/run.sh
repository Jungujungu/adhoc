#!/bin/bash

echo "QuickBooks Bank Transaction Categorization Automation"
echo "==================================================="
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed or not in PATH"
    echo "Please install Python 3.7+ and try again"
    exit 1
fi

# Check if requirements are installed
echo "Checking dependencies..."
if ! python3 -c "import requests" &> /dev/null; then
    echo "Installing dependencies..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to install dependencies"
        exit 1
    fi
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "WARNING: .env file not found"
    echo "Please create a .env file with your QuickBooks API credentials"
    echo "Copy env.example to .env and update with your values"
    echo
    read -p "Press Enter to continue anyway..."
fi

echo "Starting QuickBooks automation..."
echo

# Run the main script
python3 main.py "$@"

echo
echo "Automation complete!" 