@echo off
setlocal

REM Run from repo root
cd /d "%~dp0"

set "VENV_DIR=.venv"
set "VENV_PY=%VENV_DIR%\Scripts\python.exe"
set "DEPS_MARKER=%VENV_DIR%\.deps_installed"

REM Require .env (do not use .env.example)
if not exist ".env" (
  echo ERROR: .env not found. Please create .env manually before running.
  exit /b 1
)

REM Create virtual environment if missing
if not exist "%VENV_PY%" (
  echo [1/4] Creating virtual environment in %VENV_DIR% ...
  py -3 -m venv "%VENV_DIR%" 2>nul
  if errorlevel 1 (
    python -m venv "%VENV_DIR%"
  )
  if errorlevel 1 (
    echo Failed to create virtual environment. Aborting.
    exit /b 1
  )
)

REM Install dependencies only once (or remove marker to force reinstall)
if not exist "%DEPS_MARKER%" (
  echo [2/4] Installing dependencies (first run only) ...
  "%VENV_PY%" -m pip install --upgrade pip
  if errorlevel 1 (
    echo Failed to upgrade pip. Aborting.
    exit /b 1
  )

  if exist "requirements.txt" (
    "%VENV_PY%" -m pip install -r requirements.txt
    if errorlevel 1 (
      echo Failed to install requirements.txt. Aborting.
      exit /b 1
    )
  )

  if exist "web_ui\requirements.txt" (
    "%VENV_PY%" -m pip install -r web_ui\requirements.txt
    if errorlevel 1 (
      echo Failed to install web_ui\requirements.txt. Aborting.
      exit /b 1
    )
  )

  > "%DEPS_MARKER%" echo installed
) else (
  echo [2/4] Dependencies already installed. Skipping.
)

REM Ensure required folders exist
echo [3/4] Preparing folders ...
if not exist "output" mkdir "output"
if not exist "temp" mkdir "temp"
if not exist "logs" mkdir "logs"
if not exist "web_ui\output" mkdir "web_ui\output"
if not exist "web_ui\temp" mkdir "web_ui\temp"
if not exist "web_ui\logs" mkdir "web_ui\logs"

REM Run web app
echo [4/4] Starting web app in virtual environment ...
"%VENV_PY%" web_ui\run.py

endlocal
