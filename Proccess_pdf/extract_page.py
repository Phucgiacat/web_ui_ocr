from dataclasses import dataclass
import os
import fitz
from tqdm import tqdm
from google.cloud import vision
import io
import langdetect
import shutil
from pypdf import PdfReader
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
import time

creadiential_path = "D:/learning/lab NLP/Tool_news/AutoLabel_script/vi_ocr/vision_key.json"

# Cache cho Vision Client (tái sử dụng connection)
_vision_client_cache = None
_client_lock = Lock()

@dataclass
class ExtractPageResult:
    total_pages: int
    pages: list

    def return_dict(self):
        return {
            "total_pages": self.total_pages,
            "pages": self.pages[:5],  # Return only first 5 pages for preview
        }

def get_vision_client():
    """Lấy Vision Client từ cache (tái sử dụng connection)"""
    global _vision_client_cache
    if _vision_client_cache is None:
        with _client_lock:
            if _vision_client_cache is None:
                _vision_client_cache = vision.ImageAnnotatorClient.from_service_account_json(creadiential_path)
    return _vision_client_cache

class ExtractPages:
    def __init__(self, pdf_file_path, output_folder):
        os.makedirs(output_folder, exist_ok=True)
        self.pdf_file_path = pdf_file_path
        self.output_folder = output_folder
        self.nom_path = f"{output_folder}/image/Han Nom"
        self.quoc_ngu = f"{output_folder}/image/Quoc Ngu"
        self.doc = None
        self.reader = None
        print(f"PDF file path: {self.pdf_file_path}")
        print(f"Output folder: Nom -> {self.nom_path}, QN -> {self.quoc_ngu}")

    def extract_page_content(self, image_path):
        """Sử dụng Google Cloud Vision để OCR văn bản từ hình ảnh (với retry)"""
        max_retries = 2
        for attempt in range(max_retries):
            try:
                client = get_vision_client()
                
                # Đọc file ảnh và tải ngay (không giữ file handle)
                with io.open(image_path, 'rb') as image_file:
                    content = image_file.read()
                
                image = vision.Image(content=content)
                # Gửi yêu cầu OCR
                response = client.text_detection(image=image)
                texts = response.text_annotations

                return texts[0].description if texts else ''
            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(1)  # Retry sau 1 giây
                else:
                    print(f"Error in OCR for {image_path}: {e}")
                    return ''

    def _process_page(self, page_num, num_pages, image_name, dpi=500):
        """Xử lý một page - tách hàm để dùng cho threading"""
        _page_id = f"{image_name}_{str(page_num + 1).zfill(3)}"
        try:
            # Trích text bằng pypdf (tái sử dụng reader)
            if self.reader is None:
                self.reader = PdfReader(self.pdf_file_path)
            
            raw_text = self.reader.pages[page_num].extract_text()
            
            if raw_text and raw_text.strip():
                try:
                    detected_lang = langdetect.detect(raw_text)
                    save_folder = self.quoc_ngu if detected_lang == "vi" else self.nom_path
                except Exception:
                    save_folder = self.nom_path
                
                text_file_path = os.path.join(save_folder, f"{_page_id}.txt")
                os.makedirs(save_folder, exist_ok=True)
                with open(text_file_path, "w", encoding="utf-8") as f:
                    f.write(raw_text)
                return text_file_path, None
            else:
                return self._render_and_ocr_page(page_num, _page_id, dpi)
        except Exception as e:
            print(f"Error processing page {page_num}: {e}")
            return self._render_and_ocr_page(page_num, _page_id, dpi)

    def _render_and_ocr_page(self, page_num, _page_id, dpi=500):
        """Render page thành ảnh và OCR"""
        try:
            if self.doc is None:
                self.doc = fitz.open(self.pdf_file_path)
            
            page = self.doc.load_page(page_num)
            zoom = dpi / 72
            mat = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat)
            image_path = os.path.join(self.output_folder, f"{_page_id}.jpg")
            pix.save(image_path)

            # OCR
            page_content = self.extract_page_content(image_path)
            if page_content:
                try:
                    detected_lang = langdetect.detect(page_content)
                    save_folder = self.quoc_ngu if detected_lang == "vi" else self.nom_path
                except Exception:
                    save_folder = self.nom_path
            else:
                save_folder = self.nom_path

            os.makedirs(save_folder, exist_ok=True)
            image_new = os.path.join(save_folder, f"{_page_id}.jpg")
            shutil.move(image_path, image_new)
            return image_new, None
        except Exception as e:
            print(f"Error in render_and_ocr for page {page_num}: {e}")
            return None, str(e)

    def extract(self, logs=False, return_dict=False, dpi=500, max_workers=3):
        """
        Extract pages từ PDF với tối ưu hóa
        
        Args:
            logs: In log ra console
            return_dict: Trả về dict thay vì ExtractPageResult
            dpi: DPI cho rendering (mặc định 500)
            max_workers: Số thread xử lý song song (mặc định 3 để tránh rate limit Google Cloud)
        
        Tối ưu hóa:
        - Cache Vision Client để tái sử dụng connection
        - Loại bỏ imports không cần thiết
        - DRY: Trích chung code xử lý save folder logic
        - Giảm dupplication trong exception handling
        - ThreadPoolExecutor để OCR song song
        """
        if not os.path.exists(self.pdf_file_path):
            raise FileNotFoundError(f"File not found: {self.pdf_file_path}")

        existing_files = sorted(os.listdir(self.output_folder))
        if existing_files:
            file_paths = [os.path.join(self.output_folder, f) for f in existing_files]
            result = ExtractPageResult(len(existing_files), file_paths)
            if logs:
                print(f"Total pages extracted: {len(existing_files)}")
                print(f"Pages saved at: {self.output_folder}")
            return result.return_dict() if return_dict else result

        # Mở file một lần
        self.reader = PdfReader(self.pdf_file_path)
        self.doc = fitz.open(self.pdf_file_path)

        num_pages = len(self.reader.pages)
        image_name = os.path.splitext(os.path.basename(self.pdf_file_path))[0]

        print(f"Waiting for {num_pages} pages to be processed...")
        os.makedirs(self.nom_path, exist_ok=True)
        os.makedirs(self.quoc_ngu, exist_ok=True)
        os.makedirs(self.output_folder, exist_ok=True)

        page_names = []
        page_names_lock = Lock()

        # Xử lý với ThreadPoolExecutor để OCR song song
        # Giới hạn max_workers để tránh quá tải Google Cloud Vision API
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(self._process_page, page_num, num_pages, image_name, dpi): page_num 
                for page_num in range(num_pages)
            }
            
            for future in tqdm(as_completed(futures), total=num_pages, desc="Processing extract: "):
                page_num = futures[future]
                try:
                    result_path, error = future.result()
                    if result_path:
                        with page_names_lock:
                            page_names.append(result_path)
                    elif error:
                        print(f"Failed to process page {page_num}: {error}")
                except Exception as e:
                    print(f"Exception in page {page_num}: {e}")
                
                # Log progress
                if logs and (page_num + 1) % 50 == 0:
                    print(f"Page {page_num + 1} processed.")

        # Cleanup
        if self.doc:
            self.doc.close()

        if logs:
            print(f"Total pages extracted: {len(page_names)}")

        result = ExtractPageResult(num_pages, page_names)
        return result.return_dict() if return_dict else result