#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug tool để kiểm tra file matching trong mapping

Giúp diagnose vấn đề tại sao files trong mapping bị skip
"""
import os
import sys
import ast
import pandas as pd
from pathlib import Path
from typing import Dict, List, Tuple

# Fix encoding for Windows console
if sys.platform == 'win32':
    import io
    import locale
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


def find_file_flexible(dir_path: str, target_filename: str) -> Tuple[bool, str]:
    """
    Tìm file flexible - support case insensitive và mismatch extension
    
    Args:
        dir_path: Thư mục cần tìm
        target_filename: Tên file cần tìm
    
    Returns:
        (found: bool, full_path_or_reason: str)
    """
    if not os.path.isdir(dir_path):
        return False, f"Directory not found: {dir_path}"
    
    # Thử kiểm tra trực tiếp trước
    full_path = os.path.join(dir_path, target_filename)
    if os.path.exists(full_path):
        return True, full_path
    
    # Lấy base name (không có extension)
    target_base = os.path.splitext(target_filename)[0]
    target_ext = os.path.splitext(target_filename)[1].lower()
    
    # Tìm file với base name giống nhau (ignore case, ignore extension)
    for item in os.listdir(dir_path):
        item_path = os.path.join(dir_path, item)
        if not os.path.isfile(item_path):
            continue
        
        item_base = os.path.splitext(item)[0]
        item_ext = os.path.splitext(item)[1].lower()
        
        # Match nếu base name giống (không case sensitive)
        if item_base.lower() == target_base.lower():
            if item_ext in ['.json', '.txt', '.jpg', '.png']:
                return True, item_path
    
    # Không tìm thấy, hiển thị available files
    available = []
    for item in os.listdir(dir_path):
        item_path = os.path.join(dir_path, item)
        if os.path.isfile(item_path):
            item_base = os.path.splitext(item)[0]
            if target_base.lower() == item_base.lower():
                available.append(item)
    
    if available:
        reason = f"Not found exactly, but similar files exist: {available}"
    else:
        reason = f"Not found - base name '{target_base}' doesn't exist"
    
    return False, reason


def debug_mapping(
    mapping_excel: str,
    nom_dir: str,
    vi_dir: str,
    output_report: str = "debug_mapping_report.txt"
) -> None:
    """
    Debug mapping file để tìm ra file nào bị skip
    
    Args:
        mapping_excel: Path to mapping Excel file
        nom_dir: Path to Hán Nôm directory
        vi_dir: Path to Vietnamese directory
        output_report: Path to output report file
    """
    print(f"\n{'='*80}")
    print("DEBUG MAPPING FILE")
    print(f"{'='*80}\n")
    
    # Validate inputs
    if not os.path.exists(mapping_excel):
        print(f"❌ Error: Mapping file not found: {mapping_excel}")
        return
    
    if not os.path.isdir(nom_dir):
        print(f"❌ Error: Hán Nôm directory not found: {nom_dir}")
        return
    
    if not os.path.isdir(vi_dir):
        print(f"❌ Error: Vietnamese directory not found: {vi_dir}")
        return
    
    # Read mapping
    try:
        df = pd.read_excel(mapping_excel)
    except Exception as e:
        print(f"❌ Error reading mapping file: {e}")
        return
    
    print(f"✓ Loaded mapping file with {len(df)} rows\n")
    
    # Process each mapping row
    report_lines = [
        "DEBUG MAPPING REPORT",
        f"Mapping file: {mapping_excel}",
        f"Hán Nôm dir: {nom_dir}",
        f"Vietnamese dir: {vi_dir}",
        "\n" + "="*80 + "\n"
    ]
    
    total_rows = len(df)
    valid_rows = 0
    skip_rows = 0
    
    for idx, row in df.iterrows():
        row_num = idx + 2  # Excel row number (1-indexed, +1 for header)
        
        try:
            hannom_str = str(row.get("hannom", "[]"))
            quocngu_str = str(row.get("quocngu", "[]"))
            
            files_han = ast.literal_eval(hannom_str)
            files_qn = ast.literal_eval(quocngu_str)
        except Exception as e:
            report_lines.append(f"❌ Row {row_num}: Error parsing mapping - {e}")
            skip_rows += 1
            continue
        
        print(f"\n📋 Row {row_num}:")
        print(f"   Hán Nôm files: {files_han}")
        print(f"   Vietnamese files: {files_qn}")
        
        # Check each file
        all_han_found = True
        all_qn_found = True
        details = []
        
        for f_han in files_han:
            found, info = find_file_flexible(nom_dir, f_han)
            status = "✓" if found else "❌"
            print(f"   {status} Hán: {f_han}")
            if not found:
                all_han_found = False
                print(f"      → {info}")
                details.append(f"Hán '{f_han}': {info}")
            else:
                details.append(f"Hán '{f_han}': Found")
        
        for f_qn in files_qn:
            found, info = find_file_flexible(vi_dir, f_qn)
            status = "✓" if found else "❌"
            print(f"   {status} QN: {f_qn}")
            if not found:
                all_qn_found = False
                print(f"      → {info}")
                details.append(f"QN '{f_qn}': {info}")
            else:
                details.append(f"QN '{f_qn}': Found")
        
        if all_han_found and all_qn_found:
            print(f"   ✅ ROW VALID - Will be processed")
            valid_rows += 1
            status_str = "✅ VALID"
        else:
            print(f"   ⚠️ ROW SKIPPED - Some files missing")
            skip_rows += 1
            status_str = "❌ SKIPPED"
        
        report_lines.append(f"\n--- Row {row_num}: {status_str} ---")
        report_lines.append(f"Hán files: {files_han}")
        report_lines.append(f"QN files: {files_qn}")
        for detail in details:
            report_lines.append(f"  • {detail}")
    
    # Summary
    print(f"\n{'='*80}")
    print("SUMMARY")
    print(f"{'='*80}")
    print(f"Total rows: {total_rows}")
    print(f"Valid rows (will be processed): {valid_rows} ✅")
    print(f"Skipped rows (missing files): {skip_rows} ❌")
    print(f"Success rate: {(valid_rows/total_rows*100):.1f}%\n")
    
    # Add summary to report
    report_lines.extend([
        "\n" + "="*80,
        "SUMMARY",
        "="*80,
        f"Total rows: {total_rows}",
        f"Valid rows: {valid_rows} ✅",
        f"Skipped rows: {skip_rows} ❌",
        f"Success rate: {(valid_rows/total_rows*100):.1f}%",
    ])
    
    # Write report
    try:
        with open(output_report, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report_lines))
        print(f"✓ Report saved to: {output_report}")
    except Exception as e:
        print(f"❌ Error writing report: {e}")


def list_directory_contents(dir_path: str, pattern: str = None) -> None:
    """List directory contents for inspection"""
    print(f"\n📁 Directory: {dir_path}")
    
    if not os.path.isdir(dir_path):
        print(f"❌ Not a directory")
        return
    
    files = []
    for item in os.listdir(dir_path):
        item_path = os.path.join(dir_path, item)
        if os.path.isfile(item_path):
            size = os.path.getsize(item_path)
            files.append((item, size))
    
    if not files:
        print("(empty)")
        return
    
    print(f"Files ({len(files)}):")
    for name, size in sorted(files):
        if pattern is None or pattern.lower() in name.lower():
            print(f"  • {name} ({size} bytes)")


if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) < 4:
        print("Usage: python debug_mapping.py <mapping_excel> <nom_dir> <vi_dir> [output_report]")
        sys.exit(1)
    
    mapping_file = sys.argv[1]
    nom_directory = sys.argv[2]
    vi_directory = sys.argv[3]
    output_file = sys.argv[4] if len(sys.argv) > 4 else "debug_mapping_report.txt"
    
    debug_mapping(mapping_file, nom_directory, vi_directory, output_file)
    
    # Also list directories
    print("\nDirectory Contents:")
    list_directory_contents(nom_directory)
    list_directory_contents(vi_directory)
