@echo off
echo QuickBooks Bank Transaction Categorization Automation
echo ===================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7+ and try again
    pause
    exit /b 1
)

REM Check if requirements are installed
echo Checking dependencies...
pip show requests >nul 2>&1
if errorlevel 1 (
    echo Installing dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
)

REM Check if .env file exists
if not exist .env (
    echo WARNING: .env file not found
    echo Please create a .env file with your QuickBooks API credentials
    echo Copy env.example to .env and update with your values
    echo.
    pause
)

echo Starting QuickBooks automation...
echo.

REM Run the main script
python main.py %*

echo.
echo Automation complete!
pause 