#!/usr/bin/env python3
"""
Example: Align paths flow
Minh họa cách sử dụng set_align_paths() và align_text()
"""
import os
import sys
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from web_ui.ocr_processor import OCRProcessor

def print_config(config, title=""):
    """In config một cách đẹp"""
    if title:
        print(f"\n{'='*60}")
        print(f"📋 {title}")
        print('='*60)
    for key in ['ocr_txt_qn', 'ocr_json_nom', 'ocr_image_nom', 'output_txt']:
        value = config.get(key, '(empty)')
        status = "✓" if value and value != '(empty)' else "○"
        print(f"  {status} {key:20} = {value}")

def example_1_from_ocr():
    """Example 1: Align paths tự động từ OCR"""
    print("\n" + "="*60)
    print("📚 Example 1: Align Paths từ OCR (tự động)")
    print("="*60)
    
    output_folder = "temp_example1"
    config_file = "temp_example1/config.json"
    
    # Setup
    os.makedirs(output_folder, exist_ok=True)
    
    # Create initial config
    initial_config = {
        "file_name": "document_1",
        "ocr_txt_qn": "",
        "ocr_json_nom": "",
    }
    
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(initial_config, f, indent=2, ensure_ascii=False)
    
    processor = OCRProcessor(output_folder, config_file)
    
    print("\n1️⃣  Initial config:")
    print_config(initial_config)
    
    print("\n2️⃣  Simulating OCR (auto-set paths)...")
    # Giả sử OCR đã set các paths
    config = processor.read_file_info()
    config['ocr_txt_qn'] = f"{output_folder}/ocr/Quoc_Ngu_ocr"
    config['ocr_json_nom'] = f"{output_folder}/ocr/Han_Nom_ocr"
    processor.write_file_info(config)
    
    config = processor.read_file_info()
    print_config(config, "Config sau OCR")
    
    print("\n3️⃣  get_align_paths():")
    paths = processor.get_align_paths()
    print(f"  ocr_txt_qn: {paths['ocr_txt_qn']}")
    print(f"  ocr_json_nom: {paths['ocr_json_nom']}")
    
    # Cleanup
    import shutil
    shutil.rmtree(output_folder, ignore_errors=True)
    print(f"\n🧹 Cleaned up {output_folder}")

def example_2_user_select():
    """Example 2: User chọn folder manually"""
    print("\n" + "="*60)
    print("📚 Example 2: User Chọn Folder (Manual)")
    print("="*60)
    
    output_folder = "temp_example2"
    config_file = "temp_example2/config.json"
    
    # Setup
    os.makedirs(output_folder, exist_ok=True)
    os.makedirs(f"{output_folder}/user_json", exist_ok=True)
    os.makedirs(f"{output_folder}/user_txt", exist_ok=True)
    
    # Create initial config
    initial_config = {
        "file_name": "document_2",
        "ocr_txt_qn": "",
        "ocr_json_nom": "",
    }
    
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(initial_config, f, indent=2, ensure_ascii=False)
    
    processor = OCRProcessor(output_folder, config_file)
    
    print("\n1️⃣  Initial config:")
    print_config(initial_config)
    
    print("\n2️⃣  User chọn folder...")
    print(f"  ✓ Chọn JSON: {output_folder}/user_json")
    print(f"  ✓ Chọn TXT: {output_folder}/user_txt")
    
    print("\n3️⃣  Gọi set_align_paths()...")
    result = processor.set_align_paths(
        ocr_json_nom=f"{output_folder}/user_json",
        ocr_txt_qn=f"{output_folder}/user_txt"
    )
    print(f"  Status: {result['status']}")
    
    config = processor.read_file_info()
    print_config(config, "Config sau set_align_paths()")
    
    print("\n4️⃣  get_align_paths():")
    paths = processor.get_align_paths()
    print(f"  ocr_txt_qn: {paths['ocr_txt_qn']}")
    print(f"  ocr_json_nom: {paths['ocr_json_nom']}")
    
    # Cleanup
    import shutil
    shutil.rmtree(output_folder, ignore_errors=True)
    print(f"\n🧹 Cleaned up {output_folder}")

def example_3_mixed():
    """Example 3: Kết hợp OCR + user select"""
    print("\n" + "="*60)
    print("📚 Example 3: Kết Hợp OCR + Manual Select")
    print("="*60)
    
    output_folder = "temp_example3"
    config_file = "temp_example3/config.json"
    
    # Setup
    os.makedirs(output_folder, exist_ok=True)
    os.makedirs(f"{output_folder}/ocr", exist_ok=True)
    os.makedirs(f"{output_folder}/other_txt", exist_ok=True)
    
    # Create initial config
    initial_config = {
        "file_name": "document_3",
        "ocr_txt_qn": "",
        "ocr_json_nom": "",
    }
    
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(initial_config, f, indent=2, ensure_ascii=False)
    
    processor = OCRProcessor(output_folder, config_file)
    
    print("\n1️⃣  Initial config:")
    print_config(initial_config)
    
    print("\n2️⃣  Chạy OCR Hán Nôm (auto-set JSON path)...")
    config = processor.read_file_info()
    config['ocr_json_nom'] = f"{output_folder}/ocr/Han_Nom_ocr"
    processor.write_file_info(config)
    print(f"  ✓ ocr_json_nom = {config['ocr_json_nom']}")
    
    config = processor.read_file_info()
    print_config(config, "Config sau OCR")
    
    print("\n3️⃣  User chọn TXT folder khác (không từ OCR)...")
    print(f"  ✓ Chọn TXT: {output_folder}/other_txt")
    
    print("\n4️⃣  Gọi set_align_paths() với chỉ TXT...")
    result = processor.set_align_paths(ocr_txt_qn=f"{output_folder}/other_txt")
    print(f"  Status: {result['status']}")
    
    config = processor.read_file_info()
    print_config(config, "Config sau set_align_paths()")
    
    print("\n5️⃣  Giờ align_text() có cả JSON và TXT:")
    paths = processor.get_align_paths()
    print(f"  ✓ ocr_json_nom: {paths['ocr_json_nom']}")
    print(f"  ✓ ocr_txt_qn: {paths['ocr_txt_qn']}")
    print(f"  → Sẵn sàng align!")
    
    # Cleanup
    import shutil
    shutil.rmtree(output_folder, ignore_errors=True)
    print(f"\n🧹 Cleaned up {output_folder}")

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🎯 Align Paths Examples - set_align_paths() & align_text()")
    print("="*60)
    
    try:
        example_1_from_ocr()
        example_2_user_select()
        example_3_mixed()
        
        print("\n" + "="*60)
        print("✅ All examples completed!")
        print("="*60)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
