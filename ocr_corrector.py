"""
OCR Corrector - Công cụ OCR và alignment cho tài liệu Hán Nôm và Quốc Ngữ

Công cụ này hỗ trợ:
- OCR tài liệu Quốc Ngữ và Hán Nôm
- Alignment giữa văn bản Quốc Ngữ và Hán Nôm
- Correction và marking tự động
"""
import argparse
import logging
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional

import pandas as pd
from dotenv import load_dotenv

from align.align import align
from align.color import convert_txt_to_ecel, marking
from handle_data import read_file_info, write_file_info, str2bool
from nom_ocr.nom_ocr import nom_ocr
from vi_ocr.vi_ocr import vi_ocr

# Load environment variables
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


def process_ocr(
    ocr_vi_nom: tuple[bool, bool],
    info: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Xử lý OCR cho Quốc Ngữ và/hoặc Hán Nôm
    
    Args:
        ocr_vi_nom: Tuple (ocr_quoc_ngu, ocr_han_nom)
        info: Dictionary chứa thông tin file
    
    Returns:
        Updated info dictionary
    
    Raises:
        FileNotFoundError: Nếu không tìm thấy thư mục input
        ValueError: Nếu thông tin thiếu hoặc không hợp lệ
    """
    logger.info("Bắt đầu xử lý OCR...")
    
    ocr_quoc_ngu, ocr_han_nom = ocr_vi_nom
    
    # OCR Quốc Ngữ
    if ocr_quoc_ngu:
        logger.info("Đang OCR Quốc Ngữ...")
        
        if 'vi_dir' not in info or not os.path.exists(info['vi_dir']):
            raise FileNotFoundError(f"Không tìm thấy thư mục Quốc Ngữ: {info.get('vi_dir', 'N/A')}")
        
        info['ocr_txt_qn'] = f"{OUTPUT_FOLDER}/ocr/Quoc_Ngu_ocr"
        os.makedirs(info['ocr_txt_qn'], exist_ok=True)
        
        vi_ocr(info['vi_dir'], info['ocr_txt_qn'])
        logger.info(f"✓ Hoàn thành OCR Quốc Ngữ: {info['ocr_txt_qn']}")
    
    # OCR Hán Nôm
    if ocr_han_nom:
        logger.info("Đang OCR Hán Nôm...")
        
        if 'nom_dir' not in info or not os.path.exists(info['nom_dir']):
            raise FileNotFoundError(f"Không tìm thấy thư mục Hán Nôm: {info.get('nom_dir', 'N/A')}")
        
        info['ocr_json_nom'] = f"{OUTPUT_FOLDER}/ocr/Han_Nom_ocr"
        info['ocr_image_nom'] = f"{OUTPUT_FOLDER}/ocr/image_bbox"
        
        os.makedirs(info['ocr_json_nom'], exist_ok=True)
        os.makedirs(info['ocr_image_nom'], exist_ok=True)
        
        nom_ocr(info['nom_dir'], info['ocr_json_nom'], info['ocr_image_nom'])
        logger.info(f"✓ Hoàn thành OCR Hán Nôm: {info['ocr_json_nom']}")
    
    return info


def process_alignment(
    align_k: int,
    info: Dict[str, Any],
    align_reverse: bool = False,
    mapping_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Xử lý alignment giữa Quốc Ngữ và Hán Nôm
    
    Args:
        align_k: Tham số k (1=không mapping, 2=có mapping)
        info: Dictionary chứa thông tin file
        align_reverse: Đảo ngược thứ tự (chỉ với k=1)
        mapping_path: Đường dẫn file mapping (bắt buộc khi k=2)
    
    Returns:
        Updated info dictionary
    
    Raises:
        ValueError: Nếu thiếu thông tin hoặc tham số không hợp lệ
        FileNotFoundError: Nếu không tìm thấy file/folder cần thiết
    """
    logger.info(f"Bắt đầu alignment với k={align_k}...")
    
    # Validate inputs
    if align_k not in [1, 2]:
        raise ValueError(f"align_k phải là 1 hoặc 2, nhận được: {align_k}")
    
    # Check required paths
    ocr_txt_qn = info.get('ocr_txt_qn')
    ocr_json_nom = info.get('ocr_json_nom')
    file_name = info.get('file_name', 'book')
    
    if not ocr_txt_qn or not ocr_json_nom:
        raise ValueError(
            "Chưa OCR! Cần chạy OCR trước khi align.\n"
            f"ocr_txt_qn: {ocr_txt_qn}\n"
            f"ocr_json_nom: {ocr_json_nom}"
        )
    
    if not os.path.exists(ocr_json_nom):
        raise FileNotFoundError(f"Không tìm thấy thư mục JSON Hán Nôm: {ocr_json_nom}")
    
    if not os.path.exists(ocr_txt_qn):
        raise FileNotFoundError(f"Không tìm thấy thư mục TXT Quốc Ngữ: {ocr_txt_qn}")
    
    # Validate mapping path for k=2
    if align_k == 2:
        if not mapping_path:
            mapping_path = info.get('mapping_path')
            if not mapping_path:
                raise ValueError(
                    "k=2 yêu cầu mapping_path (đường dẫn file mapping.xlsx).\n"
                    "Sử dụng --mapping_path hoặc đảm bảo mapping_path có trong JSON."
                )
        
        if not os.path.exists(mapping_path):
            raise FileNotFoundError(f"Không tìm thấy file mapping: {mapping_path}")
        
        info['mapping_path'] = mapping_path
    
    # Setup output
    info['output_txt'] = f"{OUTPUT_FOLDER}/result.txt"
    info['align_param'] = align_k
    info['align_reverse'] = align_reverse if align_k == 1 else False
    
    os.makedirs(os.path.dirname(info['output_txt']), exist_ok=True)
    
    # Remove old output if exists
    if os.path.exists(info['output_txt']):
        os.remove(info['output_txt'])
        logger.info("Đã xóa file output cũ")
    
    # Run alignment
    align(
        ocr_json_nom,
        ocr_txt_qn,
        info['output_txt'],
        k=align_k,
        name_book=file_name,
        reverse=align_reverse if align_k == 1 else False,
        mapping_path=mapping_path
    )
    
    logger.info(f"✓ Align thành công! Output: {info['output_txt']}")
    return info


def process_correction(
    info: Dict[str, Any],
    debug: bool = False
) -> Dict[str, Any]:
    """
    Xử lý correction và marking
    
    Args:
        info: Dictionary chứa thông tin file
        debug: Bật chế độ debug
    
    Returns:
        Updated info dictionary
    
    Raises:
        ValueError: Nếu chưa align
        FileNotFoundError: Nếu không tìm thấy file output
    """
    logger.info("Bắt đầu correction...")
    
    # Validate
    if 'output_txt' not in info or not info.get('output_txt'):
        raise ValueError("Chưa align! Cần chạy --align trước.")
    
    if not os.path.exists(info['output_txt']):
        raise FileNotFoundError(f"Không tìm thấy file align output: {info['output_txt']}")
    
    file_name = info.get('file_name', 'book')
    type_qn = int(os.environ.get('TYPE_QN', 0))
    
    # Setup output
    info['Result'] = f"{OUTPUT_FOLDER}/result.xlsx"
    os.makedirs(os.path.dirname(info['Result']), exist_ok=True)
    
    # Run correction
    logger.info("Chuyển đổi TXT sang Excel...")
    convert_txt_to_ecel(info['output_txt'], info['Result'], debug=debug, namebook=file_name)
    
    logger.info("Đang marking...")
    df = pd.read_excel(info['Result'])
    marking(df, info['Result'], debug=debug, type_qn=type_qn)
    
    logger.info(f"✓ Correction thành công! Output: {info['Result']}")
    return info


def main() -> int:
    """
    Hàm chính của chương trình
    
    Returns:
        Exit code (0 = success, 1 = error)
    """
    parser = argparse.ArgumentParser(
        description='OCR Corrector - Công cụ OCR và alignment cho Hán Nôm',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument(
        '--ocr',
        type=str2bool,
        nargs=2,
        metavar=('QN', 'HN'),
        help='OCR Quốc Ngữ (QN) và/hoặc Hán Nôm (HN). VD: --ocr true false'
    )
    
    parser.add_argument(
        '--align',
        type=int,
        choices=[1, 2],
        help='Alignment với k=1 (không mapping) hoặc k=2 (có mapping)'
    )
    
    parser.add_argument(
        '--align_reverse',
        type=str2bool,
        help='Đảo ngược thứ tự TXT (chỉ áp dụng khi k=1)'
    )
    
    parser.add_argument(
        '--mapping_path',
        type=str,
        help='Đường dẫn file mapping.xlsx (bắt buộc khi k=2)'
    )
    
    parser.add_argument(
        '--corrector',
        type=str2bool,
        help='Chạy correction và marking'
    )
    
    args = parser.parse_args()
    
    try:
        # Process OCR
        if args.ocr:
            info = read_file_info()
            info = process_ocr(tuple(args.ocr), info)
            write_file_info(info)
        
        # Process Alignment
        if args.align is not None:
            info = read_file_info()
            info = process_alignment(
                align_k=args.align,
                info=info,
                align_reverse=args.align_reverse or False,
                mapping_path=args.mapping_path
            )
            write_file_info(info)
        
        # Process Correction
        if args.corrector is not None:
            info = read_file_info()
            info = process_correction(info, debug=args.corrector)
            write_file_info(info)
        
        if not any([args.ocr, args.align is not None, args.corrector is not None]):
            parser.print_help()
            return 1
        
        return 0
        
    except FileNotFoundError as e:
        logger.error(f"❌ Lỗi file: {e}")
        return 1
    except ValueError as e:
        logger.error(f"❌ Lỗi tham số: {e}")
        return 1
    except Exception as e:
        logger.error(f"❌ Lỗi không xác định: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
