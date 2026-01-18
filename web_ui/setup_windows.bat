@echo off
REM Quick Setup Script for OCR Corrector Web UI on Windows

echo.
echo ================================================
echo   OCR Corrector Web UI - Windows Setup
echo ================================================
echo.

REM Check Python version
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [OK] Python found
echo.

REM Create virtual environment
echo Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo Error creating virtual environment
    pause
    exit /b 1
)

echo [OK] Virtual environment created
echo.

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install requirements
echo Installing requirements...
pip install -r requirements.txt
if errorlevel 1 (
    echo Error installing requirements
    pause
    exit /b 1
)

echo [OK] Requirements installed
echo.

REM Create directories
echo Creating necessary directories...
if not exist output mkdir output
if not exist temp mkdir temp
if not exist logs mkdir logs

echo [OK] Directories created
echo.

echo ================================================
echo   Setup Complete!
echo ================================================
echo.
echo To start the application:
echo   1. Open Command Prompt in this folder
echo   2. Run: venv\Scripts\activate.bat
echo   3. Run: streamlit run app.py
echo.
echo Or simply run: python run.py
echo.
pause
