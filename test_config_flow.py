#!/usr/bin/env python3
"""
Test script để kiểm tra JSON config flow
"""
import os
import sys
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from web_ui.data_handler import DataHandler
from web_ui.ocr_processor import OCRProcessor

def print_json(data, title=""):
    """In JSON một cách đẹp"""
    if title:
        print(f"\n{'='*60}")
        print(f"📋 {title}")
        print('='*60)
    print(json.dumps(data, indent=2, ensure_ascii=False))

def test_config_flow():
    """Test config flow"""
    output_folder = "temp_test"
    config_file = "temp_test/before_handle_data.json"
    
    print("\n🧪 Test JSON Config Flow\n")
    
    # Create initial config
    print("1️⃣  Creating initial config...")
    os.makedirs(output_folder, exist_ok=True)
    
    initial_config = {
        "file_name": "test_document",
        "vi_dir": f"{output_folder}/vi_images",
        "nom_dir": f"{output_folder}/nom_images",
        "vi_dir_processed": "",
        "nom_dir_processed": "",
        "ocr_json_nom": "",
        "ocr_image_nom": "",
        "ocr_id": 1,
        "lang_type": 2,
        "epitaph": 1,
        "output_txt": "",
        "result_xlsx": ""
    }
    
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(initial_config, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Config file created: {config_file}")
    print_json(initial_config, "Initial Config")
    
    # Test DataHandler
    print("\n2️⃣  Testing DataHandler...")
    handler = DataHandler(output_folder, config_file)
    
    # Read config
    config = handler.read_file_info()
    print_json(config, "Config After Reading")
    
    # Simulate crop phase
    print("\n3️⃣  Simulating crop_images() phase...")
    config['vi_dir_processed'] = config['vi_dir']
    config['nom_dir_processed'] = config['nom_dir']
    handler.write_file_info(config)
    
    config = handler.read_file_info()
    print_json(config, "Config After crop_images()")
    
    # Simulate OCR phase
    print("\n4️⃣  Simulating ocr_han_nom() phase...")
    config['ocr_json_nom'] = f"{output_folder}/ocr/Han_Nom_ocr"
    config['ocr_image_nom'] = f"{output_folder}/ocr/image_bbox"
    handler.write_file_info(config)
    
    config = handler.read_file_info()
    print_json(config, "Config After ocr_han_nom()")
    
    # Simulate Align phase
    print("\n5️⃣  Simulating align_text() phase...")
    config['output_txt'] = f"{output_folder}/result.txt"
    handler.write_file_info(config)
    
    config = handler.read_file_info()
    print_json(config, "Config After align_text()")
    
    # Test OCRProcessor
    print("\n6️⃣  Testing OCRProcessor...")
    processor = OCRProcessor(output_folder, config_file, ocr_id=1, lang_type=2, epitaph=1)
    
    # Simulate correct_text phase
    print("\n7️⃣  Simulating correct_text() phase...")
    config = processor.read_file_info()
    config['result_xlsx'] = f"{output_folder}/result.xlsx"
    processor.write_file_info(config)
    
    config = processor.read_file_info()
    print_json(config, "Final Config After correct_text()")
    
    # Verify all fields
    print("\n✅ All fields in config:")
    for key, value in config.items():
        status = "✓" if value else "○"
        print(f"  {status} {key:25} = {value}")
    
    # Cleanup
    import shutil
    shutil.rmtree(output_folder, ignore_errors=True)
    print(f"\n🧹 Cleaned up {output_folder}")
    
    print("\n" + "="*60)
    print("✅ Test completed successfully!")
    print("="*60)

if __name__ == "__main__":
    try:
        test_config_flow()
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
