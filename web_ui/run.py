"""
OCR Corrector - Web UI
Công cụ xử lý OCR cho tài liệu Quốc Ngữ và Hán Nôm
"""

import subprocess
import sys
from pathlib import Path

def run_app():
    """Chạy ứng dụng Streamlit"""
    app_path = Path(__file__).parent / "app.py"
    
    print("=" * 60)
    print("🚀 OCR Corrector - Web UI")
    print("=" * 60)
    print("📱 Ứng dụng đang chạy trên: http://localhost:8501")
    print("💡 Nhấn Ctrl+C để dừng")
    print("=" * 60)
    
    subprocess.run([sys.executable, "-m", "streamlit", "run", str(app_path)])

if __name__ == "__main__":
    run_app()
