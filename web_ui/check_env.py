#!/usr/bin/env python3
"""
Environment Check Script
Kiểm tra môi trường trước khi chạy ứng dụng
"""

import sys
import os
from pathlib import Path

def print_header(text):
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60 + "\n")

def check_python_version():
    """Kiểm tra phiên bản Python"""
    print_header("Python Version Check")
    version = sys.version_info
    print(f"Python {version.major}.{version.minor}.{version.micro}")
    
    if version < (3, 8):
        print("❌ Python 3.8+ is required!")
        return False
    
    print("✅ Python version OK")
    return True

def check_directories():
    """Kiểm tra các thư mục tồn tại"""
    print_header("Directory Check")
    
    required_dirs = {
        'output': './output',
        'temp': './temp',
        'logs': './logs',
        'model/vi': './model/vi',
        'model/nom': './model/nom',
    }
    
    all_ok = True
    for name, path in required_dirs.items():
        if os.path.isdir(path):
            print(f"✅ {name}: {path}")
        else:
            print(f"⚠️  {name}: {path} (will be created)")
            os.makedirs(path, exist_ok=True)
    
    return all_ok

def check_env_file():
    """Kiểm tra file .env"""
    print_header("Environment File Check")
    
    env_path = Path(__file__).parent.parent / '.env'
    
    if env_path.exists():
        print(f"✅ .env file found at {env_path}")
        with open(env_path, 'r') as f:
            content = f.read()
            print("\nConfiguration:")
            for line in content.split('\n'):
                if line and not line.startswith('#'):
                    print(f"  {line}")
        return True
    else:
        print(f"⚠️  .env file not found at {env_path}")
        print("   Please create .env file with required configuration")
        return False

def check_packages():
    """Kiểm tra các package quan trọng"""
    print_header("Package Check")
    
    packages = [
        'streamlit',
        'streamlit_option_menu',
        'flask',
        'opencv_python',
        'pandas',
        'numpy',
        'dotenv',
    ]
    
    missing = []
    for package in packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - NOT INSTALLED")
            missing.append(package)
    
    if missing:
        print(f"\n⚠️  Missing packages: {', '.join(missing)}")
        print("   Run: pip install -r requirements.txt")
        return False
    
    return True

def check_project_files():
    """Kiểm tra các file dự án quan trọng"""
    print_header("Project Files Check")
    
    required_files = {
        'app.py': 'Main application',
        'config_manager.py': 'Configuration manager',
        'data_handler.py': 'Data handler',
        'ocr_processor.py': 'OCR processor',
        'requirements.txt': 'Requirements file',
    }
    
    web_ui_dir = Path(__file__).parent
    all_ok = True
    
    for filename, description in required_files.items():
        filepath = web_ui_dir / filename
        if filepath.exists():
            print(f"✅ {filename}: {description}")
        else:
            print(f"❌ {filename}: NOT FOUND")
            all_ok = False
    
    return all_ok

def check_parent_modules():
    """Kiểm tra các module từ project gốc"""
    print_header("Parent Project Modules Check")
    
    modules = {
        'Proccess_pdf.extract_page': 'PDF extraction',
        'Proccess_pdf.edge_detection': 'Edge detection',
        'vi_ocr.vi_ocr': 'VI OCR',
        'nom_ocr.nom_ocr': 'NOM OCR',
        'align.align': 'Alignment',
    }
    
    all_ok = True
    for module, description in modules.items():
        try:
            __import__(module.split('.')[0])
            print(f"✅ {module}: {description}")
        except ImportError:
            print(f"⚠️  {module}: {description} - Could not import")
    
    return all_ok

def main():
    """Chạy tất cả kiểm tra"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " OCR Corrector Web UI - Environment Check ".center(58) + "║")
    print("╚" + "=" * 58 + "╝")
    
    checks = [
        ("Python Version", check_python_version),
        ("Directories", check_directories),
        ("Environment File", check_env_file),
        ("Packages", check_packages),
        ("Project Files", check_project_files),
        ("Parent Modules", check_parent_modules),
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ Error checking {name}: {e}")
            results.append((name, False))
    
    # Summary
    print_header("Summary")
    
    for name, result in results:
        status = "✅" if result else "⚠️"
        print(f"{status} {name}")
    
    all_ok = all(result for _, result in results)
    
    print("\n")
    if all_ok:
        print("🎉 All checks passed! You can run the application.")
        print("\nTo start: python run.py")
        return 0
    else:
        print("⚠️  Some checks failed. Please fix the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
