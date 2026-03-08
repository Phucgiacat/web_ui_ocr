@echo off
setlocal

REM Run from repo root
cd /d "%~dp0"

REM Require .env (do not use .env.example)
if not exist ".env" (
  echo ERROR: .env not found. Please create .env manually before running.
  exit /b 1
)

REM Setup dependencies and folders
python web_ui\setup.py
if errorlevel 1 (
  echo Setup failed. Aborting.
  exit /b 1
)

REM Run web app
python web_ui\run.py

endlocal
