import os
import sys
import json
import shutil
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path để import các module
sys.path.insert(0, str(Path(__file__).parent.parent))

load_dotenv(Path(__file__).parent.parent / '.env')

class ConfigManager:
    """Quản lý cấu hình và môi trường"""
    
    def __init__(self):
        self.output_folder = os.getenv('OUTPUT_FOLDER', './output')
        self.name_file_info = os.getenv('NAME_FILE_INFO', 'before_handle_data.json')
        self.num_crop_hn = int(os.getenv('NUM_CROP_HN', '1'))
        self.num_crop_qn = int(os.getenv('NUM_CROP_QN', '1'))
        self.vi_model = os.getenv('VI_MODEL', './model/vi')
        self.nom_model = os.getenv('NOM_MODEL', './model/nom')
        # Default directories for OCR inputs
        self.vi_dir = os.getenv('VI_DIR', os.path.join(os.getcwd(), 'data', 'vi'))
        self.nom_dir = os.getenv('NOM_DIR', os.path.join(os.getcwd(), 'data', 'nom'))
        self.ocr_json_nom = os.getenv('OCR_JSON_NOM', os.path.join(os.getcwd(), 'data', 'nom', 'ocr_json_nom'))
        self.ocr_txt_qn = os.getenv('OCR_TXT_QN', os.path.join(os.getcwd(), 'data', 'vi', 'ocr_txt_qn'))
        
        # OCR Hán Nôm parameters
        self.ocr_id = int(os.getenv('OCR_ID', '1'))  # 1: thông thường dọc, 2: hành chính, 3: ngoại cảnh, 4: thông thường ngang
        self.lang_type = int(os.getenv('LANG_TYPE', '0'))  # 0: chưa biết, 1: Hán, 2: Nôm
        self.epitaph = int(os.getenv('EPITAPH', '0'))  # 0: văn bản thông thường, 1: văn bia
        
        # Config file for storing settings
        self.config_file = os.path.join(os.path.dirname(__file__), 'project_config.json')
        self.load_config()
        
    def load_config(self):
        """Load project config từ file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.output_folder = config.get('output_folder', self.output_folder)
                    self.num_crop_hn = config.get('num_crop_hn', self.num_crop_hn)
                    self.num_crop_qn = config.get('num_crop_qn', self.num_crop_qn)
                    self.ocr_id = config.get('ocr_id', self.ocr_id)
                    self.lang_type = config.get('lang_type', self.lang_type)
                    self.epitaph = config.get('epitaph', self.epitaph)
                    self.vi_dir = config.get('vi_dir', self.vi_dir)
                    self.nom_dir = config.get('nom_dir', self.nom_dir)
                    self.ocr_json_nom = config.get('ocr_json_nom', self.ocr_json_nom)
                    self.ocr_txt_qn = config.get('ocr_txt_qn', self.ocr_txt_qn)
                    self.name_file_info = config.get('name_file_info', self.name_file_info)
        except Exception as e:
            print(f"Error loading config: {e}")
    
    def save_config(self):
        """Save project config to file"""
        try:
            config = {
                'output_folder': self.output_folder,
                'num_crop_hn': self.num_crop_hn,
                'num_crop_qn': self.num_crop_qn,
                'ocr_id': self.ocr_id,
                'lang_type': self.lang_type,
                'epitaph': self.epitaph,
                'vi_dir': self.vi_dir,
                'nom_dir': self.nom_dir,
                'name_file_info': self.name_file_info,
            }
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False
    
    def save(self):
        """Alias for save_config()"""
        return self.save_config()
    
    def save_paths_to_info(self):
        """Save vi_dir and nom_dir to before_handle_data.json"""
        try:
            info = self.read_info() or {}
            info['vi_dir'] = self.vi_dir
            info['nom_dir'] = self.nom_dir
            return self.write_info(info)
        except Exception as e:
            print(f"Error saving paths to info: {e}")
            return False
        
    def get_info_file_path(self):
        """Lấy đường dẫn file thông tin"""
        return self.name_file_info
    
    def read_info(self):
        """Đọc thông tin từ file JSON"""
        try:
            if os.path.exists(self.name_file_info):
                with open(self.name_file_info, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error reading info file: {e}")
        return None
    
    def write_info(self, info: dict):
        """Ghi thông tin vào file JSON"""
        try:
            with open(self.name_file_info, 'w', encoding='utf-8') as f:
                json.dump(info, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            print(f"Error writing info file: {e}")
            return False
    
    def clear_output_folder(self):
        """Xóa folder output"""
        try:
            if os.path.exists(self.output_folder):
                shutil.rmtree(self.output_folder)
            return True
        except Exception as e:
            print(f"Error clearing output folder: {e}")
            return False
    
    def get_status(self):
        """Lấy trạng thái hiện tại"""
        info = self.read_info()
        status = {
            'extracted': info and 'file_name' in info,
            'cropped': info and 'vi_dir' in info,
            'ocr_vi': info and 'ocr_txt_qn' in info,
            'ocr_nom': info and 'ocr_json_nom' in info,
            'aligned': info and 'output_txt' in info,
            'corrected': info and 'Result' in info,
            'info': info
        }
        return status

