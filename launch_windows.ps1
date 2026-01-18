# OCR Corrector Web UI - Quick Launch Script for Windows

# Colors for output
$Colors = @{
    Green = 'Green'
    Yellow = 'Yellow'
    Red = 'Red'
    Cyan = 'Cyan'
}

function Print-Header {
    Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor $Colors.Cyan
    Write-Host "║   OCR Corrector Web UI - Windows Launcher               ║" -ForegroundColor $Colors.Cyan
    Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor $Colors.Cyan
    Write-Host ""
}

function Print-Menu {
    Write-Host "What would you like to do?" -ForegroundColor $Colors.Cyan
    Write-Host ""
    Write-Host "1. Setup (First time - Install dependencies)" -ForegroundColor $Colors.Yellow
    Write-Host "2. Check Environment (Verify setup)" -ForegroundColor $Colors.Yellow
    Write-Host "3. Run Application (Start the web UI)" -ForegroundColor $Colors.Yellow
    Write-Host "4. Open Browser (Go to http://localhost:8501)" -ForegroundColor $Colors.Yellow
    Write-Host "5. Virtual Environment > Activate" -ForegroundColor $Colors.Yellow
    Write-Host "6. View Documentation" -ForegroundColor $Colors.Yellow
    Write-Host "7. Clean (Remove output files)" -ForegroundColor $Colors.Yellow
    Write-Host "8. Exit" -ForegroundColor $Colors.Yellow
    Write-Host ""
}

function Setup {
    Write-Host "Starting setup..." -ForegroundColor $Colors.Green
    Write-Host ""
    
    $venvPath = "web_ui\venv"
    
    # Check Python
    Write-Host "Checking Python..." -ForegroundColor $Colors.Yellow
    $pythonVer = python --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Python not found!" -ForegroundColor $Colors.Red
        Write-Host "Please install Python 3.8+ from https://www.python.org/downloads/" -ForegroundColor $Colors.Red
        return
    }
    Write-Host "✓ Found: $pythonVer" -ForegroundColor $Colors.Green
    Write-Host ""
    
    # Create venv
    if (Test-Path $venvPath) {
        Write-Host "✓ Virtual environment already exists" -ForegroundColor $Colors.Green
    } else {
        Write-Host "Creating virtual environment..." -ForegroundColor $Colors.Yellow
        python -m venv $venvPath
        Write-Host "✓ Virtual environment created" -ForegroundColor $Colors.Green
    }
    Write-Host ""
    
    # Activate venv
    Write-Host "Activating virtual environment..." -ForegroundColor $Colors.Yellow
    & "$venvPath\Scripts\Activate.ps1"
    Write-Host "✓ Virtual environment activated" -ForegroundColor $Colors.Green
    Write-Host ""
    
    # Install requirements
    Write-Host "Installing packages (this may take a few minutes)..." -ForegroundColor $Colors.Yellow
    pip install --upgrade pip
    pip install -r web_ui\requirements.txt
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ All packages installed successfully" -ForegroundColor $Colors.Green
    } else {
        Write-Host "ERROR: Failed to install packages" -ForegroundColor $Colors.Red
        return
    }
    Write-Host ""
    
    # Create directories
    Write-Host "Creating directories..." -ForegroundColor $Colors.Yellow
    New-Item -ItemType Directory -Force -Path "output" > $null
    New-Item -ItemType Directory -Force -Path "temp" > $null
    New-Item -ItemType Directory -Force -Path "logs" > $null
    Write-Host "✓ Directories created" -ForegroundColor $Colors.Green
    Write-Host ""
    
    Write-Host "✓ Setup completed successfully!" -ForegroundColor $Colors.Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor $Colors.Cyan
    Write-Host "  1. Run option 3 to start the application" -ForegroundColor $Colors.Yellow
    Write-Host "  2. Open http://localhost:8501 in your browser" -ForegroundColor $Colors.Yellow
    Write-Host ""
}

function CheckEnvironment {
    Write-Host "Checking environment..." -ForegroundColor $Colors.Green
    Write-Host ""
    
    Push-Location web_ui
    python check_env.py
    Pop-Location
    
    Write-Host ""
}

function RunApplication {
    Write-Host "Starting OCR Corrector Web UI..." -ForegroundColor $Colors.Green
    Write-Host ""
    
    $venvPath = "web_ui\venv"
    
    if (-not (Test-Path $venvPath)) {
        Write-Host "Virtual environment not found!" -ForegroundColor $Colors.Red
        Write-Host "Please run Setup (option 1) first" -ForegroundColor $Colors.Yellow
        return
    }
    
    & "$venvPath\Scripts\Activate.ps1"
    
    Write-Host "Starting application..." -ForegroundColor $Colors.Green
    Write-Host "Opening http://localhost:8501 in your browser..." -ForegroundColor $Colors.Green
    Write-Host ""
    Write-Host "Press Ctrl+C to stop the application" -ForegroundColor $Colors.Yellow
    Write-Host ""
    
    Start-Sleep -Seconds 2
    Start-Process "http://localhost:8501"
    
    Push-Location web_ui
    python run.py
    Pop-Location
}

function OpenBrowser {
    Write-Host "Opening http://localhost:8501..." -ForegroundColor $Colors.Green
    Start-Process "http://localhost:8501"
}

function ActivateVenv {
    $venvPath = "web_ui\venv"
    
    if (-not (Test-Path $venvPath)) {
        Write-Host "Virtual environment not found!" -ForegroundColor $Colors.Red
        Write-Host "Please run Setup (option 1) first" -ForegroundColor $Colors.Yellow
        return
    }
    
    Write-Host "Activating virtual environment..." -ForegroundColor $Colors.Green
    & "$venvPath\Scripts\Activate.ps1"
    Write-Host "✓ Virtual environment activated" -ForegroundColor $Colors.Green
    Write-Host "You can now run: streamlit run web_ui/app.py" -ForegroundColor $Colors.Cyan
}

function ViewDocumentation {
    Write-Host "Documentation files:" -ForegroundColor $Colors.Green
    Write-Host ""
    Write-Host "1. README.md - Quick start (open in default app)" -ForegroundColor $Colors.Yellow
    Write-Host "2. GUIDE.md - Detailed guide (open in default app)" -ForegroundColor $Colors.Yellow
    Write-Host "3. SUMMARY.md - Project summary (open in default app)" -ForegroundColor $Colors.Yellow
    Write-Host "4. Quick reference in terminal" -ForegroundColor $Colors.Yellow
    Write-Host ""
    
    $docChoice = Read-Host "Which one to open? (1-4 or press Enter to skip)"
    
    switch ($docChoice) {
        "1" {
            if (Test-Path "web_ui\README.md") {
                Invoke-Item "web_ui\README.md"
            }
        }
        "2" {
            if (Test-Path "web_ui\GUIDE.md") {
                Invoke-Item "web_ui\GUIDE.md"
            }
        }
        "3" {
            if (Test-Path "web_ui\SUMMARY.md") {
                Invoke-Item "web_ui\SUMMARY.md"
            }
        }
        "4" {
            & ".\web_ui\venv\Scripts\python.exe" web_ui\quick_reference.py
        }
    }
}

function CleanOutput {
    Write-Host "Cleaning output files..." -ForegroundColor $Colors.Yellow
    
    if (Test-Path "output") {
        Remove-Item -Path "output\*" -Recurse -Force -ErrorAction SilentlyContinue
        Write-Host "✓ Cleaned output folder" -ForegroundColor $Colors.Green
    }
    
    if (Test-Path "before_handle_data.json") {
        Remove-Item -Path "before_handle_data.json" -Force -ErrorAction SilentlyContinue
        Write-Host "✓ Removed before_handle_data.json" -ForegroundColor $Colors.Green
    }
    
    Write-Host "✓ Cleanup completed" -ForegroundColor $Colors.Green
    Write-Host ""
}

function Main {
    Print-Header
    
    while ($true) {
        Print-Menu
        $choice = Read-Host "Enter your choice (1-8)"
        Write-Host ""
        
        switch ($choice) {
            "1" { Setup }
            "2" { CheckEnvironment }
            "3" { RunApplication }
            "4" { OpenBrowser }
            "5" { ActivateVenv }
            "6" { ViewDocumentation }
            "7" { CleanOutput }
            "8" {
                Write-Host "Goodbye!" -ForegroundColor $Colors.Green
                exit
            }
            default {
                Write-Host "Invalid choice. Please try again." -ForegroundColor $Colors.Red
            }
        }
        
        Write-Host ""
        Read-Host "Press Enter to continue"
        Clear-Host
        Print-Header
    }
}

# Run main
Main
