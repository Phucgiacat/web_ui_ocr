import os
import json
import shutil
import sys
from pathlib import Path
from typing import Dict, Any, Optional
from tqdm import tqdm
import cv2
import re

# Add parent directory to path to import parent modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import từ project gốc (optional)
PARENT_MODULES_AVAILABLE = False
try:
    from Proccess_pdf.extract_page import ExtractPages
    from Proccess_pdf.edge_detection import EdgeDetection
    PARENT_MODULES_AVAILABLE = True
except ImportError as e:
    # Check if it's a missing google.cloud.vision dependency
    if "google.cloud" in str(e) or "vision" in str(e):
        print(f"⚠️ Warning: google-cloud-vision not installed. Install with: pip install google-cloud-vision")
        PARENT_MODULES_AVAILABLE = False
    elif "ultralytics" in str(e):
        print(f"⚠️ Warning: ultralytics not installed. Install with: pip install ultralytics")
        PARENT_MODULES_AVAILABLE = False
    else:
        print(f"⚠️ Warning: Could not import Proccess_pdf: {e}")
        import traceback
        traceback.print_exc()
        PARENT_MODULES_AVAILABLE = False
    ExtractPages = None
    EdgeDetection = None

class DataHandler:
    """Xử lý dữ liệu từ PDF đến ảnh"""
    
    def __init__(self, output_folder: str, name_file_info: str):
        self.output_folder = output_folder
        self.name_file_info = name_file_info
        
    def crop_image_func(self, image_path: str, num_crop: int) -> dict:
        """Cắt ảnh theo số lượng crop"""
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Cannot read image: {image_path}")

        height, width, _ = image.shape

        if num_crop <= 1:
            os.remove(image_path)
            return {1: image}

        crop_image = {}
        step = width // num_crop
        start = 0

        for i in range(1, num_crop + 1):
            end = width if i == num_crop else start + step
            crop_image[i] = image[:, start:end]
            start += step

        os.remove(image_path)
        return crop_image

    def crop_folder(self, dir_input: str, num_crop: int = 1, progress_callback=None):
        """Cắt tất cả ảnh trong folder"""
        os.makedirs(dir_input, exist_ok=True)
        images = [f for f in os.listdir(dir_input) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        index = 0
        
        for idx, image in enumerate(images):
            if progress_callback:
                progress_callback(f"Cắt ảnh: {image}", idx, len(images))
                
            image_path = os.path.join(dir_input, image)
            crop_image = self.crop_image_func(image_path, num_crop)
            filename, ext = os.path.splitext(image)
            
            for key in sorted(crop_image.keys()):
                index += 1
                output_file = os.path.join(dir_input, f"{filename}_{str(index).zfill(3)}{ext}")
                cv2.imwrite(output_file, crop_image[key])

    def replace_number_in_filename(self, filename: str, number: int, type_str: str = " ") -> str:
        """Thay thế số trong tên file"""
        padding = f"{number:02d}"
        pattern = r'_(\d+)\.'
        new_filename = re.sub(pattern, f'_{type_str}_{padding}.', filename)
        return new_filename

    def extract_pdf(self, file_path: str, progress_callback=None) -> Optional[Dict[str, Any]]:
        """Trích xuất PDF thành ảnh"""
        try:
            if not PARENT_MODULES_AVAILABLE:
                raise ImportError(
                    "Cannot extract PDF - missing dependencies:\n\n"
                    "Missing: google-cloud-vision\n"
                    "Install with:\n"
                    "  pip install google-cloud-vision\n\n"
                    "Or install all OCR dependencies:\n"
                    "  pip install -r requirements.txt\n"
                )
            
            # Xóa output folder cũ
            if os.path.exists(self.output_folder):
                shutil.rmtree(self.output_folder)
            
            # Xóa file info cũ
            if os.path.exists(self.name_file_info):
                os.remove(self.name_file_info)
            
            file_name = os.path.basename(file_path)
            file_name = os.path.splitext(file_name)[0]
            info = {"file_name": file_name}
            
            os.makedirs(self.output_folder, exist_ok=True)
            
            if progress_callback:
                progress_callback("Đang trích xuất PDF...", 0, 100)
            
            extractor = ExtractPages(file_path, self.output_folder)
            extractor.extract(logs=False, return_dict=False)
            
            vi_dir = f"{self.output_folder}/image/Quoc Ngu"
            nom_dir = f"{self.output_folder}/image/Han Nom"
            info['vi_dir'] = vi_dir
            info['nom_dir'] = nom_dir
            
            with open(self.name_file_info, 'w', encoding='utf-8') as f:
                json.dump(info, f, ensure_ascii=False, indent=4)
            
            if progress_callback:
                progress_callback("Trích xuất hoàn thành!", 100, 100)
            
            return info
        except Exception as e:
            raise Exception(f"Lỗi trích xuất PDF: {str(e)}")

    def crop_images(self, num_crop_qn: int, num_crop_hn: int, progress_callback=None) -> bool:
        """Cắt ảnh Quốc Ngữ và Hán Nôm"""
        try:
            info = self.read_file_info()
            
            if progress_callback:
                progress_callback("Đang cắt ảnh Quốc Ngữ...", 0, 100)
            self.crop_folder(info['vi_dir'], num_crop=num_crop_qn, progress_callback=progress_callback)
            
            if progress_callback:
                progress_callback("Đang cắt ảnh Hán Nôm...", 50, 100)
            self.crop_folder(info['nom_dir'], num_crop=num_crop_hn, progress_callback=progress_callback)
            
            self.write_file_info(info)
            
            if progress_callback:
                progress_callback("Cắt ảnh hoàn thành!", 100, 100)
            
            return True
        except Exception as e:
            raise Exception(f"Lỗi cắt ảnh: {str(e)}")

    def edge_detection_crop(self, vi_model: str, nom_model: str, crop_qn: bool, crop_hn: bool, progress_callback=None) -> bool:
        """Áp dụng edge detection để cắt ảnh"""
        try:
            if not PARENT_MODULES_AVAILABLE or EdgeDetection is None:
                raise ImportError("Parent modules (Proccess_pdf) not available. Make sure to run from ocr_corrector root directory.")
            
            info = self.read_file_info()
            
            if crop_qn:
                if progress_callback:
                    progress_callback("Đang xử lý Quốc Ngữ...", 0, 100)
                
                output_vi_dir = f"{self.output_folder}/image_processed/Quoc Ngu"
                edge_detection = EdgeDetection(info["vi_dir"], output_vi_dir, path_module=vi_model)
                edge_detection.process(crop=True, info="Processing Quoc Ngu: ")
                info["vi_dir"] = output_vi_dir
            
            if crop_hn:
                if progress_callback:
                    progress_callback("Đang xử lý Hán Nôm...", 50, 100)
                
                output_nom_dir = f"{self.output_folder}/image_processed/Han Nom"
                edge_detection = EdgeDetection(info["nom_dir"], output_nom_dir, path_module=nom_model)
                edge_detection.process(crop=True, info="Processing Han Nom: ")
                info["nom_dir"] = output_nom_dir
            
            self.write_file_info(info)
            
            if progress_callback:
                progress_callback("Edge detection hoàn thành!", 100, 100)
            
            return True
        except Exception as e:
            raise Exception(f"Lỗi edge detection: {str(e)}")

    def align_images(self, reverse_nom: bool, progress_callback=None) -> bool:
        """Căn chỉnh tên ảnh để align"""
        try:
            info = self.read_file_info()
            
            list_image_vi = os.listdir(info['vi_dir'])
            list_image_nom = os.listdir(info['nom_dir'])
            
            if len(list_image_vi) == 0 or len(list_image_nom) == 0:
                raise ValueError("Không tìm thấy ảnh trong các thư mục")
            
            list_image_vi = sorted(list_image_vi, key=lambda x: int(x.split('.')[0].split('_')[-1]))
            list_image_nom = sorted(list_image_nom, key=lambda x: int(x.split('.')[0].split('_')[-1]))
            
            if reverse_nom:
                list_image_nom.reverse()
            
            if progress_callback:
                progress_callback("Đang đổi tên ảnh...", 0, len(list_image_nom))
            
            for i in range(len(list_image_nom)):
                if progress_callback:
                    progress_callback(f"Đang đổi tên {i+1}/{len(list_image_nom)}", i, len(list_image_nom))
                
                output_path_vi = os.path.join(info['vi_dir'], list_image_vi[i])
                output_path_nom = os.path.join(info['nom_dir'], list_image_nom[i])
                new_name_vi = self.replace_number_in_filename(output_path_vi, i+1, type_str="vi")
                new_name_nom = self.replace_number_in_filename(output_path_nom, i+1, type_str="nom")
                os.rename(output_path_vi, new_name_vi)
                os.rename(output_path_nom, new_name_nom)
            
            self.write_file_info(info)
            
            if progress_callback:
                progress_callback("Căn chỉnh hoàn thành!", 100, 100)
            
            return True
        except Exception as e:
            raise Exception(f"Lỗi căn chỉnh: {str(e)}")

    def read_file_info(self) -> Dict[str, Any]:
        """Đọc thông tin từ file"""
        with open(self.name_file_info, 'r', encoding='utf-8') as f:
            return json.load(f)

    def write_file_info(self, info: Dict[str, Any]):
        """Ghi thông tin vào file"""
        with open(self.name_file_info, 'w', encoding='utf-8') as f:
            json.dump(info, f, ensure_ascii=False, indent=4)

    def check_num_pages(self) -> Dict[str, int]:
        """Kiểm tra số trang"""
        info = self.read_file_info()
        num_pages_vi = len(os.listdir(info['vi_dir']))
        num_pages_nom = len(os.listdir(info['nom_dir']))
        return {
            'vi': num_pages_vi,
            'nom': num_pages_nom
        }
