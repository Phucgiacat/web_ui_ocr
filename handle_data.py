"""
Data Handler Module - Xử lý dữ liệu PDF, crop ảnh và quản lý file info

Module này hỗ trợ:
- Trích xuất trang từ PDF
- Crop và xử lý ảnh
- Quản lý thông tin file JSON
- Edge detection và image preprocessing
"""
import argparse
import json
import logging
import os
import re
import shutil
from pathlib import Path
from typing import Dict, Any, Optional, Union

import cv2
import numpy as np
from dotenv import load_dotenv
from tqdm import tqdm

from Proccess_pdf.edge_detection import EdgeDetection
from Proccess_pdf.extract_page import ExtractPages

load_dotenv('.env')

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Constants
OUTPUT_FOLDER = os.environ.get('OUTPUT_FOLDER', './output')
NAME_FILE_INFO = os.environ.get('NAME_FILE_INFO', 'before_handle_data.json')
VI_MODEL = os.environ.get('VI_MODEL', '')
NOM_MODEL = os.environ.get('NOM_MODEL', '')
NUM_CROP_HN = int(os.environ.get('NUM_CROP_HN', 1))
NUM_CROP_QN = int(os.environ.get('NUM_CROP_QN', 1))
TYPE_QN = int(os.environ.get('TYPE_QN', 0))


def crop_image_func(
    image_path: str,
    num_crop: int
) -> Dict[int, np.ndarray]:
    """
    Crop một ảnh thành nhiều phần theo chiều ngang
    
    Args:
        image_path: Đường dẫn đến ảnh
        num_crop: Số phần muốn chia (1 = không crop)
    
    Returns:
        Dictionary {index: cropped_image}
    
    Raises:
        ValueError: Nếu không đọc được ảnh
    """
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Không thể đọc ảnh: {image_path}")
    
    height, width, _ = image.shape
    
    # Nếu không cần crop, xóa ảnh gốc và trả về ảnh nguyên bản
    if num_crop <= 1:
        os.remove(image_path)
        return {1: image}
    
    crop_images = {}
    step = width // num_crop
    start = 0
    
    for i in range(1, num_crop + 1):
        end = width if i == num_crop else start + step
        crop_images[i] = image[:, start:end]
        start += step
    
    os.remove(image_path)
    return crop_images



def crop_folder(
    dir_input: str,
    info: str = "Processing: ",
    num_crop: int = 1
) -> None:
    """
    Crop tất cả các ảnh trong một thư mục
    
    Args:
        dir_input: Đường dẫn thư mục chứa ảnh
        info: Thông báo hiển thị trên progress bar
        num_crop: Số phần muốn chia mỗi ảnh
    """
    os.makedirs(dir_input, exist_ok=True)
    
    # Lấy danh sách các file ảnh
    image_extensions = ('.png', '.jpg', '.jpeg', '.bmp', '.tiff')
    images = [
        f for f in os.listdir(dir_input)
        if f.lower().endswith(image_extensions)
    ]
    
    if not images:
        logger.warning(f"Không tìm thấy ảnh nào trong {dir_input}")
        return
    
    logger.info(f"Tìm thấy {len(images)} ảnh trong {dir_input}")
    
    index = 0
    for image in tqdm(images, desc=info):
        try:
            image_path = os.path.join(dir_input, image)
            cropped_images = crop_image_func(image_path, num_crop)
            
            filename, ext = os.path.splitext(image)
            
            # Lưu các ảnh đã crop
            for key in sorted(cropped_images.keys()):
                index += 1
                output_file = os.path.join(
                    dir_input,
                    f"{filename}_{str(index).zfill(3)}{ext}"
                )
                cv2.imwrite(output_file, cropped_images[key])
        except Exception as e:
            logger.error(f"Lỗi khi xử lý {image}: {e}")
            continue



def replace_number_in_filename(
    filename: str,
    number: int,
    file_type: str = " "
) -> str:
    """
    Thay thế số trong tên file theo format chuẩn
    
    Args:
        filename: Tên file gốc
        number: Số mới
        file_type: Loại file (vi/nom)
    
    Returns:
        Tên file đã được thay thế
    
    Example:
        replace_number_in_filename("file_001.jpg", 5, "vi") -> "file_vi_05.jpg"
    """
    padding = f"{number:02d}"
    pattern = r'_(\d+)\.'
    new_filename = re.sub(pattern, f'_{file_type}_{padding}.', filename)
    return new_filename



def process_file(file_path: str) -> None:
    """
    Xử lý file PDF: trích xuất trang và crop ảnh
    
    Args:
        file_path: Đường dẫn đến file PDF
    
    Raises:
        FileNotFoundError: Nếu file không tồn tại
        Exception: Lỗi khác trong quá trình xử lý
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Không tìm thấy file: {file_path}")
    
    logger.info(f"Bắt đầu xử lý file: {file_path}")
    
    # Xóa thư mục output cũ nếu có
    if os.path.exists(OUTPUT_FOLDER):
        logger.info(f"Xóa thư mục output cũ: {OUTPUT_FOLDER}")
        shutil.rmtree(OUTPUT_FOLDER)
    
    # Lấy tên file
    file_name = Path(file_path).stem
    info: Dict[str, Any] = {"file_name": file_name}
    
    # Xóa file info cũ nếu có
    if os.path.exists(NAME_FILE_INFO):
        os.remove(NAME_FILE_INFO)
    
    # Tạo thư mục output
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    
    # Trích xuất các trang từ PDF
    logger.info("Trích xuất các trang từ PDF...")
    extractor = ExtractPages(file_path, OUTPUT_FOLDER)
    extractor.extract(logs=False, return_dict=False)
    
    # Đường dẫn thư mục Quốc Ngữ và Hán Nôm
    vi_dir = f"{OUTPUT_FOLDER}/image/Quoc Ngu"
    nom_dir = f"{OUTPUT_FOLDER}/image/Han Nom"
    info['vi_dir'] = vi_dir
    info['nom_dir'] = nom_dir
    
    # Crop ảnh
    try:
        logger.info(f"Số phần crop Quốc Ngữ: {NUM_CROP_QN}")
        logger.info(f"Số phần crop Hán Nôm: {NUM_CROP_HN}")
        
        crop_folder(vi_dir, info="Crop Quốc Ngữ: ", num_crop=NUM_CROP_QN)
        crop_folder(nom_dir, info="Crop Hán Nôm: ", num_crop=NUM_CROP_HN)
    except Exception as error:
        logger.error(f"Lỗi khi crop ảnh: {error}")
        raise
    
    # Lưu thông tin vào file JSON
    with open(NAME_FILE_INFO, "w", encoding="utf-8") as file:
        json.dump(info, file, ensure_ascii=False, indent=4)
    
    logger.info(f"✓ Xử lý thành công! Kết quả lưu tại {OUTPUT_FOLDER}")


def str2bool(v: Union[str, int, bool]) -> Union[bool, int]:
    """
    Chuyển đổi string thành boolean hoặc int
    
    Args:
        v: Giá trị cần chuyển đổi
    
    Returns:
        Boolean hoặc int tương ứng
    """
    if isinstance(v, bool):
        return v
    if isinstance(v, int):
        return v
    if isinstance(v, str):
        if v.isdigit():
            return int(v)
        return v.lower() in ('true', '1', 'yes', 'y')
    return False


def read_file_info(file_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Đọc thông tin từ file JSON
    
    Args:
        file_path: Đường dẫn file JSON (nếu None sẽ dùng NAME_FILE_INFO)
    
    Returns:
        Dictionary chứa thông tin
    """
    if file_path is None:
        file_path = NAME_FILE_INFO
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(
            f"Không tìm thấy file info: {file_path}\n"
            "Vui lòng chạy xử lý file PDF trước."
        )
    
    with open(file_path, "r", encoding="utf-8") as file:
        info = json.load(file)
    
    return info


def write_file_info(
    info: Dict[str, Any],
    file_path: Optional[str] = None
) -> None:
    """
    Ghi thông tin vào file JSON
    
    Args:
        info: Dictionary chứa thông tin
        file_path: Đường dẫn file JSON (nếu None sẽ dùng NAME_FILE_INFO)
    """
    if file_path is None:
        file_path = NAME_FILE_INFO
    
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(info, file, ensure_ascii=False, indent=4)
    
    logger.debug(f"Đã lưu thông tin vào {file_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        'Sentence alignment using sentence embeddings',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument('--input', type=str, required=False,
                        help='path_to_input_document')
    
    parser.add_argument('--file_id', type=str, required=False,
                        help='file_id')
    
    parser.add_argument("--check_num_pages", type=str, required=False,
                        help="check num pages")

    parser.add_argument("--crop", type=str2bool, nargs=2, metavar=('quocngu', 'hannom'),
                        help="Truyền 2 giá trị crop (true/false)")
    
    parser.add_argument("--align_number_reverse", type=str2bool, required=False
                        , help="Đánh số để align")

    args = parser.parse_args()

    input_file = args.input if args.input else None
    file_id = args.file_id if args.file_id else None
    crop = args.crop if args.crop else None
    align_number_reverse = args.align_number_reverse
    check_num = args.check_num_pages if args.check_num_pages else None
    if file_id and input_file:
        new_path = os.path.join(os.path.dirname(input_file), file_id + os.path.splitext(input_file)[1])
        os.rename(input_file, new_path)
        input_file = new_path
    
    if input_file:
        process_file(input_file)
        print('Results are saved to', os.path.splitext(os.path.basename(input_file))[0])

    if check_num:
        info = read_file_info()
        num_pages_vi = len(os.listdir(info['vi_dir']))
        num_pages_nom = len(os.listdir(info['nom_dir']))
        print(f"Số trang quốc ngữ: {num_pages_vi}")
        print(f"Số trang Hán Nôm: {num_pages_nom}")
    
    if crop:
        if os.path.exists("before_handle_data.json") == False:
            raise "Chưa Extract File"
        
        info = read_file_info()
        output_vi_dir = f"{os.environ['OUTPUT_FOLDER']}/image_processed/Quoc Ngu"
        output_nom_dir = f"{os.environ['OUTPUT_FOLDER']}/image_processed/Han Nom"

        edge_detection = EdgeDetection(info["vi_dir"], output_vi_dir,path_module=os.environ['VI_MODEL'])
        edge_detection.process(crop=crop[0],info="Cropping Quoc Ngu: ")

        edge_detection = EdgeDetection(info["nom_dir"], output_nom_dir,path_module=os.environ['NOM_MODEL'])
        edge_detection.process(crop=crop[1], info="Cropping Nom: ")

        info["vi_dir"] = output_vi_dir
        info["nom_dir"] = output_nom_dir

        write_file_info(info)
        print("cropped !!!")
    
    if align_number_reverse is not None:
        try:
            have_reverse = align_number_reverse
            info = read_file_info()

            list_image_vi = os.listdir(info['vi_dir'])
            list_image_nom = os.listdir(info['nom_dir'])
            
            if len(list_image_vi) == 0 or len(list_image_nom) == 0 or len(list_image_nom) > len(list_image_vi):
                raise ValueError("No images found in the specified directories.")

            list_image_vi = sorted(list_image_vi, key=lambda x: int(x.split('.')[0].split('_')[-1]))
            list_image_nom = sorted(list_image_nom, key=lambda x: int(x.split('.')[0].split('_')[-1]))

            if have_reverse:
                list_image_nom.reverse()

            for i in tqdm(range(len(list_image_nom)), desc="rename to algin: "):
                output_path_vi = os.path.join(info['vi_dir'], list_image_vi[i])
                output_path_nom = os.path.join(info['nom_dir'], list_image_nom[i])
                new_name_vi = replace_number_in_filename(output_path_vi, i+1,type = "vi")
                new_name_nom = replace_number_in_filename(output_path_nom, i+1,type = "nom")
                os.rename(output_path_vi, new_name_vi)
                os.rename(output_path_nom, new_name_nom)     

            list_image_vi = os.listdir(info['vi_dir'])
            list_image_nom = os.listdir(info['nom_dir'])
            list_image_vi = sorted(list_image_vi, key=lambda x: int(x.split('.')[0].split('_')[-1]))
            list_image_nom = sorted(list_image_nom, key=lambda x: int(x.split('.')[0].split('_')[-1]))
            # Đánh số theo chữ quốc ngữ
            # for i in tqdm(range(len(list_image_nom)), desc="Đánh lại số: "):
            #     output_path_vi = os.path.join(info['vi_dir'], list_image_vi[i]) 
            #     output_path_nom = os.path.join(info['nom_dir'], list_image_nom[i])
            #     name_image = list_image_vi[i].replace("_vi_", "_")
            #     new_name_vi = os.path.join(info['vi_dir'], name_image) #<- đổi tại đây để đánh số.
            #     new_name_nom = os.path.join(info['nom_dir'], name_image) #<- Đổi tại đây để đánh số.
            #     os.rename(output_path_nom, new_name_nom)  
            #     os.rename(output_path_vi, new_name_vi)
            for i in tqdm(range(len(list_image_nom)), desc="Đánh lại số: "):
                output_path_vi = os.path.join(info['vi_dir'], list_image_vi[i]) 
                output_path_nom = os.path.join(info['nom_dir'], list_image_nom[i])
                _, ext_nom = os.path.splitext(list_image_nom[i])
                _, ext_vi = os.path.splitext(list_image_vi[i])
                new_base_name = list_image_vi[i].replace("_vi_", "_").rsplit('.', 1)[0]  # bỏ đuôi
                new_name_vi = os.path.join(info['vi_dir'], new_base_name + ext_vi)
                new_name_nom = os.path.join(info['nom_dir'], new_base_name + ext_nom)
                os.rename(output_path_nom, new_name_nom)  
                os.rename(output_path_vi, new_name_vi)
        except Exception as e:
            raise e
    
    