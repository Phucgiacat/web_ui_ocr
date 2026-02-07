import os
import ast
from typing import List, Tuple
import numpy as np
import pandas as pd
from difflib import SequenceMatcher
from tqdm import tqdm
from align.nom_process import process_nom


def _extract_name_and_last_number(filename: str) -> Tuple[str, int]:
    name_without_ext = os.path.splitext(filename)[0]
    parts = name_without_ext.split('_')
    first_name = parts[0] if parts else ''
    last_num = None
    for part in reversed(parts):
        if part.isdigit():
            last_num = int(part)
            break
    if last_num is None:
        last_num = float('inf')
    return (first_name, last_num)


def _read_txt_tokens(txt_path: str) -> List[str]:
    with open(txt_path, 'r', encoding='utf-8') as f:
        content = f.read().strip().replace('。', '').replace('，', '').replace('\n', '')
    if not content:
        return []
    if ' ' in content:
        return [t for t in content.replace('\n', ' ').split() if t]
    return list(content)


def _levenshtein_align_tokens(left: List[str], right: List[str]) -> Tuple[List[str], List[str]]:
    m, n = len(left), len(right)
    dp = np.zeros((m + 1, n + 1), dtype=int)
    back = np.full((m + 1, n + 1), '', dtype=object)
    for i in range(m + 1):
        dp[i][0] = i
        back[i][0] = 'U'
    for j in range(n + 1):
        dp[0][j] = j
        back[0][j] = 'L'
    back[0][0] = ''
    for i in range(1, m + 1):
        li = left[i - 1]
        for j in range(1, n + 1):
            rj = right[j - 1]
            cost = 0 if li == rj else 1
            options = [
                (dp[i - 1][j] + 1, 'U'),
                (dp[i][j - 1] + 1, 'L'),
                (dp[i - 1][j - 1] + cost, 'D'),
            ]
            dp[i][j], back[i][j] = min(options)
    aligned_left, aligned_right = [], []
    i, j = m, n
    while i > 0 or j > 0:
        if i > 0 and j > 0 and back[i][j] == 'D':
            aligned_left.append(left[i - 1])
            aligned_right.append(right[j - 1])
            i -= 1
            j -= 1
        elif i > 0 and back[i][j] == 'U':
            aligned_left.append(left[i - 1])
            aligned_right.append('*')
            i -= 1
        elif j > 0 and back[i][j] == 'L':
            aligned_left.append('*')
            aligned_right.append(right[j - 1])
            j -= 1
    aligned_left.reverse()
    aligned_right.reverse()
    return aligned_left, aligned_right


def _count_units_per_bbox(text_items: List[str]) -> List[int]:
    counts: List[int] = []
    for s in text_items:
        if not s:
            counts.append(0)
            continue
        if ' ' in s:
            counts.append(len([t for t in s.split() if t]))
        else:
            counts.append(len(s))
    return counts


def _flatten_units(text_items: List[str]) -> List[str]:
    tokens: List[str] = []
    word_mode = any((' ' in s) for s in text_items if s)
    if word_mode:
        for s in text_items:
            if not s:
                continue
            tokens.extend([t for t in s.split() if t])
    else:
        for s in text_items:
            if not s:
                continue
            tokens.extend(list(s))
    return tokens


def _pad_segments(lseg: List[str], rseg: List[str]) -> Tuple[List[str], List[str]]:
    """Pad the shorter segment with '*' so lengths match (keeps alignment rows)."""
    if len(lseg) < len(rseg):
        lseg = lseg + ['*'] * (len(rseg) - len(lseg))
    elif len(rseg) < len(lseg):
        rseg = rseg + ['*'] * (len(lseg) - len(rseg))
    return lseg, rseg


def _calculate_similarity(str1: str, str2: str) -> float:
    # Filter out Chinese punctuation and spaces: "，" (comma), "。" (period), and whitespace
    filtered1 = str1.replace("，", "").replace("。", "").replace(" ", "").strip()
    filtered2 = str2.replace("，", "").replace("。", "").replace(" ", "").strip()
    
    if not filtered1 and not filtered2:
        return 100.0
    if not filtered1 or not filtered2:
        return 0.0
    
    # Only compare if lengths match
    if len(filtered1) != len(filtered2):
        return 0.0
    
    # Count characters at same position
    match_count = sum(1 for c1, c2 in zip(filtered1, filtered2) if c1 == c2)
    return (match_count / len(filtered1)) * 100


def _write_skip_report(skip_messages, skip_report_path):
    if not skip_messages:
        print('No skipped files')
        return
    with open(skip_report_path, 'w', encoding='utf-8') as f:
        f.write('=== BAO CAO FILE BO QUA - ALIGN HAN ===\n\n')
        for msg in skip_messages:
            f.write(f"{msg}\n")
    print(f"Skip report: {skip_report_path} ({len(skip_messages)} warnings)")


def align_han(left_dir: str, right_dir: str, output_excel: str, k: int = 1, name_book: str = 'book', reverse: bool = False, mapping_path: str = None):
    """
    Align pure Hán Nôm text (not OCR) with Vietnamese translation
    
    Args:
        left_dir: Directory with Hán Nôm JSON files
        right_dir: Directory with Vietnamese TXT files
        output_excel: Output Excel file path
        k: Alignment mode (1=simple, 2=with mapping)
        name_book: Book name for output
        reverse: Reverse order
        mapping_path: Path to mapping Excel file (required for k=2)
    """
    output_dir = os.path.dirname(output_excel) or '.'
    skip_report_path = os.path.join(output_dir, 'align_han_skip_report.txt')
    
    if os.path.exists(output_excel):
        os.remove(output_excel)
    if os.path.exists(skip_report_path):
        os.remove(skip_report_path)
    
    results = []
    skip_messages = []
    left_files = sorted(os.listdir(left_dir), key=_extract_name_and_last_number)
    right_files = sorted([f for f in os.listdir(right_dir) if f.endswith('.txt')], key=_extract_name_and_last_number)
    
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
                # Nếu có extension, flexible match
                if item_ext in ['.json', '.txt', '.jpg', '.png']:
                    return item_path
        
        return None
    
    if k == 2:
        if not mapping_path:
            raise ValueError('k=2 requires mapping_path (path to mapping.xlsx)')
        if not os.path.exists(mapping_path):
            raise FileNotFoundError(f'Mapping file not found: {mapping_path}')
        
        df = pd.read_excel(mapping_path)
        # df = df.iloc[57:].reset_index(drop=True)
        
        for lst_left, lst_right in tqdm(zip(df['hannom'].to_list(), df['quocngu'].to_list()), desc='Preprocessing with mapping'):
            preprocess_left = []
            right_tokens = []
            files_left = ast.literal_eval(lst_left)
            files_right = ast.literal_eval(lst_right)
            
            # Sử dụng flexible file finding
            actual_left_files = []
            actual_right_files = []
            missing_left_list = []
            missing_right_list = []
            
            for f in files_left:
                actual_file = find_file_flexible(left_dir, f)
                if actual_file:
                    actual_left_files.append(actual_file)
                else:
                    missing_left_list.append(f)
            
            for f in files_right:
                actual_file = find_file_flexible(right_dir, f)
                if actual_file:
                    actual_right_files.append(actual_file)
                else:
                    missing_right_list.append(f)
            
            if missing_left_list or missing_right_list:
                msg = f"Skip mapping: missing files"
                if missing_left_list:
                    msg += f" - Left: {missing_left_list}"
                if missing_right_list:
                    msg += f" - Right: {missing_right_list}"
                print(msg)
                skip_messages.append(msg)
                print(f"   Found: Left={len(actual_left_files)}, Right={len(actual_right_files)}")
                continue
            
            for lf in actual_left_files:
                if lf.lower().endswith('.json'):
                    nom_data = process_nom(lf, 1)
                    number_units = _count_units_per_bbox(nom_data['text']) if nom_data.get('text') else []
                    file_name = os.path.basename(lf)
                    preprocess_left.append({'file_name': file_name, 'data': nom_data, 'number_units': number_units})
                else:
                    file_name = os.path.basename(lf)
                    msg = f"Skip {file_name}: left must be JSON to include bbox"
                    print(msg)
                    skip_messages.append(msg)
            
            for rf in actual_right_files:
                right_tokens.extend(_read_txt_tokens(rf))
            flat_left_all = []
            for page in preprocess_left:
                flat_left_all.extend(_flatten_units(page['data'].get('text', [])))
            aligned_left, aligned_right = _levenshtein_align_tokens(flat_left_all, right_tokens)
            left_remain, right_remain = aligned_left.copy(), aligned_right.copy()
            for page in preprocess_left:
                segments = []
                for num in page['number_units']:
                    if num == 0:
                        segments.append(([], []))
                        continue
                    
                    # Check if we have enough tokens left
                    if not left_remain:
                        # No more tokens - append empty segment
                        segments.append(([], []))
                        continue
                    
                    count = 0
                    i = 0
                    while i < len(left_remain):
                        if left_remain[i] != '*':
                            count += 1
                        i += 1
                        if count == num:
                            break
                    
                    # Warning if we couldn't get enough tokens
                    if count < num and i >= len(left_remain):
                        msg = f"Warning {page['file_name']}: Not enough tokens for bbox (need {num}, got {count})"
                        print(msg)
                        skip_messages.append(msg)
                    
                    lseg = left_remain[:i]
                    rseg = right_remain[:i]
                    segments.append((lseg, rseg))
                    left_remain = left_remain[i:]
                    right_remain = right_remain[i:]
                
                # Don't reset left_remain/right_remain here - let it continue to next page
                nom_data = page['data']
                if len(nom_data['bbox']) != len(segments):
                    msg = f"ERROR {page['file_name']}: bbox count ({len(nom_data['bbox'])}) != segments ({len(segments)}) - this should not happen!"
                    print(msg)
                    skip_messages.append(msg)
                    # Pad segments if needed
                    while len(segments) < len(nom_data['bbox']):
                        segments.append(([], []))
                    msg = f"  → Padded {len(nom_data['bbox']) - len(segments)} empty segments"
                    print(msg)
                    skip_messages.append(msg)
                for bbox_idx, (bbox, text_orig, (lseg, rseg)) in enumerate(zip(nom_data['bbox'], nom_data['text'], segments)):
                    # Get original text from bbox
                    orig_chars = set(text_orig) if text_orig else set()
                    
                    # Validate lseg only contains original chars + '*'
                    lseg_chars = set([c for c in lseg if c != '*'])
                    if lseg_chars - orig_chars:
                        # lseg contains chars not in original bbox - this is wrong!
                        extra_chars = lseg_chars - orig_chars
                        msg = f"Error {page['file_name']} bbox {bbox_idx}: OCR segment contains foreign chars {extra_chars}. Original: '{text_orig}', Got: {lseg}"
                        print(msg)
                        skip_messages.append(msg)
                        continue
                    
                    if len(lseg) != len(rseg):
                        lseg, rseg = _pad_segments(lseg, rseg)
                    left_str = ' '.join(lseg).strip()
                    right_str = ' '.join(rseg).strip()
                    if not left_str and not right_str:
                        continue
                    similarity = _calculate_similarity(left_str, right_str)
                    file_base = os.path.splitext(page['file_name'])[0]
                    results.append({
                        'ID': f"{file_base}_{bbox_idx}",
                        'File Name': page['file_name'],
                        'bbox': str(bbox),
                        'OCR': left_str,
                        'SinomChar': right_str,
                        'rate': round(similarity, 2),
                    })
            
            # After all pages processed, check for remaining tokens
            if left_remain or right_remain:
                left_excess = ' '.join([t for t in left_remain if t != '*'])
                right_excess = ' '.join([t for t in right_remain if t != '*'])
                if left_excess or right_excess:
                    msg = f"Warning after all pages: Excess tokens - Left: '{left_excess}', Right: '{right_excess}'"
                    print(msg)
                    skip_messages.append(msg)
    else:
        if not reverse:
            right_files = list(reversed(right_files))
        for idx, lf in enumerate(tqdm(left_files, desc='Processing files', unit='file')):
            if idx >= len(right_files):
                msg = f"Warning: more left files than right, skip {lf}"
                print(msg)
                skip_messages.append(msg)
                break
            rf = right_files[idx]
            left_path = os.path.join(left_dir, lf)
            right_path = os.path.join(right_dir, rf)
            try:
                if not lf.lower().endswith('.json'):
                    msg = f"Skip {lf}: left must be JSON to include bbox"
                    print(msg)
                    skip_messages.append(msg)
                    continue
                nom_data = process_nom(left_path, 1)
                if not nom_data.get('text') or not nom_data.get('bbox'):
                    msg = f"Skip {lf}: missing text or bbox"
                    print(msg)
                    skip_messages.append(msg)
                    continue
                right_tokens = _read_txt_tokens(right_path)
                if not right_tokens:
                    msg = f"Skip {lf}: right tokens empty"
                    print(msg)
                    skip_messages.append(msg)
                    continue
            except Exception as e:
                import traceback
                msg = f"Error reading {lf} or {rf}: {e}\n   Traceback: {traceback.format_exc()}"
                print(msg)
                skip_messages.append(msg)
                continue
            number_units = _count_units_per_bbox(nom_data['text'])
            flat_left = _flatten_units(nom_data['text'])
            aligned_left, aligned_right = _levenshtein_align_tokens(flat_left, right_tokens)
            left_remain, right_remain = aligned_left.copy(), aligned_right.copy()
            segments = []
            for num in number_units:
                if num == 0:
                    segments.append(([], []))
                    continue
                count = 0
                i = 0
                while i < len(left_remain):
                    if left_remain[i] != '*':
                        count += 1
                    i += 1
                    if count == num:
                        break
                lseg = left_remain[:i]
                rseg = right_remain[:i]
                segments.append((lseg, rseg))
                left_remain = left_remain[i:]
                right_remain = right_remain[i:]
            if left_remain or right_remain:
                # Don't append remainder to last bbox - log warning instead
                left_excess = ' '.join([t for t in left_remain if t != '*'])
                right_excess = ' '.join([t for t in right_remain if t != '*'])
                if left_excess or right_excess:
                    msg = f"Warning {lf}: Excess tokens after distribution - Left: '{left_excess}', Right: '{right_excess}'"
                    print(msg)
                    skip_messages.append(msg)
            if len(nom_data['bbox']) != len(segments):
                msg = f"Skip {lf}: bbox count ({len(nom_data['bbox'])}) != segments ({len(segments)})"
                print(msg)
                skip_messages.append(msg)
                continue
            file_base = os.path.splitext(lf)[0]
            for bbox_idx, (bbox, text_orig, (lseg, rseg)) in enumerate(zip(nom_data['bbox'], nom_data['text'], segments)):
                # Get original text from bbox
                orig_chars = set(text_orig) if text_orig else set()
                
                # Validate lseg only contains original chars + '*'
                lseg_chars = set([c for c in lseg if c != '*'])
                if lseg_chars - orig_chars:
                    # lseg contains chars not in original bbox - this is wrong!
                    extra_chars = lseg_chars - orig_chars
                    msg = f"Error {lf} bbox {bbox_idx}: OCR segment contains foreign chars {extra_chars}. Original: '{text_orig}', Got: {lseg}"
                    print(msg)
                    skip_messages.append(msg)
                    continue
                
                if len(lseg) != len(rseg):
                    lseg, rseg = _pad_segments(lseg, rseg)
                left_str = ' '.join(lseg).strip()
                right_str = ' '.join(rseg).strip()
                if not left_str and not right_str:
                    continue
                similarity = _calculate_similarity(left_str, right_str)
                results.append({
                    'ID': f"{file_base}_{bbox_idx}",
                    'File Name': lf.replace('.json', '.jpg'),
                    'bbox': str(bbox),
                    'OCR': left_str,
                    'SinomChar': right_str,
                    'rate': round(similarity, 2),
                })
    if results:
        df_out = pd.DataFrame(results)
        # Ensure column order
        df_out = df_out[['ID', 'File Name', 'bbox', 'OCR', 'SinomChar', 'rate']]
        df_out.to_excel(output_excel, index=False, engine='openpyxl')
        print(f"Saved {len(results)} rows to {output_excel}")
    else:
        print('No results to write')
    _write_skip_report(skip_messages, skip_report_path)
