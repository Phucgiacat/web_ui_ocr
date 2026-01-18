from typing import Dict, Any, Optional
import pandas as pd
import os
import sys
import json

# Add parent directory to path to import parent modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import từ project gốc (optional)
PARENT_MODULES_AVAILABLE = False
vi_ocr = None
nom_ocr = None
align = None
convert_txt_to_ecel = None
marking = None

try:
    from vi_ocr.vi_ocr import vi_ocr as vi_ocr_func
    vi_ocr = vi_ocr_func
except (ImportError, Exception) as e:
    pass

try:
    from nom_ocr.nom_ocr import nom_ocr as nom_ocr_func
    nom_ocr = nom_ocr_func
except (ImportError, Exception) as e:
    pass

try:
    from nom_ocr.resize import process_images_in_directory
except (ImportError, Exception) as e:
    pass

try:
    from align.align import align
    from align.color import convert_txt_to_ecel, marking
    PARENT_MODULES_AVAILABLE = True
except (ImportError, Exception) as e:
    print(f"⚠️ Warning: Could not import align modules: {e}")
    PARENT_MODULES_AVAILABLE = False
    align = None
    convert_txt_to_ecel = None
    marking = None

class OCRProcessor:
    """Xử lý OCR cho Quốc Ngữ và Hán Nôm"""
    
    def __init__(self, output_folder: str, name_file_info: str, ocr_id: int = 1, lang_type: int = 0, epitaph: int = 0):
        self.output_folder = output_folder
        self.name_file_info = name_file_info
        self.ocr_id = ocr_id
        self.lang_type = lang_type
        self.epitaph = epitaph
    
    def ocr_quoc_ngu(self, progress_callback=None) -> bool:
        """OCR text Quốc Ngữ"""
        try:
            if vi_ocr is None:
                raise ImportError(
                    "❌ Vietnamese OCR (vi_ocr) is not fully configured.\n\n"
                    "Requirements:\n"
                    "1. Google Cloud Vision API credentials\n"
                    "2. Set GOOGLE_APPLICATION_CREDENTIALS environment variable\n"
                    "3. Configuration file at: ocr_corrector/vi_ocr/vision_key.json\n\n"
                    "This feature requires proper setup which is outside scope of this tool.\n"
                    "For now, you can:\n"
                    "- Use the text alignment feature (Align tab)\n"
                    "- Use the error correction feature (Sửa lỗi tab)\n"
                    "- Or configure Google Cloud credentials manually"
                )
            
            info = self.read_file_info()
            
            if progress_callback:
                progress_callback("Đang OCR Quốc Ngữ...", 0, 100)
            
            info['ocr_txt_qn'] = f"{self.output_folder}/ocr/Quoc_Ngu_ocr"
            vi_ocr(info['vi_dir'], info['ocr_txt_qn'])
            
            self.write_file_info(info)
            
            if progress_callback:
                progress_callback("OCR Quốc Ngữ hoàn thành!", 100, 100)
            
            return True
        except Exception as e:
            raise Exception(f"Lỗi OCR Quốc Ngữ: {str(e)}")
    
    def ocr_han_nom(self, progress_callback=None) -> bool:
        """OCR text Hán Nôm"""
        try:
            if nom_ocr is None:
                raise ImportError(
                    "❌ Sino-Vietnamese OCR (nom_ocr) is not fully configured.\n\n"
                    "Requirements:\n"
                    "1. External OCR API service connection\n"
                    "2. Network access to OCR service\n"
                    "3. Proper credentials/authentication setup\n\n"
                    "This feature requires special configuration.\n"
                    "For now, you can:\n"
                    "- Use the text alignment feature (Align tab)\n"
                    "- Use the error correction feature (Sửa lỗi tab)\n"
                    "- Or configure the OCR service manually"
                )
            
            info = self.read_file_info()
            
            if progress_callback:
                progress_callback("Đang OCR Hán Nôm...", 0, 100)
            
            info['ocr_json_nom'] = f"{self.output_folder}/ocr/Han_Nom_ocr"
            info['ocr_image_nom'] = f"{self.output_folder}/ocr/image_bbox"
            info['ocr_id'] = self.ocr_id
            info['lang_type'] = self.lang_type
            info['epitaph'] = self.epitaph
            process_images_in_directory(info['nom_dir'], "resized_images.txt")
            # Call nom_ocr with parameters from config
            nom_ocr(info['nom_dir'], info['ocr_json_nom'], info['ocr_image_nom'], start=0, ocr_id=self.ocr_id, lang_type=self.lang_type, epitaph=self.epitaph, progress_callback=progress_callback)
            
            self.write_file_info(info)
            
            if progress_callback:
                progress_callback("OCR Hán Nôm hoàn thành!", 100, 100)
            
            return True
        except Exception as e:
            raise Exception(f"Lỗi OCR Hán Nôm: {str(e)}")
    
    def ocr_both(self, progress_callback=None) -> bool:
        """OCR cả Quốc Ngữ và Hán Nôm"""
        try:
            self.ocr_quoc_ngu(progress_callback)
            self.ocr_han_nom(progress_callback)
            return True
        except Exception as e:
            raise Exception(f"Lỗi OCR: {str(e)}")
    
    def align_text(self, ocr_json_nom: str, ocr_txt_qn: str, output_txt: str = None, align_param: int = 30, name_book: str = "", reverse: bool = False, progress_callback=None) -> bool:
        """Align text Quốc Ngữ và Hán Nôm
        
        Args:
            ocr_json_nom: Thư mục chứa file JSON từ nom OCR (hoặc file JSON đơn)
            ocr_txt_qn: Thư mục chứa file TXT từ vi OCR (hoặc file TXT đơn)
            output_txt: Đường dẫn file output (mặc định: output_folder/result.txt)
            align_param: Tham số align (threshold), mặc định 30
            name_book: Tên sách (để ghi vào output)
            reverse: Nếu True, đảo thứ tự JSON (file đầu tiên JSON ứng với file cuối TXT)
            progress_callback: Callback để báo cáo tiến độ
        
        Note: 
            - Các file JSON và TXT phải có cùng tên (ví dụ: image_001.json và image_001.txt)
            - Hoặc chỉ truyền file JSON riêng lẻ kèm file TXT riêng lẻ
        """
        try:
            if not PARENT_MODULES_AVAILABLE or align is None:
                raise ImportError("Parent modules (align) not available. Make sure to run from ocr_corrector root directory.")
            
            # Validate that paths exist
            if not os.path.exists(ocr_json_nom):
                raise FileNotFoundError(f"Không tìm thấy thư mục JSON: {ocr_json_nom}")
            if not os.path.exists(ocr_txt_qn):
                raise FileNotFoundError(f"Không tìm thấy thư mục TXT: {ocr_txt_qn}")
            
            # Use provided paths or fallback to info file
            if not output_txt:
                output_txt = f"{self.output_folder}/result.txt"
            
            if progress_callback:
                progress_callback("Đang align text...", 0, 100)
            
            # Create output directory if needed
            os.makedirs(os.path.dirname(output_txt) or '.', exist_ok=True)
            
            align(ocr_json_nom, ocr_txt_qn, output_txt, align_param, name_book=name_book, reverse=reverse)
            
            # Update info file if it exists
            try:
                info = self.read_file_info()
                info['output_txt'] = output_txt
                self.write_file_info(info)
            except:
                pass
            
            if progress_callback:
                progress_callback("Align text hoàn thành!", 100, 100)
            
            return True
        except Exception as e:
            raise Exception(f"Lỗi align: {str(e)}")
    
    def correct_text(self, debug: bool = False, progress_callback=None) -> bool:
        """Sửa lỗi và tạo Excel"""
        try:
            if not PARENT_MODULES_AVAILABLE:
                raise ImportError("Parent modules (align.color) not available. Make sure to run from ocr_corrector root directory.")
            
            info = self.read_file_info()
            
            if 'output_txt' not in info:
                raise ValueError("Chưa align xong!")
            
            if progress_callback:
                progress_callback("Đang sửa lỗi và tạo Excel...", 0, 50)
            
            info['Result'] = f"{self.output_folder}/result.xlsx"
            name_book = info.get('file_name', '')
            
            convert_txt_to_ecel(info['output_txt'], info['Result'], debug=debug, namebook=name_book)
            
            if progress_callback:
                progress_callback("Đang đánh dấu...", 50, 100)
            
            df = pd.read_excel(info['Result'])
            type_qn = int(os.getenv('TYPE_QN', '1'))
            marking(df, info['Result'], debug=debug, type_qn=type_qn)
            
            self.write_file_info(info)
            
            if progress_callback:
                progress_callback("Sửa lỗi hoàn thành!", 100, 100)
            
            return True
        except Exception as e:
            raise Exception(f"Lỗi sửa lỗi: {str(e)}")
    
    def read_file_info(self) -> Dict[str, Any]:
        """Đọc thông tin từ file"""
        with open(self.name_file_info, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def write_file_info(self, info: Dict[str, Any]):
        """Ghi thông tin vào file"""
        with open(self.name_file_info, 'w', encoding='utf-8') as f:
            json.dump(info, f, ensure_ascii=False, indent=4)
