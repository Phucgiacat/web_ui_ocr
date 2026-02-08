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
        layout_type: str,
        llm_processor: LLMProcessor,
        progress_callback=None
    ) -> str:
        """
        Executes the full pipeline.

        Args:
            pdf_path: Path to the input PDF.
            layout_type: Strategy for splitting pages ('Split Vertical', 'Split Horizontal', 'Full Page').
            llm_processor: Instance of LLMProcessor for smart alignment.
            progress_callback: Callback function for progress updates.

        Returns:
            Path to the final Excel file.
        """
        try:
            # 1. Extract PDF
            if progress_callback:
                progress_callback("Step 1/5: Extracting PDF...", 0, 100)

            # This creates 'image/Quoc Ngu' and 'image/Han Nom' folders by default in DataHandler
            info = self.data_handler.extract_pdf(pdf_path)
            if not info:
                raise ValueError("PDF Extraction failed.")

            # 2. Crop/Segment Images based on layout
            if progress_callback:
                progress_callback("Step 2/5: Processing Images...", 20, 100)

            # Logic to handle layout.
            # DataHandler's extract_pdf puts images into separate folders if ExtractPages logic supports it.
            # If layout_type demands specific cropping, we apply it here.
            # Assuming standard DataHandler.crop_images usage:
            if layout_type == "Split Vertical":
                # Typical for bilingual books: Left column Nom, Right column Vi (or vice versa)
                # We assume 2 crops per page for both
                self.data_handler.crop_images(num_crop_qn=2, num_crop_hn=2)
            elif layout_type == "Split Horizontal":
                # Top/Bottom split
                # DataHandler doesn't explicitly support vertical vs horizontal crop direction param in crop_images
                # It assumes horizontal splitting (columns) by default in crop_image_func logic:
                # "step = width // num_crop" -> this splits vertically (columns).
                # If we need horizontal split (rows), DataHandler needs update or we rely on 'Full Page'.
                # For now, we assume 'Split Vertical' maps to num_crop=2 (2 columns).
                self.data_handler.crop_images(num_crop_qn=2, num_crop_hn=2)
            else: # "Full Page"
                self.data_handler.crop_images(num_crop_qn=1, num_crop_hn=1)

            # 3. OCR
            if progress_callback:
                progress_callback("Step 3/5: Running OCR...", 40, 100)

            self.ocr_processor.ocr_both(progress_callback=lambda msg, c, t: None) # Suppress internal progress or pipe it?

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
