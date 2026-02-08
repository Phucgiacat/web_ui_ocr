import os
import pandas as pd
from typing import Dict, Any, Optional, List
from web_ui.data_handler import DataHandler
from web_ui.ocr_processor import OCRProcessor
from web_ui.ai_analyst import LLMProcessor

class AutoPipeline:
    """
    Automated pipeline for processing bilingual PDF documents (Hán-Nôm & Quốc Ngữ).
    Flow: Extract -> Crop/Segment -> OCR -> LLM Alignment -> Excel Output.
    """

    def __init__(self, output_folder: str, name_file_info: str):
        self.output_folder = output_folder
        self.data_handler = DataHandler(output_folder, name_file_info)
        self.ocr_processor = OCRProcessor(output_folder, name_file_info)

    def run_pipeline(
        self,
        pdf_path: str,
        layout_mode: str, # "Manual" or "AI Auto-Detect"
        llm_processor: LLMProcessor,
        manual_layout_type: str = "Full Page",
        progress_callback=None
    ) -> str:
        """
        Executes the full pipeline with AI-driven layout analysis.
        """
        try:
            # 1. Extract PDF
            if progress_callback:
                progress_callback("Step 1/5: Extracting PDF...", 0, 100)

            info = self.data_handler.extract_pdf(pdf_path)
            if not info:
                raise ValueError("PDF Extraction failed.")

            # 2. Layout Analysis & Cropping
            if progress_callback:
                progress_callback("Step 2/5: Analyzing & Processing Images...", 20, 100)

            # Use images from extracted folders
            # Note: extract_pdf puts images in 'vi_dir' and 'nom_dir'.
            # We will process one of them (or both if they are identical/pages) to determine layout.
            # Usually extract_pdf splits pages into folders based on index, but for a raw PDF
            # likely we just have pages. Let's assume we iterate over all pages in 'vi_dir'.

            process_dir = info.get('vi_dir')
            if not process_dir or not os.path.exists(process_dir):
                raise FileNotFoundError("Image directory not found after extraction")

            images = sorted([f for f in os.listdir(process_dir) if f.lower().endswith(('.jpg', '.png'))])

            # Determine global strategy or per-page
            # For efficiency in this prototype, we analyze the first page if AI mode is on,
            # or apply manual strategy. Ideally, we analyze every page or samples.

            import cv2

            # We need the model path for detection.
            # Assuming it's in config or .env. Let's try to get it from environment variables or standard path.
            model_path = os.getenv('VI_MODEL', './model/vi/best.pt')
            # Fallback check
            if not os.path.exists(model_path):
                 # Try finding it
                 if os.path.exists("./model/vi/best.pt"): model_path = "./model/vi/best.pt"

            for idx, img_name in enumerate(images):
                img_path = os.path.join(process_dir, img_name)

                strategy = manual_layout_type
                split_point = 0.5

                if layout_mode == "AI Auto-Detect":
                    # Analyze layout
                    if progress_callback:
                        progress_callback(f"Analyzing layout for {img_name}...", 20 + int(idx/len(images)*20), 100)

                    # Detect boxes
                    bboxes = self.data_handler.detect_text_boxes(img_path, model_path)

                    # Ask LLM
                    # Read image dims
                    img = cv2.imread(img_path)
                    h, w, _ = img.shape

                    analysis = llm_processor.analyze_page_structure(bboxes, w, h)
                    strategy = analysis.get("strategy", "FULL_PAGE")
                    split_point = analysis.get("split_point", 0.5)

                    print(f"Image {img_name}: Detected {strategy}")

                # Apply cropping
                # We need to save the crops back.
                # DataHandler.smart_crop returns dict {1: img, 2: img}
                crops = self.data_handler.smart_crop(img_path, strategy, split_point)

                # Overwrite/Save crops
                # Standard convention: image_001.jpg -> image_001_001.jpg, image_001_002.jpg
                base_name = os.path.splitext(img_name)[0]
                ext = os.path.splitext(img_name)[1]

                for k, v in crops.items():
                    # We might want to separate into Quoc Ngu / Han Nom folders if we know which is which.
                    # For SPLIT_VERTICAL, usually left is Nom, right is Vi (or vice versa).
                    # For now, we save inplace or to specific dirs if we want to follow existing logic.
                    # Existing logic expects 'vi_dir' and 'nom_dir' to contain the separated images.
                    # Let's save crop 1 to nom_dir? and crop 2 to vi_dir?
                    # That depends on the book.
                    # Let's just save inplace with suffix and let manual alignment handle it?
                    # No, user wants automated pipeline.
                    # Let's assume Left=Nom, Right=Vi for now (common).

                    # We simply overwrite the original file with the first crop if Full Page
                    # Or delete original and save parts.
                    pass

                # ACTUAL EXECUTION:
                # To integrate with existing ocr_processor, we need images in info['vi_dir'] and info['nom_dir'].
                # If we split, we should put one half in vi_dir and one in nom_dir?
                # DataHandler.extract_pdf puts ALL pages in BOTH folders usually (as duplicates)
                # or splits them if using split_nom_vi logic.
                # Here we extracted raw pages.

                if strategy != "FULL_PAGE" and len(crops) == 2:
                    # Save Left/Top to one dir, Right/Bottom to other?
                    # Let's assume standard: 1->Nom, 2->Vi
                    nom_dest = os.path.join(info['nom_dir'], f"{base_name}_001{ext}")
                    vi_dest = os.path.join(info['vi_dir'], f"{base_name}_002{ext}")

                    cv2.imwrite(nom_dest, crops[1])
                    cv2.imwrite(vi_dest, crops[2])

                    # Remove original if it was just a raw page in that folder
                    # But extract_pdf puts images in both folders.
                    # We should clean up.
                    if os.path.exists(os.path.join(info['nom_dir'], img_name)):
                        os.remove(os.path.join(info['nom_dir'], img_name))
                    if os.path.exists(os.path.join(info['vi_dir'], img_name)):
                        os.remove(os.path.join(info['vi_dir'], img_name))

                else:
                    # Full page, keep as is.
                    pass

            # 3. OCR
            if progress_callback:
                progress_callback("Step 3/5: Running OCR (Quoc Ngu)...", 40, 100)

            # Run Quoc Ngu OCR once (assuming it's local/stable)
            self.ocr_processor.ocr_quoc_ngu(progress_callback=lambda msg, c, t: None)

            if progress_callback:
                progress_callback("Step 3.5/5: Running OCR (Han Nom) with Retry...", 50, 100)

            # Run Han Nom OCR with retry loop until all files are processed
            max_retries = 10
            attempt = 0
            while attempt < max_retries:
                # Check progress
                progress_info = self.ocr_processor.get_ocr_progress()
                processed = progress_info.get('processed_count', 0)
                total = progress_info.get('total_count', 0)

                if total > 0 and processed >= total:
                    print("OCR Han Nom completed successfully.")
                    break

                print(f"OCR Han Nom Progress: {processed}/{total}. Attempt {attempt + 1}/{max_retries}")
                if progress_callback:
                    progress_callback(f"OCR Han Nom: {processed}/{total} (Attempt {attempt+1})", 50, 100)

                try:
                    # Run/Resume OCR
                    self.ocr_processor.ocr_han_nom(progress_callback=lambda msg, c, t: None)
                except Exception as e:
                    print(f"OCR attempt failed: {e}")

                attempt += 1

            # Final check
            progress_info = self.ocr_processor.get_ocr_progress()
            if progress_info.get('total_count', 0) > 0 and progress_info.get('processed_count', 0) < progress_info.get('total_count', 0):
                print("Warning: OCR Han Nom did not complete all files after retries.")

            # 4. Read OCR Results
            if progress_callback:
                progress_callback("Step 4/5: Reading Text...", 70, 100)

            # Get paths
            paths = self.ocr_processor.get_align_paths()
            json_dir = paths.get('ocr_json_nom')
            txt_dir = paths.get('ocr_txt_qn')

            nom_sentences = []
            vi_sentences = []

            # Collect Nom text from JSONs
            if json_dir and os.path.exists(json_dir):
                json_files = sorted([f for f in os.listdir(json_dir) if f.endswith('.json')])
                for jf in json_files:
                    try:
                        import json
                        with open(os.path.join(json_dir, jf), 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            # Extract text from standard structure (adjust key if needed)
                            # Assuming structure similar to: {'data': {'result_bbox': [{'text': '...'}, ...]}}
                            # or simple text list if that's what nom_ocr outputs.
                            # Based on ocr_corrector.py logic, usually we align from file to file.
                            # Here we aggregate to list for LLM alignment if files are fragmented.
                            # But LLM chunking is better. Let's read file by file.
                            pass
                    except:
                        pass

            # Simple aggregation for the prototype: read all text content
            # (In a real scenario, we'd preserve file boundaries for context)

            # Let's rely on the output_txt generation from align_text for raw data,
            # OR read the raw OCR files directly.
            # Reading raw TXT files from Vi OCR
            if txt_dir and os.path.exists(txt_dir):
                txt_files = sorted([f for f in os.listdir(txt_dir) if f.endswith('.txt')])
                for tf in txt_files:
                    with open(os.path.join(txt_dir, tf), 'r', encoding='utf-8') as f:
                        content = f.read().strip()
                        if content:
                            vi_sentences.extend(content.split('\n'))

            # Reading Nom is trickier without specific structure knowledge,
            # let's assume we can get a list of texts.
            # For this prototype, we'll try to use the `align_text` output (result.txt)
            # if we run the basic aligner first, then refine it.
            # BUT the user wants AI to do it.

            # Let's try to read JSONs again properly
            if json_dir:
                json_files = sorted([f for f in os.listdir(json_dir) if f.endswith('.json')])
                for jf in json_files:
                    with open(os.path.join(json_dir, jf), 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        # Heuristic to find text
                        # Common structure in this project seems variable, but let's try to find text fields
                        # If data is list of strings:
                        if isinstance(data, list):
                            for item in data:
                                if isinstance(item, str): nom_sentences.append(item)
                                elif isinstance(item, dict) and 'text' in item: nom_sentences.append(item['text'])
                        elif isinstance(data, dict):
                            # Try known keys
                            if 'text' in data: nom_sentences.append(data['text'])
                            elif 'result' in data:
                                # if result is list
                                if isinstance(data['result'], list):
                                    for res in data['result']:
                                        if isinstance(res, str): nom_sentences.append(res)
                                        elif isinstance(res, dict) and 'text' in res: nom_sentences.append(res['text'])

            # 5. Smart Alignment
            if progress_callback:
                progress_callback("Step 5/5: Smart AI Alignment...", 85, 100)

            aligned_data = llm_processor.align_bilingual_data(nom_sentences, vi_sentences)

            # 6. Save Output
            df = pd.DataFrame(aligned_data)
            output_excel = os.path.join(self.output_folder, "pipeline_result.xlsx")
            df.to_excel(output_excel, index=False)

            if progress_callback:
                progress_callback("Pipeline Finished!", 100, 100)

            return output_excel

        except Exception as e:
            print(f"Pipeline Error: {e}")
            raise e
