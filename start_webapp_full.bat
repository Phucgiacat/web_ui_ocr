@echo off
setlocal

REM Run from repo root
cd /d "%~dp0"

REM Create .env if missing
if not exist ".env" (
  if exist ".env.example" (
    copy /Y ".env.example" ".env" >nul
    echo Created .env from .env.example
  ) else (
    echo WARNING: .env.example not found. Please create .env manually.
  )
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
