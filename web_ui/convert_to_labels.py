"""
Convert to PaddleOCR Labels Module
Chuyển đổi dữ liệu từ Excel sang định dạng Label cho PaddleOCR
"""

import pandas as pd
import numpy as np
import os
import json
from pathlib import Path
from PIL import Image
from typing import List, Dict, Tuple, Any
from io import BytesIO


def sort_box(points):
    """
    Sắp xếp các điểm theo quy tắc: top-left → top-right → bottom-right → bottom-left
    
    Args:
        points: List of [x, y] coordinates
    
    Returns:
        Sorted points in PaddleOCR format
    """
    points = np.array(points)
    sorted_indices = np.lexsort((points[:, 0], points[:, 1]))
    top_two = points[sorted_indices[:2]]
    bottom_two = points[sorted_indices[2:]]

    top_two = top_two[np.argsort(top_two[:, 0])]
    top_left, top_right = top_two[0], top_two[1]

    bottom_two = bottom_two[np.argsort(bottom_two[:, 0])]
    bottom_left, bottom_right = bottom_two[0], bottom_two[1]

    return [top_left.tolist(), top_right.tolist(), bottom_right.tolist(), bottom_left.tolist()]


def get_image_dimensions(image_path: str) -> Tuple[int, int]:
    """
    Lấy kích thước ảnh (width, height)
    
    Args:
        image_path: Đường dẫn ảnh
    
    Returns:
        (width, height) hoặc None nếu lỗi
    """
    try:
        with Image.open(image_path) as img:
            return img.size  # (width, height)
    except Exception as e:
        print(f"❌ Lỗi đọc ảnh {image_path}: {e}")
        return None


def validate_image_sizes(
    extracted_image_dir: str,
    json_dir: str,
    image_names: List[str]
) -> Dict[str, bool]:
    """
    Kiểm tra file JPG và JSON
    
    Args:
        extracted_image_dir: Thư mục extracted/image (chứa .jpg)
        json_dir: Thư mục JSON (chứa .json, ví dụ: ocr/Han_Nom_ocr)
        image_names: Danh sách tên file (format: <tên>_<số>)
    
    Returns:
        Dict {image_name: {valid, reason}}
    """
    validation_results = {}
    
    for img_name in image_names:
        # Convert image_name format: remove _<number> suffix
        # Example: "08729-21_0" -> "08729-21"
        if '_' in img_name:
            parts = img_name.rsplit('_', 1)
            if len(parts) == 2 and parts[1].isdigit():
                base_name = parts[0]
            else:
                base_name = img_name
        else:
            base_name = img_name.replace('.jpg', '').replace('.json', '')
        
        # Tìm file JPG trong extracted_image_dir
        jpg_path = os.path.join(extracted_image_dir, f"{base_name}.jpg")
        
        # Tìm file JSON trong json_dir
        json_path = os.path.join(json_dir, f"{base_name}.json")
        
        jpg_exists = os.path.exists(jpg_path)
        json_exists = os.path.exists(json_path)
        
        if jpg_exists and json_exists:
            validation_results[img_name] = {
                'valid': True,
                'jpg_path': jpg_path,
                'json_path': json_path,
                'reason': 'OK'
            }
        else:
            reasons = []
            if not jpg_exists:
                reasons.append(f'{base_name}.jpg không tìm thấy trong extracted/image')
            if not json_exists:
                reasons.append(f'{base_name}.json không tìm thấy trong JSON folder')
            
            validation_results[img_name] = {
                'valid': False,
                'jpg_path': jpg_path if jpg_exists else None,
                'json_path': json_path if json_exists else None,
                'reason': '; '.join(reasons)
            }
    
    return validation_results


def convert_data_to_labeltxt(
    df: pd.DataFrame,
    extracted_image_dir: str,
    output_dir: str,
    image_name_col: str = "Image Name",
    bbox_col: str = "Image Box",
    ocr_col: str = "Text OCR",
    file_name_prefix: str = "extracted"
) -> Tuple[List[str], List[Dict]]:
    """
    Chuyển đổi dữ liệu Excel sang định dạng Label
    
    Args:
        df: DataFrame từ Excel
        extracted_image_dir: Thư mục extracted/image
        output_dir: Thư mục output
        image_name_col: Tên cột ảnh
        bbox_col: Tên cột bbox
        ocr_col: Tên cột OCR
        file_name_prefix: Prefix cho output file
    
    Returns:
        (list_image_names, validation_results)
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # Xử lý tên ảnh trước khi group
    def process_image_name(name):
        """Convert image name: remove _number suffix and ensure .jpg extension"""
        # Process image_name: if format is "filename_number", convert to "filename.jpg"
        if '_' in name:
            parts = name.rsplit('_', 1)
            if len(parts) == 2 and parts[1].isdigit():
                base_name = parts[0]
            else:
                base_name = name
        else:
            base_name = name
        
        # Add .jpg extension if not present
        if not base_name.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
            return f"{base_name}.jpg"
        return base_name
    
    # Tạo cột tên ảnh đã xử lý
    df['processed_image_name'] = df[image_name_col].apply(process_image_name)
    
    # Nhóm dữ liệu theo tên ảnh ĐÃ XỬ LÝ
    grouped = df.groupby('processed_image_name')
    
    result = []
    image_names = []
    validation_results = []
    
    for output_image_name, group in grouped:
        
        image_names.append(output_image_name)
        page_result = []
        errors = []
        
        for _, row in group.iterrows():
            try:
                # Parse bbox từ string
                if isinstance(row[bbox_col], str):
                    points = eval(row[bbox_col])
                else:
                    points = row[bbox_col]
                
                # Sort bbox
                sorted_points = sort_box(points)
                transcription = str(row[ocr_col]).strip()
                
                page_result.append({
                    "transcription": transcription,
                    "points": sorted_points
                })
            except Exception as e:
                errors.append(f"❌ Lỗi parse bbox cho {image_name}: {e}")
        
        if errors:
            for err in errors:
                print(err)
                validation_results.append({
                    'image_name': output_image_name,
                    'valid': False,
                    'reason': err
                })
        
        # Tạo JSON string
        if page_result:
            annotations_json = json.dumps(
                [
                    {
                        "transcription": item["transcription"],
                        "points": item["points"],
                        "difficult": False
                    }
                    for item in page_result
                ],
                ensure_ascii=False
            )
            result.append(f"{file_name_prefix}/{output_image_name}\t{annotations_json}")
            
            validation_results.append({
                'image_name': output_image_name,
                'valid': True,
                'items': len(page_result)
            })
    
    # Ghi file Label.txt
    label_output = os.path.join(output_dir, "Label.txt")
    with open(label_output, "w", encoding="utf-8") as f:
        f.write("\n".join(result))
    
    print(f"✅ Đã lưu {len(result)} items vào {label_output}")
    
    return image_names, validation_results


def create_filestate_txt(
    output_dir: str,
    image_names: List[str],
    file_name_prefix: str = "extracted"
) -> str:
    """
    Tạo file fileState.txt cho PaddleOCR
    
    Args:
        output_dir: Thư mục output
        image_names: Danh sách tên ảnh
        file_name_prefix: Prefix cho file names
    
    Returns:
        Đường dẫn file đã tạo
    """
    filestate_output = os.path.join(output_dir, "fileState.txt")
    
    with open(filestate_output, "w", encoding="utf-8") as f:
        for img_name in image_names:
            f.write(f"{file_name_prefix}/{img_name}\t1\n")
    
    print(f"✅ Đã tạo {len(image_names)} entries vào {filestate_output}")
    
    return filestate_output


def read_excel_columns(excel_file_path: str) -> List[str]:
    """
    Đọc danh sách cột từ file Excel
    
    Args:
        excel_file_path: Đường dẫn file Excel hoặc file-like (BytesIO)
    
    Returns:
        List các tên cột
    """
    try:
        df = read_excel_any(excel_file_path, nrows=0)  # Chỉ đọc header
        return df.columns.tolist()
    except Exception as e:
        print(f"❌ Lỗi đọc Excel: {e}")
        return []


def _choose_engine(excel_source: Any) -> str | None:
    """Chọn engine theo phần mở rộng nếu có"""
    name = None
    if isinstance(excel_source, (str, os.PathLike)):
        name = str(excel_source)
    else:
        name = getattr(excel_source, 'name', None)
    if not name:
        return None
    lower = name.lower()
    if lower.endswith('.xlsx'):
        return 'openpyxl'
    if lower.endswith('.xls'):
        return 'xlrd'
    return None


def read_excel_any(excel_source: Any, **kwargs) -> pd.DataFrame:
    """
    Đọc Excel với engine phù hợp (.xlsx → openpyxl, .xls → xlrd), hỗ trợ file-like.
    Gợi ý cài đặt nếu thiếu dependency.
    """
    engine = _choose_engine(excel_source)
    try:
        return pd.read_excel(excel_source, engine=engine, **kwargs)
    except ImportError as e:
        msg = str(e)
        if 'openpyxl' in msg:
            raise ImportError("Thiếu 'openpyxl'. Cài đặt: pip install openpyxl>=3.1.0") from e
        if 'xlrd' in msg:
            raise ImportError("Thiếu 'xlrd'. Cài đặt: pip install xlrd>=2.0.1") from e
        raise
    except ValueError:
        # Có thể engine=None; thử lần lượt openpyxl rồi xlrd
        for eng in ('openpyxl', 'xlrd'):
            try:
                return pd.read_excel(excel_source, engine=eng, **kwargs)
            except ImportError as e:
                continue
            except Exception:
                continue
        raise
