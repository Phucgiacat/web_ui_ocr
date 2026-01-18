from .logger import Logger
import os
import json
from .ocr_client import OCR, UploadImageReq, OCRReq
import time
from tqdm import tqdm
from dotenv import load_dotenv
load_dotenv(".env")
import os

def  nom_ocr(nom_dir, output_json_dir, output_image_dir, start=0, ocr_id=1, lang_type=0, epitaph=0, progress_callback=None):
    nom_logger = Logger('NOMOCR', stdout='DEBUG', file='DEBUG', file_name="nom_ocr/logs/main.log")
    start = int(start or 0)
    files = [f for f in os.listdir(nom_dir) if os.path.isfile(os.path.join(nom_dir, f))]
    total = len(files)
    count = 0
    for file in tqdm(files, desc="Processing ocr images: "):
        print('nom_ocr: processing file ->', file)
        count += 1
        if count < start:
            continue
        time.sleep(1)
        if progress_callback:
            try:
                progress_callback(f"OCR Hán Nôm: {count}/{total}", count, total)
            except Exception:
                pass
        agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)...'
        ocr_client = OCR()
        os.makedirs(output_image_dir,exist_ok=True)
        os.makedirs(output_json_dir, exist_ok=True)
        image_path = os.path.join(nom_dir, file)
        output_json_path = os.path.join(output_json_dir, file.replace(".jpg", ".json"))
        output_image_path = os.path.join(output_image_dir, file.replace(".jpg", ".jpeg"))

        req = UploadImageReq(image=image_path)
        try:
            print('nom_ocr: calling ocr_client.upload_image')
            result = ocr_client.upload_image(req, agent=agent)
            print('nom_ocr: upload_image returned ->', getattr(result, 'data', None) and getattr(result.data, 'file_name', None))
        except Exception as e:
            nom_logger.error(f"Error: {image_path} - Upload: {e}")
            break

        req = OCRReq(ocr_id=ocr_id, file_name=result.data.file_name)
        try:
            print('nom_ocr: calling ocr_client.ocr ->', output_json_path)
            # pass explicit ocr params to the client so it uses our web settings
            result = ocr_client.ocr(req, output_file=output_json_path, agent=agent, ocr_id=ocr_id, lang_type=lang_type, epitaph=epitaph)
            print('nom_ocr: ocr returned ->', getattr(result, 'data', None) and getattr(result.data, 'result_file_name', None))
        except Exception as e:
            nom_logger.error(f"Error: {image_path} - OCR: {e}")
            break
        # attach metadata to saved OCR JSON for traceability
        try:
            if os.path.exists(output_json_path):
                with open(output_json_path, "r", encoding='utf-8') as f:
                    data = json.load(f)
            else:
                data = {}

            # add/overwrite metadata
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
                # fallback: attempt to extract file_name from original result
                file_name = result.data.file_name
            except Exception:
                file_name = None
        
        try:
            ocr_client.download_image(file_name, output_image_path, agent=agent)
        except Exception as e:
            nom_logger.error(f"Error: {image_path} - Download: {e}")
            break
        time.sleep(2)
        print("đang xử lý ảnh tiếp theo...")
        
        
# if __name__ == "__main__":
#     nom_dir = "data/nom/image_proccess"
#     output_json_dir = "output/json_1"
#     output_image_dir = "output/images_1"
#     index = 237
#     nom_ocr(nom_dir, output_json_dir, output_image_dir, index)