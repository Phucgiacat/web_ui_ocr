import pandas as pd
import re
import ast
import numpy as np
import os
import json
import logging
from pathlib import Path
from typing import List

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Constants
DEFAULT_OUTPUT_DIR = Path("./check_label/images_label")
LABEL_FILE = "Label.txt"
FILE_STATE = "fileState.txt"

# Hàm parse bounding box từ string hoặc list
def parse_bbox(bbox_data):
    """Parse bounding box từ nhiều format khác nhau"""
    if isinstance(bbox_data, str):
        return eval(bbox_data)
    elif isinstance(bbox_data, list):
        return bbox_data
    else:
        raise ValueError(f"Unsupported bbox format: {type(bbox_data)}")

# Hàm sắp xếp các điểm theo quy tắc top-left → top-right → bottom-right → bottom-left
def sort_box(points):
    points = np.array(points)  # Chuyển sang numpy array
    sorted_indices = np.lexsort((points[:, 0], points[:, 1]))  # Sắp xếp theo y trước, sau đó x
    top_two = points[sorted_indices[:2]]  # Lấy 2 điểm trên cùng
    bottom_two = points[sorted_indices[2:]]  # Lấy 2 điểm dưới cùng

    # Xác định top-left và top-right
    top_two = top_two[np.argsort(top_two[:, 0])]  # Sắp xếp theo x
    top_left, top_right = top_two[0], top_two[1]

    # Xác định bottom-left và bottom-right
    bottom_two = bottom_two[np.argsort(bottom_two[:, 0])]  # Sắp xếp theo x
    bottom_left, bottom_right = bottom_two[0], bottom_two[1]

    # Kết hợp theo quy tắc
    return [top_left.tolist(), top_right.tolist(), bottom_right.tolist(), bottom_left.tolist()]

def convert_data_to_label_txt(
    df: pd.DataFrame,
    folder_images_path: str,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    image_col: str = "Image_name",
    bbox_col: str = "Image Box",
    text_col: str = "Text OCR"
) -> List[str]:
    """
    Chuyển đổi DataFrame sang file Label.txt theo định dạng PaddleOCR
    
    Args:
        df: DataFrame chứa dữ liệu
        folder_images_path: Đường dẫn folder chứa ảnh
        output_dir: Thư mục output
        image_col: Tên cột chứa tên ảnh
        bbox_col: Tên cột chứa bounding box
        text_col: Tên cột chứa text OCR
    
    Returns:
        Danh sách tên ảnh unique
    """
    logger.info("Bắt đầu chuyển đổi dữ liệu sang Label.txt...")
    
    # Tạo thư mục output nếu chưa có
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Lấy folder name
    folder_name = Path(folder_images_path).name
    
    # Group theo tên ảnh
    grouped = df.groupby(image_col)
    results = []
    
    for image_name, group in grouped:
        logger.debug(f"Xử lý ảnh: {image_name}")
        annotations = []
        
        for _, row in group.iterrows():
            try:
                # Parse và sắp xếp bbox
                bbox = parse_bbox(row[bbox_col])
                sorted_points = sort_box(bbox)
                
                # Lấy transcription và xử lý
                transcription = str(row[text_col]).strip()
                
                annotations.append({
                    "transcription": transcription,
                    "points": sorted_points
                })
            except Exception as e:
                logger.error(f"Lỗi xử lý dòng {row.name} của ảnh {image_name}: {e}")
                continue
        
        # Tạo label string theo format PaddleOCR
        # Format: image_path\t[{json_object1}, {json_object2}, ...]
        annotations_json = json.dumps(
            [
                {
                    "transcription": ann["transcription"],
                    "points": ann["points"],
                    "difficult": False
                }
                for ann in annotations
            ],
            ensure_ascii=False
        )
        
        results.append(f"images_label/{image_name}\t{annotations_json}")
    
    # Ghi file
    output_path = output_dir / LABEL_FILE
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(results))
    
    logger.info(f"✓ Đã lưu {len(results)} ảnh vào {output_path}")
    
    # Trả về danh sách tên ảnh unique
    return df[image_col].unique().tolist()


def convert_data_to_fileStatetxt(_FolderImagesName_path, folder_list_ImageName):
    output_path = f"./check_label/images_label/fileState.txt"
    with open(f"{output_path}", "w", encoding="utf-8") as file:
        folder_name = _FolderImagesName_path.split('/')[-1]
        for _imgName in folder_list_ImageName:
            file.write(f"images_label/{_imgName}\t1\n")
            print("name",_imgName)
    print(f"Đã lưu dữ liệu vào {output_path}")



#==============================================================
# YOU CAN CHANGE HERE:
def convert_ID_To_png(string: str):
    result = string[:-3]
    result = result.replace("_",".png")
    return result
#==============================================================


def main():
    #==============================================================
    # YOU CAN CHANGE HERE:
    print(os.getcwd())  # Prints the current working directory

    # Chỉnh thành tên file Excel ngữ liệu GK
    current_dir = os.path.join(os.getcwd(), 'output')

    # Construct the full path to 'result.xlsx'
    result_file_path = os.path.join(current_dir, 'midterm.xlsx')

    # Debugging print to verify the path
    print(f"Looking for file at: {result_file_path}")

    # Chỉnh thành tên folder chứa thư mục ảnh của bạn
    folder_images_path = os.path.join(os.getcwd(), 'Label', 'images_label')

    # Chỉnh thành Tên cột của cột chứa "Tên ảnh" trong file Excel của bạn
    _ImageName_Column = "Image Name"

    # Chỉnh thành Tên cột của cột chứa tọa độ "Bounding Box" trong file Excel của bạn
    _PositionBBoxName_Column = "Image Box"

    # Chỉnh thành Tên cột của cột chứa "Văn bản OCR" trong file Excel của bạn
    _OCRName_Column = "SinoNom OCR"

    ##===================================================================
    ##===================================================================

    df = pd.read_excel(result_file_path)
    df.insert(0, "Image Name", [ convert_ID_To_png(x) for x in df["ID"]])

    _img_names = convert_data_to_label_txt(df, folder_images_path, DEFAULT_OUTPUT_DIR, _ImageName_Column, _PositionBBoxName_Column, _OCRName_Column)
    convert_data_to_fileStatetxt(folder_images_path, _img_names)

if __name__ == "__main__":
    main()