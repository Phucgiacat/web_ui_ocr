#!/bin/bash

# Quick Setup Script for OCR Corrector Web UI on macOS/Linux

echo ""
echo "================================================"
echo "  OCR Corrector Web UI - Setup"
echo "================================================"
echo ""

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    echo "Please install Python 3.8+ from https://www.python.org/downloads/"
    exit 1
fi

echo "[OK] Python 3 found"
echo ""

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo "Error creating virtual environment"
    exit 1
fi

echo "[OK] Virtual environment created"
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
python -m pip install --upgrade pip

# Install requirements
echo "Installing requirements..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "Error installing requirements"
    exit 1
fi

echo "[OK] Requirements installed"
echo ""

# Create directories
echo "Creating necessary directories..."
mkdir -p output temp logs

echo "[OK] Directories created"
echo ""

echo "================================================"
echo "  Setup Complete!"
echo "================================================"
echo ""
echo "To start the application:"
echo "  1. Open Terminal in this folder"
echo "  2. Run: source venv/bin/activate"
echo "  3. Run: streamlit run app.py"
echo ""
echo "Or simply run: python run.py"
echo ""
