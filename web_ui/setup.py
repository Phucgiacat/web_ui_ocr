#!/usr/bin/env python3
"""
Setup script để chuẩn bị môi trường cho web UI
"""

import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Kiểm tra phiên bản Python"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ được yêu cầu!")
        sys.exit(1)
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}")

def install_requirements():
    """Cài đặt các thư viện cần thiết"""
    req_file = Path(__file__).parent / 'requirements.txt'
    
    print("\n📦 Cài đặt các thư viện...")
    print("   (Đây có thể mất vài phút...)\n")
    
    result = subprocess.run(
        [sys.executable, '-m', 'pip', 'install', '-r', str(req_file), '--upgrade'],
        capture_output=False
    )
    
    if result.returncode != 0:
        print("\n⚠️  Lỗi cài đặt thư viện!")
        print("   Thử chạy manual:")
        print(f"   {sys.executable} -m pip install -r {req_file}")
        sys.exit(1)
    
    print("\n✅ Cài đặt thành công!")

def create_directories():
    """Tạo các thư mục cần thiết"""
    dirs = [
        'output',
        'temp',
        'logs',
    ]
    
    for dir_name in dirs:
        dir_path = Path(__file__).parent.parent / dir_name
        dir_path.mkdir(exist_ok=True)
        print(f"✅ Tạo thư mục: {dir_name}")

def main():
    """Main setup function"""
    print("=" * 60)
    print("🚀 Setup OCR Corrector Web UI")
    print("=" * 60)
    
    check_python_version()
    create_directories()
    install_requirements()
    
    print("\n" + "=" * 60)
    print("✅ Setup hoàn thành!")
    print("=" * 60)
    print("\n🎯 Để chạy ứng dụng:")
    print("   python web_ui/run.py  (từ thư mục gốc repo)")
    print("   hoặc: python run.py  (nếu đang đứng trong thư mục web_ui)")
    print("\n📖 Hoặc xem README.md để biết thêm chi tiết")

if __name__ == "__main__":
    main()
