import pandas as pd
import numpy as np
import ast
import os
from pathlib import Path
from .nom_process import process_nom
from .vi_process import process_quoc_ngu
from tqdm import tqdm
from dotenv import load_dotenv
load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env", override=True)

def build_dicts(similar_df, trans_df):
    trans_dict = {}
    for _, row in trans_df.iterrows():
        word, han_char = row.iloc[0], row.iloc[1]
        trans_dict.setdefault(word, []).append(han_char)

    similar_dict = {}
    for _, row in similar_df.iterrows():
        char, sim_char = row.iloc[0], row.iloc[1]
        similar_dict.setdefault(char, []).append(sim_char)

    return trans_dict, similar_dict

def is_compatible(han_nom_char, quoc_ngu_word, trans_dict, similar_dict):
    hn_candidates = trans_dict.get(quoc_ngu_word, [])
    similar_chars = similar_dict.get(han_nom_char, []) + [han_nom_char]
    return bool(set(hn_candidates) & set(similar_chars))

def levenshtein_align_boxes(nom_list, qn_list, similar_df, trans_df):
    trans_dict, similar_dict = build_dicts(similar_df, trans_df)
    m, n = len(nom_list), len(qn_list)
    dp = np.zeros((m + 1, n + 1), dtype=int)
    backtrace = np.full((m + 1, n + 1), '', dtype=object)

    for i in range(m + 1):
        dp[i][0] = i
        backtrace[i][0] = 'U'
    for j in range(n + 1):
        dp[0][j] = j
        backtrace[0][j] = 'L'
    backtrace[0][0] = ''

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            match = is_compatible(nom_list[i - 1], qn_list[j - 1], trans_dict, similar_dict)
            cost = 0 if match else 1
            options = [
                (dp[i - 1][j] + 1, 'U'),
                (dp[i][j - 1] + 1, 'L'),
                (dp[i - 1][j - 1] + cost, 'D')
            ]
            dp[i][j], backtrace[i][j] = min(options)

    aligned_nom, aligned_qn = [], []
    i, j = m, n
    while i > 0 or j > 0:
        if i > 0 and j > 0 and backtrace[i][j] == 'D':
            aligned_nom.append(nom_list[i - 1])
            aligned_qn.append(qn_list[j - 1])
            i -= 1
            j -= 1
        elif i > 0 and backtrace[i][j] == 'U':
            aligned_nom.append(nom_list[i - 1])
            aligned_qn.append("*")
            i -= 1
        elif j > 0 and backtrace[i][j] == 'L':
            aligned_nom.append("*")
            aligned_qn.append(qn_list[j - 1])
            j -= 1

    aligned_nom.reverse()
    aligned_qn.reverse()
    return [aligned_nom, aligned_qn]

def align(nom_dir, vi_dir, output_txt, k=1, name_book="book", reverse=False, mapping_path=None):
    similar = pd.read_excel(os.environ['NOM_SIMILARITY_DICTIONARY'])
    trans = pd.read_excel(os.environ['QN2NOM_DICTIONARY']).iloc[:, [0, 1]]
    
    # Xóa file output cũ nếu có
    if os.path.exists(output_txt):
        os.remove(output_txt)
    
    # Extract first name and last number from filename for sorting
    def extract_name_and_last_number(filename):
        """Extract first name part and last number from filename.
        e.g., phuc_001_002_001.json -> ('phuc', 1)
        """
        name_without_ext = os.path.splitext(filename)[0]
        parts = name_without_ext.split("_")
        
        # Get first part as name
        first_name = parts[0] if parts else ""
        
        # Get last number
        last_num = None
        for part in reversed(parts):
            if part.isdigit():
                last_num = int(part)
                break
        
        if last_num is None:
            last_num = float('inf')
        
        return (first_name, last_num)
    
    # Get JSON files sorted by (first_name, last_number)
    json_files_list = sorted(os.listdir(nom_dir), key=extract_name_and_last_number)
    
    # Get TXT files sorted by (first_name, last_number)
    txt_files_list = sorted([f for f in os.listdir(vi_dir) if f.endswith('.txt')], 
                             key=extract_name_and_last_number)
    
    # Check if file counts match
    json_count = len(json_files_list)
    txt_count = len(txt_files_list)
    if json_count != txt_count:
        print(f"⚠️ Cảnh báo: Số lượng file không bằng nhau. JSON: {json_count}, TXT: {txt_count}")
    
    # Xử lý theo k=1 hoặc k=2
    if k == 2:
        # K=2: Sử dụng mapping file
        if not mapping_path:
            raise ValueError("k=2 yêu cầu mapping_path (đường dẫn file mapping.xlsx)")
        if not os.path.exists(mapping_path):
            raise FileNotFoundError(f"Không tìm thấy file mapping: {mapping_path}")
        
        # Đọc mapping file
        df = pd.read_excel(mapping_path)
        df = df.iloc[57:].reset_index(drop=True)
        
        # Helper function để flexible kiểm tra file tồn tại
        def find_file_flexible(dir_path, target_filename):
            """
            Tìm file flexible - support case insensitive và mismatch extension
            
            Args:
                dir_path: Thư mục cần tìm
                target_filename: Tên file cần tìm
            
            Returns:
                Full path nếu tìm thấy, None nếu không
            """
            if not os.path.isdir(dir_path):
                return None
            
            # Thử kiểm tra trực tiếp trước
            full_path = os.path.join(dir_path, target_filename)
            if os.path.exists(full_path):
                return full_path
            
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
                    # Nếu có extension, thử match extension
                    if target_ext:
                        # Flexible extension matching (e.g., .json có thể là .txt, etc)
                        if item_ext in ['.json', '.txt', '.jpg', '.png']:
                            return item_path
                    else:
                        return item_path
            
            return None
        
        # Preprocess và align theo mapping
        for lst_han, lst_qn in tqdm(zip(df["hannom"].to_list(), df["quocngu"].to_list()), desc="Preprocessing with mapping"):
            preprocess_han = []
            preprocess_qn = []
            files_han = ast.literal_eval(lst_han)
            files_qn = ast.literal_eval(lst_qn)

            # Bỏ qua mapping nếu bất kỳ file JSON/TXT nào không tồn tại
            # Sử dụng flexible checking
            actual_han_files = []
            actual_qn_files = []
            missing_han_list = []
            missing_qn_list = []
            
            for f in files_han:
                actual_file = find_file_flexible(nom_dir, f)
                if actual_file:
                    actual_han_files.append(actual_file)
                else:
                    missing_han_list.append(f)
            
            for f in files_qn:
                actual_file = find_file_flexible(vi_dir, f)
                if actual_file:
                    actual_qn_files.append(actual_file)
                else:
                    missing_qn_list.append(f)
            
            if missing_han_list or missing_qn_list:
                print(f"⚠️ Bỏ qua mapping: thiếu file")
                if missing_han_list:
                    print(f"   Hán Nôm: {missing_han_list}")
                if missing_qn_list:
                    print(f"   Quốc Ngữ: {missing_qn_list}")
                print(f"   Tìm được: Hán={len(actual_han_files)}, QN={len(actual_qn_files)}")
                continue
            
            # Xử lý từng file Hán Nôm
            for file_path in actual_han_files:
                nom_data = process_nom(file_path, 1)
                file_name = os.path.basename(file_path)
                preprocess_han.append({
                    "file_name": file_name,
                    "data": nom_data, 
                    "number words": [len(box) for box in nom_data["text"]], 
                    "text": "".join(nom_data["text"])
                })
            
            # Xử lý từng file Quốc Ngữ
            for file_path in actual_qn_files:
                quoc_ngu_list = process_quoc_ngu(file_path)
                preprocess_qn.extend(quoc_ngu_list)
            
            # Align
            flatten_nom = list("".join([page["text"] for page in preprocess_han]))
            aligned_hn, aligned_qn = levenshtein_align_boxes(flatten_nom, preprocess_qn, similar, trans)
            hn_remain, qn_remain = aligned_hn.copy(), aligned_qn.copy()
            
            # Xử lý từng page
            for page_idx, page_content in enumerate(preprocess_han):
                segments = []
                for num in page_content["number words"]:
                    if num == 0:
                        segments.append(("", ""))
                        continue
                    count, i = 0, 0
                    while i < len(hn_remain):
                        if hn_remain[i] != "*":
                            count += 1
                        i += 1
                        if count == num:
                            break
                    han_seg = hn_remain[:i]
                    qn_seg = qn_remain[:i]
                    segments.append((han_seg, qn_seg))
                    hn_remain = hn_remain[i:]
                    qn_remain = qn_remain[i:]
                
                # Xử lý phần còn lại: thêm vào segment cuối cùng nếu có
                # Chỉ thêm vào page cuối cùng của row hiện tại
                if page_idx == len(preprocess_han) - 1:
                    if hn_remain or qn_remain:
                        if segments:
                            last_han, last_qn = segments[-1]
                            segments[-1] = (last_han + hn_remain, last_qn + qn_remain)
                        else:
                            segments.append((hn_remain, qn_remain))
                
                # Ghi kết quả
                nom_data = page_content["data"]
                if len(nom_data['bbox']) != len(segments):
                    print(f"⚠️ Bỏ qua {page_content['file_name']}: Số bbox ({len(nom_data['bbox'])}) ≠ segments ({len(segments)})")
                    continue
                
                with open(output_txt, "a", encoding="utf-8") as f:
                    for bbox, (han_seg, qn_seg) in zip(nom_data['bbox'], segments):
                        if len(han_seg) != len(qn_seg):
                            print(f"⚠️ Warning: Mismatch độ dài align tại file {page_content['file_name']}. Hán={len(han_seg)}, Việt={len(qn_seg)}")
                            continue
                        nom = ''.join(han_seg).strip()
                        qn = ' '.join(qn_seg).strip()
                        
                        if not nom and not qn:
                            continue
                        
                        f.write(f"{page_content['file_name']}\t{str(bbox)}\t{nom}\t{qn}\n")
        
        return  # K=2 đã xử lý xong
    
    # K=1: Xử lý bình thường (code cũ)
    # When NOT reverse (default): TXT is reversed (paired high-to-low)
    # When reverse=True: TXT is normal order (paired low-to-high)
    if not reverse:
        txt_files_list = list(reversed(txt_files_list))
    
    # Match files by position after sorting/reversing
    for idx, json_file in enumerate(tqdm(json_files_list, desc="Processing files", unit="file")):
        if idx >= len(txt_files_list):
            print(f"⚠️ Cảnh báo: Số lượng file JSON vượt quá TXT, bỏ qua {json_file}")
            break
        
        txt_file = txt_files_list[idx]
        
        try:
            nom_data = process_nom(os.path.join(nom_dir, json_file), k)
            quoc_ngu_list = process_quoc_ngu(os.path.join(vi_dir, txt_file))
        except Exception as e:
            import traceback
            print(f"❌ Lỗi khi đọc file {json_file} hoặc {txt_file}: {e}")
            print(f"   Chi tiết: {traceback.format_exc()}")
            continue
        
        # Check if nom_data has text
        print(f"🔍 DEBUG {json_file}: text={len(nom_data.get('text', []))}, bbox={len(nom_data.get('bbox', []))}, k={k}")
        if not nom_data.get('text') or not nom_data.get('bbox'):
            print(f"⚠️ Bỏ qua {json_file}: không có text hoặc bbox (text: {len(nom_data.get('text', []))}, bbox: {len(nom_data.get('bbox', []))})")
            continue
        
        # Check if quoc_ngu_list is empty
        if not quoc_ngu_list:
            print(f"⚠️ Bỏ qua {json_file}: không có text Quốc Ngữ")
            continue

        segments = []
        # if k == 1:
        num_word_hn = [len(sentence) for sentence in nom_data['text']]
        flatten_nom = list("".join(nom_data['text']))
        aligned_hn, aligned_qn = levenshtein_align_boxes(flatten_nom, quoc_ngu_list, similar, trans)
        hn_remain, qn_remain = aligned_hn.copy(), aligned_qn.copy()
        for num in num_word_hn:
            if num == 0:
                segments.append(("", ""))
                continue
            count, i = 0, 0
            while i < len(hn_remain):
                if hn_remain[i] != "*":
                    count += 1
                i += 1
                if count == num:
                    break

            han_seg = hn_remain[:i]
            qn_seg = qn_remain[:i]
            segments.append((han_seg, qn_seg))
            hn_remain = hn_remain[i:]
            qn_remain = qn_remain[i:]

        if hn_remain or qn_remain:
            if segments:
                last_han, last_qn = segments[-1]
                segments[-1] = (last_han + hn_remain, last_qn + qn_remain)
            else:
                segments.append((hn_remain, qn_remain))

        with open(output_txt, "a", encoding="utf-8") as f:
            if len(nom_data['bbox']) != len(segments):
                print(f"⚠️ Bỏ qua {json_file}: Số bbox ({len(nom_data['bbox'])}) ≠ segments ({len(segments)})")
                continue
            for bbox, (han_seg, qn_seg) in zip(nom_data['bbox'], segments):
                if len(han_seg) != len(qn_seg):
                    print(f"⚠️ Warning: Mismatch độ dài align tại file {json_file}. Hán={len(han_seg)}, Việt={len(qn_seg)}")
                    continue
                nom = ''.join(han_seg).strip()
                qn = ' '.join(qn_seg).strip()

                if not nom and not qn:
                    continue

                f.write(f"{json_file}\t{str(bbox)}\t{nom}\t{qn}\n")


# if __name__ == "__main__":
#     input_dir = r"D:\lab NLP\test\output\json\\"
#     vi_dir = r"D:\lab NLP\test\output\vi_gg"
#     output_txt = "data/result.txt"
#     k = 5
#     align(input_dir, vi_dir, output_txt,k)