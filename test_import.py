import sys
import os

# Try to import the module
try:
    from Proccess_pdf.extract_page import ExtractPages
    print("✅ Import successful")
except ImportError as e:
    print(f"❌ Import failed: {e}")
    print(f"Current directory: {os.getcwd()}")
    print(f"Python path: {sys.path}")
    import traceback
    traceback.print_exc()
