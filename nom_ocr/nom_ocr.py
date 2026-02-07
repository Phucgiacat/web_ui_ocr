from .logger import Logger
import os
import json
from .ocr_client import OCR, UploadImageReq, OCRReq
from .resize import resize_image
import time
from tqdm import tqdm
from dotenv import load_dotenv
load_dotenv(".env")
import os
import random

# ============================================
# RATE LIMITING CONFIGURATION
# ============================================
class RateLimitConfig:
    """Cấu hình rate limiting - có thể điều chỉnh từ .env"""
    
    # Base delays (seconds)
    DELAY_BEFORE_UPLOAD = float(os.getenv('DELAY_BEFORE_UPLOAD', '2'))
    DELAY_AFTER_UPLOAD = float(os.getenv('DELAY_AFTER_UPLOAD', '3'))
    DELAY_BEFORE_DOWNLOAD = float(os.getenv('DELAY_BEFORE_DOWNLOAD', '2'))
    DELAY_BETWEEN_FILES = float(os.getenv('DELAY_BETWEEN_FILES', '3'))
    
    # Retry configuration
    MAX_RETRIES = int(os.getenv('OCR_MAX_RETRIES', '3'))
    INITIAL_RETRY_DELAY = float(os.getenv('INITIAL_RETRY_DELAY', '5'))
    MAX_RETRY_DELAY = float(os.getenv('MAX_RETRY_DELAY', '60'))
    
    # Circuit breaker
    MAX_CONSECUTIVE_FAILURES = int(os.getenv('MAX_CONSECUTIVE_FAILURES', '5'))
    CIRCUIT_BREAKER_COOLDOWN = float(os.getenv('CIRCUIT_BREAKER_COOLDOWN', '30'))
    
    # Adaptive delay
    ENABLE_ADAPTIVE_DELAY = os.getenv('ENABLE_ADAPTIVE_DELAY', 'true').lower() == 'true'
    ADAPTIVE_DELAY_MULTIPLIER = float(os.getenv('ADAPTIVE_DELAY_MULTIPLIER', '1.5'))


def exponential_backoff(attempt, base_delay=5, max_delay=60, jitter=True):
    """
    Exponential backoff với jitter để tránh thundering herd
    
    Args:
        attempt: Lần thử thứ mấy (0-indexed)
        base_delay: Delay cơ bản (seconds)
        max_delay: Delay tối đa (seconds)
        jitter: Thêm random để tránh synchronized retries
    
    Returns:
        Số giây cần chờ
    """
    delay = min(base_delay * (2 ** attempt), max_delay)
    
    if jitter:
        # Add random jitter ±25%
        jitter_range = delay * 0.25
        delay = delay + random.uniform(-jitter_range, jitter_range)
    
    return max(delay, 0)


def smart_sleep(seconds, reason="", logger=None):
    """
    Sleep với logging và có thể interrupt
    
    Args:
        seconds: Số giây chờ
        reason: Lý do chờ (để log)
        logger: Logger instance
    """
    if seconds <= 0:
        return
    
    if logger:
        logger.debug(f"Sleeping {seconds:.2f}s - {reason}")
    
    time.sleep(seconds)

def count_processed_images(output_json_dir):
    """Đếm số ảnh đã OCR (dựa trên số file .json)"""
    if not os.path.exists(output_json_dir):
        return 0
    return len([f for f in os.listdir(output_json_dir) if f.endswith('.json')])

def get_next_unprocessed_file(nom_dir, output_json_dir):
    """Lấy file ảnh đầu tiên chưa được OCR
    
    Returns:
        (file_name, file_index) hoặc (None, 0) nếu tất cả đã xong
    """
    if not os.path.exists(output_json_dir):
        files = [f for f in os.listdir(nom_dir) if os.path.isfile(os.path.join(nom_dir, f))]
        return (files[0] if files else None, 0)
    
    files = [f for f in os.listdir(nom_dir) if os.path.isfile(os.path.join(nom_dir, f))]
    processed_json = set(f.replace('.json', '') for f in os.listdir(output_json_dir) if f.endswith('.json'))
    
    for idx, file in enumerate(files):
        base_name = file.replace(".jpg", "").replace(".jpeg", "").replace(".png", "")
        if base_name not in processed_json:
            return (file, idx)
    
    return (None, len(files))  # Tất cả đã xong

def  nom_ocr(nom_dir, output_json_dir, output_image_dir, start=0, ocr_id=1, lang_type=0, epitaph=0, progress_callback=None):
    nom_logger = Logger('NOMOCR', stdout='DEBUG', file='DEBUG', file_name="nom_ocr/logs/main.log")
    start = int(start or 0)
    files = [f for f in os.listdir(nom_dir) if os.path.isfile(os.path.join(nom_dir, f))]
    total = len(files)
    count = 0
    skipped = 0
    processed = 0
    
    # Rate limiting tracking
    consecutive_failures = 0
    total_failures = 0
    adaptive_delay_multiplier = 1.0
    
    # Load rate limit config
    config = RateLimitConfig()
    
    # Đếm số file đã OCR từ trước
    previously_processed = count_processed_images(output_json_dir)
    
    nom_logger.info(f"===== OCR SESSION START =====")
    nom_logger.info(f"Total files: {total}")
    nom_logger.info(f"Previously processed: {previously_processed}")
    nom_logger.info(f"Rate limit config:")
    nom_logger.info(f"  - Upload delay: {config.DELAY_BEFORE_UPLOAD}s")
    nom_logger.info(f"  - After upload: {config.DELAY_AFTER_UPLOAD}s")
    nom_logger.info(f"  - Download delay: {config.DELAY_BEFORE_DOWNLOAD}s")
    nom_logger.info(f"  - Between files: {config.DELAY_BETWEEN_FILES}s")
    nom_logger.info(f"  - Max retries: {config.MAX_RETRIES}")
    nom_logger.info(f"  - Circuit breaker: {config.MAX_CONSECUTIVE_FAILURES} failures")
    
    for file in tqdm(files, desc="Processing OCR images"):
        count += 1
        
        # Skip files before start index
        if count < start:
            continue
        
        # ===== CIRCUIT BREAKER CHECK =====
        if consecutive_failures >= config.MAX_CONSECUTIVE_FAILURES:
            nom_logger.error(f"⛔ CIRCUIT BREAKER ACTIVATED!")
            nom_logger.error(f"Too many consecutive failures ({consecutive_failures}). Cooling down for {config.CIRCUIT_BREAKER_COOLDOWN}s...")
            
            if progress_callback:
                try:
                    progress_callback(
                        f"⛔ Rate limit detected. Cooling down {config.CIRCUIT_BREAKER_COOLDOWN}s...", 
                        previously_processed + processed, 
                        total
                    )
                except Exception:
                    pass
            
            smart_sleep(config.CIRCUIT_BREAKER_COOLDOWN, "Circuit breaker cooldown", nom_logger)
            consecutive_failures = 0  # Reset after cooldown
            adaptive_delay_multiplier = min(adaptive_delay_multiplier * 1.5, 3.0)  # Increase caution
        
        # Tạo output paths
        os.makedirs(output_image_dir, exist_ok=True)
        os.makedirs(output_json_dir, exist_ok=True)
        image_path = os.path.join(nom_dir, file)
        output_json_path = os.path.join(output_json_dir, file.replace(".jpg", ".json").replace(".jpeg", ".json").replace(".png", ".json"))
        output_image_path = os.path.join(output_image_dir, file.replace(".jpg", ".jpeg").replace(".png", ".jpeg"))
        
        # ===== SKIP FILE ĐÃ OCR =====
        if os.path.exists(output_json_path):
            skipped += 1
            nom_logger.info(f"[SKIP] File đã OCR: {file} ({skipped} skipped, {processed} processed)")
            
            # Cập nhật progress
            if progress_callback:
                try:
                    progress_callback(
                        f"OCR Hán Nôm: {previously_processed}/{total} (Skip: {skipped}, New: {processed})", 
                        previously_processed, 
                        total
                    )
                except Exception:
                    pass
            continue
        
        # ===== XỬ LÝ FILE MỚI =====
        nom_logger.info(f'\n{"="*60}')
        nom_logger.info(f'Processing file: {file} ({count}/{total})')
        nom_logger.info(f'Stats: Skipped={skipped}, Processed={processed}, Failures={total_failures}')
        
        # Cập nhật progress cho file đang xử lý
        if progress_callback:
            try:
                progress_callback(
                    f"OCR Hán Nôm: {previously_processed + processed + 1}/{total} (Processing: {file})", 
                    previously_processed + processed, 
                    total
                )
            except Exception:
                pass
        
        agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)...'
        ocr_client = OCR()
        
        # ===== RETRY LOGIC WITH EXPONENTIAL BACKOFF =====
        upload_success = False
        ocr_success = False
        download_success = False
        resize_attempted = False
        resize_log_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "resized_retry_log.txt"))
        
        for attempt in range(config.MAX_RETRIES):
            try:
                # ===== RESIZE BEFORE FINAL RETRY =====
                if attempt == 2 and not resize_attempted and not (upload_success and ocr_success):
                    try:
                        resize_image(image_path)
                        os.makedirs(os.path.dirname(resize_log_path), exist_ok=True)
                        with open(resize_log_path, "a", encoding="utf-8") as log_f:
                            log_f.write(f"{file}\n")
                        nom_logger.warning(f"🔄 Resized image before retry {attempt + 1}: {file}")
                        resize_attempted = True
                        upload_success = False  # Reset upload success to retry upload
                    except Exception as resize_err:
                        nom_logger.error(f"Resize failed before retry {attempt + 1}: {resize_err}")

                # ===== UPLOAD IMAGE =====
                if not upload_success:
                    # Adaptive delay before upload
                    delay = config.DELAY_BEFORE_UPLOAD * adaptive_delay_multiplier
                    smart_sleep(delay, f"Before upload (attempt {attempt + 1})", nom_logger)
                    
                    req = UploadImageReq(image=image_path)
                    nom_logger.info(f'[Attempt {attempt + 1}/{config.MAX_RETRIES}] Uploading image: {file}')
                    result = ocr_client.upload_image(req, agent=agent)
                    nom_logger.info(f'✅ Upload success: {getattr(result, "data", None) and getattr(result.data, "file_name", None)}')
                    upload_success = True
                    
                    # Delay after successful upload
                    delay = config.DELAY_AFTER_UPLOAD * adaptive_delay_multiplier
                    smart_sleep(delay, "After upload", nom_logger)
                
                # ===== OCR PROCESSING =====
                if upload_success and not ocr_success:
                    req = OCRReq(ocr_id=ocr_id, file_name=result.data.file_name)
                    nom_logger.info(f'[Attempt {attempt + 1}/{config.MAX_RETRIES}] OCR processing: {file}')
                    result = ocr_client.ocr(req, output_file=output_json_path, agent=agent, ocr_id=ocr_id, lang_type=lang_type, epitaph=epitaph)
                    nom_logger.info(f'✅ OCR success: {getattr(result, "data", None) and getattr(result.data, "result_file_name", None)}')
                    ocr_success = True
                
                # If we got here, break the retry loop
                if upload_success and ocr_success:
                    break
                    
            except Exception as e:
                error_msg = str(e).lower()
                is_rate_limit = any(keyword in error_msg for keyword in ['rate', 'limit', 'too many', '429', 'quota'])
                
                nom_logger.error(f"❌ Error on attempt {attempt + 1}/{config.MAX_RETRIES}: {e}")
                
                if is_rate_limit:
                    nom_logger.warning(f"🚨 Rate limit detected!")
                
                # Last attempt failed
                if attempt == config.MAX_RETRIES - 1:
                    nom_logger.error(f"❌ All {config.MAX_RETRIES} attempts failed for {file}")
                    consecutive_failures += 1
                    total_failures += 1
                    break
                
                # Exponential backoff for retry
                backoff_delay = exponential_backoff(
                    attempt, 
                    base_delay=config.INITIAL_RETRY_DELAY,
                    max_delay=config.MAX_RETRY_DELAY
                )
                
                nom_logger.warning(f"⏳ Retrying in {backoff_delay:.2f}s...")
                
                if progress_callback:
                    try:
                        progress_callback(
                            f"⚠️ Error: {file}. Retry {attempt + 1}/{config.MAX_RETRIES} in {backoff_delay:.0f}s", 
                            previously_processed + processed, 
                            total
                        )
                    except Exception:
                        pass
                
                smart_sleep(backoff_delay, f"Exponential backoff (attempt {attempt + 1})", nom_logger)
        
        # Check if file processing succeeded
        if not (upload_success and ocr_success):
            nom_logger.error(f"❌ FAILED: {file} after {config.MAX_RETRIES} attempts")
            continue  # Skip to next file
        
        # ===== RESET FAILURE COUNTER ON SUCCESS =====
        consecutive_failures = 0  # Reset on successful upload + OCR
        
        # Adaptive delay adjustment - decrease if successful
        if config.ENABLE_ADAPTIVE_DELAY:
            adaptive_delay_multiplier = max(adaptive_delay_multiplier * 0.95, 1.0)
        
        # ===== SAVE METADATA =====
        try:
            if os.path.exists(output_json_path):
                with open(output_json_path, "r", encoding='utf-8') as f:
                    data = json.load(f)
            else:
                data = {}

            meta = data.get('meta', {}) if isinstance(data, dict) else {}
            meta.update({
                'ocr_id': int(ocr_id),
                'lang_type': int(lang_type),
                'epitaph': int(epitaph),
                'processed_file': result.data.result_file_name if getattr(result, 'data', None) else None
            })
            if isinstance(data, dict):
                data['meta'] = meta
            else:
                data = {'meta': meta}

            with open(output_json_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)

            file_name = data.get('data', {}).get('result_file_name') if isinstance(data, dict) else None

        except Exception as e:
            nom_logger.error(f"Warning: could not attach metadata to {output_json_path}: {e}")
            try:
                file_name = result.data.file_name
            except Exception:
                file_name = None
        
        # ===== DOWNLOAD RESULT IMAGE =====
        delay = config.DELAY_BEFORE_DOWNLOAD * adaptive_delay_multiplier
        smart_sleep(delay, "Before download", nom_logger)
        
        for attempt in range(config.MAX_RETRIES):
            try:
                nom_logger.info(f'[Attempt {attempt + 1}/{config.MAX_RETRIES}] Downloading: {file}')
                ocr_client.download_image(file_name, output_image_path, agent=agent)
                nom_logger.info(f'✅ Download success: {output_image_path}')
                download_success = True
                break
            except Exception as e:
                nom_logger.error(f"Download error: {e}")
                if attempt < config.MAX_RETRIES - 1:
                    backoff_delay = exponential_backoff(attempt, base_delay=2, max_delay=10)
                    smart_sleep(backoff_delay, "Download retry", nom_logger)
                else:
                    nom_logger.warning(f"⚠️ Download failed. JSON saved, continuing...")
        
        # ===== SUCCESS =====
        # ===== SAVE METADATA =====
        try:
            if os.path.exists(output_json_path):
                with open(output_json_path, "r", encoding='utf-8') as f:
                    data = json.load(f)
            else:
                data = {}

            meta = data.get('meta', {}) if isinstance(data, dict) else {}
            meta.update({
                'ocr_id': int(ocr_id),
                'lang_type': int(lang_type),
                'epitaph': int(epitaph),
                'processed_file': result.data.result_file_name if getattr(result, 'data', None) else None
            })
            if isinstance(data, dict):
                data['meta'] = meta
            else:
                data = {'meta': meta}

            with open(output_json_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)

            file_name = data.get('data', {}).get('result_file_name') if isinstance(data, dict) else None

        except Exception as e:
            nom_logger.error(f"Warning: metadata save failed for {output_json_path}: {e}")
            try:
                file_name = result.data.file_name
            except Exception:
                file_name = None
        
        # ===== DOWNLOAD RESULT IMAGE WITH RETRY =====
        download_success = False
        for attempt in range(config.MAX_RETRIES):
            try:
                smart_sleep(config.DELAY_BEFORE_DOWNLOAD, "Before download", nom_logger)
                nom_logger.info(f'Downloading result image: {file} (attempt {attempt + 1}/{config.MAX_RETRIES})')
                ocr_client.download_image(file_name, output_image_path, agent=agent)
                nom_logger.info(f'Download success: {output_image_path}')
                download_success = True
                break
            except Exception as e:
                error_msg = str(e).lower()
                if attempt < config.MAX_RETRIES - 1:
                    backoff_delay = exponential_backoff(attempt, base_delay=2, max_delay=10)
                    nom_logger.warning(f"Download failed (attempt {attempt + 1}): {e}. Retrying in {backoff_delay:.1f}s...")
                    smart_sleep(backoff_delay, "Download retry backoff", nom_logger)
                else:
                    nom_logger.error(f"Download failed after {config.MAX_RETRIES} attempts: {e}")
                    nom_logger.warning(f"JSON saved successfully, continuing...")
        
        # ===== SUCCESS HANDLING =====
        consecutive_failures = 0  # Reset on success
        adaptive_delay_multiplier = max(adaptive_delay_multiplier * 0.95, 1.0)  # Reduce multiplier
        processed += 1
        total_failures_in_session = total_failures  # Track for stats
        nom_logger.info(f"✅ SUCCESS: {file} (Processed={processed}, Skipped={skipped}, Failures={total_failures})")
        
        # Adaptive delay between files
        delay = config.DELAY_BETWEEN_FILES * adaptive_delay_multiplier
        smart_sleep(delay, f"Between files (multiplier={adaptive_delay_multiplier:.2f})", nom_logger)
        
        # Update progress callback
        if progress_callback:
            try:
                progress_callback(
                    f"OCR: {previously_processed + processed}/{total} (New: {processed}, Skip: {skipped})", 
                    previously_processed + processed, 
                    total
                )
            except Exception:
                pass
    
    # ===== SUMMARY =====
    nom_logger.info(f"===== OCR HOÀN THÀNH =====")
    nom_logger.info(f"Tổng file: {total}")
    nom_logger.info(f"Đã có sẵn (skip): {skipped}")
    nom_logger.info(f"Mới xử lý: {processed}")
    nom_logger.info(f"Tổng đã OCR: {previously_processed + processed}")
    
    if progress_callback:
        try:
            progress_callback(
                f"✅ OCR Hoàn thành! Tổng: {previously_processed + processed}/{total} (Skip: {skipped}, New: {processed})", 
                total, 
                total
            )
        except Exception:
            pass
        
        
# if __name__ == "__main__":
#     nom_dir = "data/nom/image_proccess"
#     output_json_dir = "output/json_1"
#     output_image_dir = "output/images_1"
#     index = 237
#     nom_ocr(nom_dir, output_json_dir, output_image_dir, index)