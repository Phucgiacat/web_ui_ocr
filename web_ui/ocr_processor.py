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
            
            # Kiểm tra vi_dir có trong info không
            if 'vi_dir' not in info:
                raise ValueError("Chưa extract PDF! Cần chạy extract PDF trước.")
            
            if progress_callback:
                progress_callback("Đang OCR Quốc Ngữ...", 0, 100)
            
            # Lưu thông tin path OCR Quốc Ngữ
            info['ocr_txt_qn'] = f"{self.output_folder}/ocr/Quoc_Ngu_ocr"
            os.makedirs(info['ocr_txt_qn'], exist_ok=True)
            
            # Chạy OCR
            vi_ocr(info['vi_dir'], info['ocr_txt_qn'])
            
            # Lưu lại thông tin sau khi OCR xong
            self.write_file_info(info)
            
            if progress_callback:
                progress_callback(f"OCR Quốc Ngữ hoàn thành! Output: {info['ocr_txt_qn']}", 100, 100)
            
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
            
            # Kiểm tra nom_dir có trong info không
            if 'nom_dir' not in info:
                raise ValueError("Chưa extract PDF! Cần chạy extract PDF trước.")
            
            if progress_callback:
                progress_callback("Đang OCR Hán Nôm...", 0, 100)
            
            # Lưu thông tin path OCR Hán Nôm
            info['ocr_json_nom'] = f"{self.output_folder}/ocr/Han_Nom_ocr"
            info['ocr_image_nom'] = f"{self.output_folder}/ocr/image_bbox"
            os.makedirs(info['ocr_json_nom'], exist_ok=True)
            os.makedirs(info['ocr_image_nom'], exist_ok=True)
            
            info['ocr_id'] = self.ocr_id
            info['lang_type'] = self.lang_type
            info['epitaph'] = self.epitaph
            
            process_images_in_directory(info['nom_dir'], "resized_images.txt")
            # Call nom_ocr with parameters from config
            nom_ocr(info['nom_dir'], info['ocr_json_nom'], info['ocr_image_nom'], start=0, ocr_id=self.ocr_id, lang_type=self.lang_type, epitaph=self.epitaph, progress_callback=progress_callback)
            
            # Lưu lại thông tin sau khi OCR xong
            self.write_file_info(info)
            
            if progress_callback:
                progress_callback(f"OCR Hán Nôm hoàn thành! Output JSON: {info['ocr_json_nom']}, Images: {info['ocr_image_nom']}", 100, 100)
            
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
    
    def set_align_paths(self, ocr_json_nom: str = None, ocr_txt_qn: str = None) -> Dict[str, str]:
        """Thiết lập đường dẫn cho align (thường được gọi khi user chọn folder)
        
        Args:
            ocr_json_nom: Đường dẫn folder/file JSON Hán Nôm (nếu None, lấy từ config)
            ocr_txt_qn: Đường dẫn folder/file TXT Quốc Ngữ (nếu None, lấy từ config)
        
        Returns:
            Dict chứa ocr_json_nom, ocr_txt_qn, status
        """
        try:
            info = self.read_file_info()
            
            # Nếu user cung cấp path, update vào config
            if ocr_json_nom:
                if not os.path.exists(ocr_json_nom):
                    raise FileNotFoundError(f"Không tìm thấy: {ocr_json_nom}")
                info['ocr_json_nom'] = ocr_json_nom
            
            if ocr_txt_qn:
                if not os.path.exists(ocr_txt_qn):
                    raise FileNotFoundError(f"Không tìm thấy: {ocr_txt_qn}")
                info['ocr_txt_qn'] = ocr_txt_qn
            
            # Lưu vào file config
            self.write_file_info(info)
            
            return {
                'ocr_json_nom': info.get('ocr_json_nom', ''),
                'ocr_txt_qn': info.get('ocr_txt_qn', ''),
                'status': 'success'
            }
        except Exception as e:
            return {
                'ocr_json_nom': '',
                'ocr_txt_qn': '',
                'status': f'error: {str(e)}'
            }
    
    def get_align_paths(self) -> Dict[str, str]:
        """Lấy đường dẫn align từ config
        
        Returns:
            Dict chứa ocr_json_nom, ocr_txt_qn
        """
        try:
            info = self.read_file_info()
            return {
                'ocr_json_nom': info.get('ocr_json_nom', ''),
                'ocr_txt_qn': info.get('ocr_txt_qn', '')
            }
        except Exception as e:
            return {
                'ocr_json_nom': '',
                'ocr_txt_qn': ''
            }
    
    def align_text(self, ocr_json_nom: str = None, ocr_txt_qn: str = None, output_txt: str = None, align_param: int = 30, name_book: str = "", reverse: bool = False, mapping_path: str = None, progress_callback=None) -> bool:
        """Align text Quốc Ngữ và Hán Nôm
        
        Args:
            ocr_json_nom: Thư mục chứa file JSON từ nom OCR (hoặc file JSON đơn)
                         Nếu None, sẽ lấy từ file JSON config
            ocr_txt_qn: Thư mục chứa file TXT từ vi OCR (hoặc file TXT đơn)
                       Nếu None, sẽ lấy từ file JSON config
            output_txt: Đường dẫn file output (mặc định: output_folder/result.txt)
            align_param: Tham số align (k), chỉ chấp nhận 1 hoặc 2. 1=không có mapping, 2=có mapping file
            name_book: Tên sách (để ghi vào output). Nếu rỗng, lấy từ file_name trong JSON
            reverse: Nếu True, đảo thứ tự JSON (file đầu tiên JSON ứng với file cuối TXT). Chỉ áp dụng khi k=1
            mapping_path: Đường dẫn file mapping.xlsx (chỉ cần khi k=2)
            progress_callback: Callback để báo cáo tiến độ
        
        Note: 
            - Các file JSON và TXT phải có cùng tên (ví dụ: image_001.json và image_001.txt)
            - Hoặc chỉ truyền file JSON riêng lẻ kèm file TXT riêng lẻ
            - Thông tin align sẽ được lưu vào before_handle_data.json
        """
        try:
            if not PARENT_MODULES_AVAILABLE or align is None:
                raise ImportError("Parent modules (align) not available. Make sure to run from ocr_corrector root directory.")
            
            # Đọc thông tin từ file JSON config
            info = self.read_file_info()
            
            # Lấy paths từ JSON nếu không được truyền
            if not ocr_json_nom:
                ocr_json_nom = info.get('ocr_json_nom', '')
            if not ocr_txt_qn:
                ocr_txt_qn = info.get('ocr_txt_qn', '')
            
            # Validate that paths exist
            if not ocr_json_nom:
                raise ValueError("Chưa set đường dẫn JSON (ocr_json_nom). Vui lòng chọn folder JSON hoặc chạy OCR trước.")
            if not ocr_txt_qn:
                raise ValueError("Chưa set đường dẫn TXT (ocr_txt_qn). Vui lòng chọn folder TXT hoặc chạy OCR trước.")
            
            if not os.path.exists(ocr_json_nom):
                raise FileNotFoundError(f"Không tìm thấy thư mục JSON: {ocr_json_nom}")
            if not os.path.exists(ocr_txt_qn):
                raise FileNotFoundError(f"Không tìm thấy thư mục TXT: {ocr_txt_qn}")
            
            # Lấy file_name từ JSON nếu name_book không được truyền
            if not name_book:
                name_book = info.get('file_name', 'book')
            
            # Tạo output path
            if not output_txt:
                output_txt = f"{self.output_folder}/result.txt"
            
            # Validate align_param (k)
            if align_param not in [1, 2]:
                raise ValueError("align_param (k) chỉ chấp nhận giá trị 1 hoặc 2. 1=không có mapping, 2=có mapping file")
            
            # Validate mapping_path khi k=2
            if align_param == 2:
                if not mapping_path:
                    raise ValueError("k=2 yêu cầu mapping_path (đường dẫn file mapping.xlsx)")
                if not os.path.exists(mapping_path):
                    raise FileNotFoundError(f"Không tìm thấy file mapping: {mapping_path}")
            
            # Lưu thông tin align vào JSON trước khi chạy
            info['ocr_json_nom'] = ocr_json_nom
            info['ocr_txt_qn'] = ocr_txt_qn
            info['output_txt'] = output_txt
            info['align_param'] = align_param  # tham số k
            info['align_reverse'] = reverse  # tham số reverse (chỉ áp dụng khi k=1)
            if mapping_path:
                info['mapping_path'] = mapping_path
            
            # Tạo thư mục output nếu chưa có
            os.makedirs(os.path.dirname(output_txt) or '.', exist_ok=True)
            
            # Xóa file output cũ nếu có
            if os.path.exists(output_txt):
                os.remove(output_txt)
            
            if progress_callback:
                progress_callback("Đang align text...", 0, 100)
            
            # Chạy align
            align(ocr_json_nom, ocr_txt_qn, output_txt, align_param, name_book=name_book, reverse=reverse, mapping_path=mapping_path)
            
            # Lưu lại thông tin sau khi align xong
            self.write_file_info(info)
            
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
            
            # Kiểm tra đã align chưa
            if 'output_txt' not in info or not info.get('output_txt'):
                raise ValueError("Chưa align xong! Cần chạy align trước.")
            
            # Kiểm tra file output_txt có tồn tại không
            if not os.path.exists(info['output_txt']):
                raise FileNotFoundError(f"Không tìm thấy file align output: {info['output_txt']}")
            
            file_name = info.get('file_name', 'book')
            
            if progress_callback:
                progress_callback("Đang sửa lỗi và tạo Excel...", 0, 50)
            
            # Lưu thông tin path result xlsx
            info['result_xlsx'] = f"{self.output_folder}/result.xlsx"
            os.makedirs(os.path.dirname(info['result_xlsx']), exist_ok=True)
            
            # Chạy correction
            convert_txt_to_ecel(info['output_txt'], info['result_xlsx'], debug=debug, namebook=file_name)
            
            if progress_callback:
                progress_callback("Đang đánh dấu...", 50, 100)
            
            df = pd.read_excel(info['result_xlsx'])
            type_qn = int(os.getenv('TYPE_QN', '1'))
            marking(df, info['result_xlsx'], debug=debug, type_qn=type_qn)
            
            # Lưu lại thông tin sau khi correct xong
            self.write_file_info(info)
            
            if progress_callback:
                progress_callback(f"Sửa lỗi hoàn thành! Output: {info['result_xlsx']}", 100, 100)
            
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
