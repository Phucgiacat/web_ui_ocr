#!/usr/bin/env python3
"""
Test script để kiểm tra import từ Proccess_pdf
"""
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

print("=" * 60)
print("Testing Proccess_pdf imports...")
print("=" * 60)

print(f"\nPython path: {sys.path}")
print(f"Current directory: {os.getcwd()}")

# Test 1: Import ExtractPages
print("\n[1] Testing: from Proccess_pdf.extract_page import ExtractPages")
try:
    from Proccess_pdf.extract_page import ExtractPages
    print("✅ SUCCESS: ExtractPages imported")
except ImportError as e:
    print(f"❌ FAILED: {e}")
    import traceback
    traceback.print_exc()

# Test 2: Import EdgeDetection
print("\n[2] Testing: from Proccess_pdf.edge_detection import EdgeDetection")
try:
    from Proccess_pdf.edge_detection import EdgeDetection
    print("✅ SUCCESS: EdgeDetection imported")
except ImportError as e:
    print(f"❌ FAILED: {e}")
    import traceback
    traceback.print_exc()

# Test 3: Check required dependencies
print("\n[3] Checking required dependencies...")
dependencies = [
    ('google.cloud.vision', 'google-cloud-vision'),
    ('ultralytics', 'ultralytics'),
    ('cv2', 'opencv-python'),
    ('fitz', 'PyMuPDF'),
]

for module_name, package_name in dependencies:
    try:
        __import__(module_name)
        print(f"✅ {module_name} is installed")
    except ImportError:
        print(f"❌ {module_name} is NOT installed - install with: pip install {package_name}")

print("\n" + "=" * 60)
print("Test complete!")
print("=" * 60)
