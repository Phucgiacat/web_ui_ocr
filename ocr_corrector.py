from vi_ocr.vi_ocr import vi_ocr
from nom_ocr.resize import process_images_in_directory
from nom_ocr.nom_ocr import nom_ocr
from dotenv import load_dotenv
import argparse
import json
from handle_data import read_file_info, write_file_info, str2bool
from align.color import convert_txt_to_ecel, marking
from align.align import align
import pandas as pd
import os
load_dotenv('.env')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        'Sentence alignment using sentence embeddings',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument('--ocr', type=str2bool, nargs=2, metavar={'QN', 'HN'},
                    help='ocr vi nom')
    
    parser.add_argument('--align', type=int, required=False,
                    help='align vi nom (tham số k cho align)')
    
    parser.add_argument('--align_reverse', type=str2bool, required=False,
                    help='align reverse (đảo thứ tự TXT, chỉ áp dụng khi k=1)')
    
    parser.add_argument('--mapping_path', type=str, required=False,
                    help='đường dẫn file mapping.xlsx (chỉ cần khi k=2)')
    
    parser.add_argument('--corrector', type=str2bool, required=False,
                        help='correct')

    args = parser.parse_args()
    ocr_vi_nom = args.ocr if args.ocr else None
    algin = args.align if args.align else None
    align_reverse = args.align_reverse if args.align_reverse is not None else False
    mapping_path = args.mapping_path if args.mapping_path else None
    correct = args.corrector

    if ocr_vi_nom:
        info = read_file_info()
        if ocr_vi_nom[0]: # <--- ocr quốc ngữ
            info['ocr_txt_qn'] = f"{os.environ['OUTPUT_FOLDER']}/ocr/Quoc_Ngu_ocr"
            vi_ocr(info['vi_dir'], info['ocr_txt_qn'])
        write_file_info(info) 

        if ocr_vi_nom[1]: # <--- ocr hán nôm
            info['ocr_json_nom'] = f"{os.environ['OUTPUT_FOLDER']}/ocr/Han_Nom_ocr"
            info['ocr_image_nom'] = f"{os.environ['OUTPUT_FOLDER']}/ocr/image_bbox"
            output_resize_path = f"{os.environ['OUTPUT_FOLDER']}/image/resized_images.txt"
            # process_images_in_directory(info['nom_dir'], output_resize_path)
            nom_ocr(info['nom_dir'], info['ocr_json_nom'], info['ocr_image_nom'])    
        write_file_info(info)
    
    if algin is not None:
        info = read_file_info()
        
        # Lấy thông tin từ JSON, nếu không có thì báo lỗi
        ocr_txt_qn = info.get('ocr_txt_qn')
        ocr_json_nom = info.get('ocr_json_nom')
        file_name = info.get('file_name', 'book')
        
        if not ocr_txt_qn or not ocr_json_nom:
            raise ValueError("chưa ocr !!! Cần chạy OCR trước khi align.")
        
        # Kiểm tra paths có tồn tại không
        if not os.path.exists(ocr_json_nom):
            raise FileNotFoundError(f"Không tìm thấy thư mục JSON: {ocr_json_nom}")
        if not os.path.exists(ocr_txt_qn):
            raise FileNotFoundError(f"Không tìm thấy thư mục TXT: {ocr_txt_qn}")
        
        # Tạo output path và lưu vào info
        info['output_txt'] = f"{os.environ['OUTPUT_FOLDER']}/result.txt"
        
        # Validate align_param (k)
        align_k = int(algin)
        if align_k not in [1, 2]:
            raise ValueError("align_param (k) chỉ chấp nhận giá trị 1 hoặc 2. 1=không có mapping, 2=có mapping file")
        
        # Validate mapping_path khi k=2
        if align_k == 2:
            if not mapping_path:
                # Thử lấy từ JSON
                mapping_path = info.get('mapping_path')
                if not mapping_path:
                    raise ValueError("k=2 yêu cầu mapping_path (đường dẫn file mapping.xlsx). Sử dụng --mapping_path hoặc đảm bảo mapping_path có trong JSON.")
            if not os.path.exists(mapping_path):
                raise FileNotFoundError(f"Không tìm thấy file mapping: {mapping_path}")
        
        # Lưu thông tin align vào JSON trước khi chạy
        info['align_param'] = align_k  # tham số k
        info['align_reverse'] = align_reverse  # tham số reverse (chỉ áp dụng khi k=1)
        if mapping_path:
            info['mapping_path'] = mapping_path
        
        # Tạo thư mục output nếu chưa có
        os.makedirs(os.path.dirname(info['output_txt']), exist_ok=True)
        
        # Xóa file output cũ nếu có
        if os.path.exists(info['output_txt']):
            os.remove(info['output_txt'])
        
        # Chạy align
        align(ocr_json_nom, ocr_txt_qn, info['output_txt'], 
              k=align_k, 
              name_book=file_name, 
              reverse=align_reverse if align_k == 1 else False,  # reverse chỉ áp dụng khi k=1
              mapping_path=mapping_path)
        
        # Lưu lại thông tin sau khi align xong
        write_file_info(info)
        print(f"✅ Align thành công! Output: {info['output_txt']}")
    
    if correct is not None:
        info = read_file_info()
        
        # Kiểm tra đã align chưa
        if 'output_txt' not in info or not info.get('output_txt'):
            raise ValueError("Chưa align xong! Cần chạy --align trước.")
        
        # Kiểm tra file output_txt có tồn tại không
        if not os.path.exists(info['output_txt']):
            raise FileNotFoundError(f"Không tìm thấy file align output: {info['output_txt']}")
        
        file_name = info.get('file_name', 'book')
        
        # Lưu thông tin path result xlsx
        info['Result'] = f"{os.environ['OUTPUT_FOLDER']}/result.xlsx"
        os.makedirs(os.path.dirname(info['Result']), exist_ok=True)
        
        # Chạy correction
        convert_txt_to_ecel(info['output_txt'], info['Result'], debug=correct, namebook=file_name)
        df = pd.read_excel(info['Result'])
        marking(df, info['Result'], debug=correct, type_qn=int(os.environ['TYPE_QN']))
        
        # Lưu lại thông tin sau khi correct xong
        write_file_info(info)
        print(f"✅ Correction thành công! Output: {info['Result']}")