"""
Utility functions cho OCR Corrector Web UI
"""

import os
import json
from pathlib import Path
from typing import Dict, Any

def create_default_env():
    """Tạo file .env mặc định nếu chưa tồn tại"""
    env_path = Path(__file__).parent.parent / '.env'
    
    if not env_path.exists():
        env_content = """# OCR Corrector Configuration

OUTPUT_FOLDER=./output
NAME_FILE_INFO=before_handle_data.json

# Crop settings
NUM_CROP_HN=1
NUM_CROP_QN=1

# Model paths
VI_MODEL=./model/vi
NOM_MODEL=./model/nom

# Processing settings
TYPE_QN=1
"""
        with open(env_path, 'w') as f:
            f.write(env_content)
        return True
    return False

def ensure_directories():
    """Đảm bảo các thư mục cần thiết tồn tại"""
    dirs = [
        './output',
        './temp',
        './logs',
    ]
    
    for dir_path in dirs:
        os.makedirs(dir_path, exist_ok=True)

def format_file_size(bytes_size: int) -> str:
    """Định dạng kích thước file"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.2f} TB"

def get_file_info(file_path: str) -> Dict[str, Any]:
    """Lấy thông tin file"""
    path = Path(file_path)
    
    return {
        'name': path.name,
        'size': format_file_size(path.stat().st_size),
        'created': path.stat().st_ctime,
        'modified': path.stat().st_mtime,
    }

def validate_pdf(file_path: str) -> bool:
    """Kiểm tra file PDF hợp lệ"""
    try:
        with open(file_path, 'rb') as f:
            header = f.read(4)
            return header == b'%PDF'
    except:
        return False

if __name__ == "__main__":
    create_default_env()
    ensure_directories()
    print("✅ Khởi tạo thành công!")
