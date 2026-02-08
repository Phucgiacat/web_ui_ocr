import pandas as pd
import numpy as np
import requests
import json
import os
from typing import List, Dict, Any, Optional
import time

class LLMProcessor:
    """
    Handles interaction with LLMs (e.g., via Hugging Face Inference API)
    for data cleaning and processing.
    """
    def __init__(self, api_token: Optional[str] = None, model_id: str = "meta-llama/Llama-2-7b-chat-hf"):
        self.api_token = api_token
        self.model_id = model_id
        self.api_url = f"https://api-inference.huggingface.co/models/{model_id}"
        self.headers = {"Authorization": f"Bearer {api_token}"} if api_token else {}

    def query_hf_api(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Send request to HF Inference API"""
        if not self.api_token:
            # Mock response if no token provided
            time.sleep(0.5)
            return [{"generated_text": "Mock: Corrected data based on heuristic."}]

        try:
            response = requests.post(self.api_url, headers=self.headers, json=payload)
            return response.json()
        except Exception as e:
            return {"error": str(e)}

    def clean_text_batch(self, texts: List[str], context: str = "OCR correction") -> List[str]:
        """
        Process a batch of texts to clean/correct them.
        """
        cleaned_texts = []
        for text in texts:
            if not text or pd.isna(text):
                cleaned_texts.append("")
                continue

            # Construct prompt based on context
            prompt = f"""
            Task: Correct OCR errors in the following Vietnamese/Han-Nom text.
            Context: {context}
            Input: "{text}"
            Output (only the corrected text):
            """

            # Call API (or mock)
            # For demo, we'll use a simple heuristic if no token, or specific logic
            if not self.api_token:
                # Simple mock correction: remove extra spaces, fix common OCR glitches
                corrected = " ".join(text.split())
                cleaned_texts.append(corrected)
            else:
                result = self.query_hf_api({"inputs": prompt})
                if isinstance(result, list) and "generated_text" in result[0]:
                    cleaned_texts.append(result[0]["generated_text"].replace(prompt, "").strip())
                else:
                    cleaned_texts.append(text) # Fallback

        return cleaned_texts

    def align_bilingual_data(self, nom_list: List[str], vi_list: List[str]) -> List[Dict[str, str]]:
        """
        Smartly align Sino-Vietnamese (Nom) and Vietnamese (Quoc Ngu) lists.
        Handles mismatches in length and alignment errors.
        """
        # Simple heuristic alignment if no API token
        if not self.api_token:
            min_len = min(len(nom_list), len(vi_list))
            aligned_data = []
            for i in range(min_len):
                aligned_data.append({
                    "Han_Nom": nom_list[i],
                    "Quoc_Ngu": vi_list[i],
                    "Confidence": "Mock (Heuristic)"
                })
            return aligned_data

        # LLM-based alignment logic
        # We process in chunks to fit context window
        aligned_data = []
        chunk_size = 5

        # Prepare data structure for the prompt
        nom_chunks = [nom_list[i:i + chunk_size] for i in range(0, len(nom_list), chunk_size)]
        vi_chunks = [vi_list[i:i + chunk_size] for i in range(0, len(vi_list), chunk_size)]

        # Determine how many chunks we can reasonably process (using min length)
        # Note: This is a simplified logic. A real robust pipeline would handle sliding windows.
        min_chunks = min(len(nom_chunks), len(vi_chunks))

        for i in range(min_chunks):
            n_chunk = nom_chunks[i]
            v_chunk = vi_chunks[i]

            prompt = f"""
            Task: Align the following two lists of sentences. List A is Sino-Vietnamese (Han-Nom), List B is Vietnamese (Quoc Ngu).
            Match them sentence by sentence based on meaning and phonetics.

            List A (Han-Nom):
            {json.dumps(n_chunk, ensure_ascii=False)}

            List B (Quoc Ngu):
            {json.dumps(v_chunk, ensure_ascii=False)}

            Output strictly a JSON list of objects with keys: "Han_Nom", "Quoc_Ngu".
            """

            result = self.query_hf_api({"inputs": prompt})

            try:
                if isinstance(result, list) and "generated_text" in result[0]:
                    generated = result[0]["generated_text"].replace(prompt, "").strip()
                    # Find JSON in the output
                    start = generated.find('[')
                    end = generated.rfind(']') + 1
                    if start != -1 and end != -1:
                        parsed = json.loads(generated[start:end])
                        aligned_data.extend(parsed)
                    else:
                        # Fallback if JSON parsing fails
                        for n, v in zip(n_chunk, v_chunk):
                            aligned_data.append({"Han_Nom": n, "Quoc_Ngu": v, "Confidence": "Low (Parse Error)"})
                else:
                    # Fallback API failure
                    for n, v in zip(n_chunk, v_chunk):
                        aligned_data.append({"Han_Nom": n, "Quoc_Ngu": v, "Confidence": "Low (API Error)"})
            except Exception as e:
                print(f"Alignment error: {e}")
                for n, v in zip(n_chunk, v_chunk):
                    aligned_data.append({"Han_Nom": n, "Quoc_Ngu": v, "Confidence": "Low (Exception)"})

        return aligned_data

class AIAnalyst:
    """
    Analyzes data quality and manages the AI cleaning pipeline.
    """
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.df = None
        self.load_data()

    def load_data(self):
        """Load data from Excel or CSV"""
        try:
            if self.file_path.endswith('.xlsx') or self.file_path.endswith('.xls'):
                self.df = pd.read_excel(self.file_path)
            elif self.file_path.endswith('.csv'):
                self.df = pd.read_csv(self.file_path)
            elif self.file_path.endswith('.txt'):
                # Try reading as tab-delimited or line-based
                try:
                    self.df = pd.read_csv(self.file_path, sep='\t')
                except:
                    with open(self.file_path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                    self.df = pd.DataFrame({'text': [l.strip() for l in lines]})
        except Exception as e:
            print(f"Error loading data: {e}")
            self.df = pd.DataFrame()

    def get_statistics(self) -> Dict[str, Any]:
        """Get basic statistics of the dataframe"""
        if self.df is None or self.df.empty:
            return {}

        stats = {
            "rows": len(self.df),
            "columns": list(self.df.columns),
            "missing_values": self.df.isnull().sum().to_dict(),
            "duplicates": self.df.duplicated().sum(),
        }

        # Specific stats if 'confidence' or similar columns exist
        if 'confidence' in self.df.columns:
            stats['avg_confidence'] = self.df['confidence'].mean()
            stats['low_confidence_rows'] = len(self.df[self.df['confidence'] < 0.8])

        return stats

    def run_cleaning_pipeline(self, target_columns: List[str], llm_processor: LLMProcessor) -> pd.DataFrame:
        """
        Run the cleaning pipeline on specific columns using LLM.
        """
        if self.df is None or self.df.empty:
            return pd.DataFrame()

        cleaned_df = self.df.copy()

        for col in target_columns:
            if col not in cleaned_df.columns:
                continue

            # Get unique values to save tokens (optional optimization)
            unique_vals = cleaned_df[col].unique()
            cleaned_vals = llm_processor.clean_text_batch(list(unique_vals))
            mapping = dict(zip(unique_vals, cleaned_vals))

            cleaned_df[f"{col}_cleaned"] = cleaned_df[col].map(mapping)

        return cleaned_df

    def save_cleaned_data(self, df: pd.DataFrame, output_path: str):
        """Save the cleaned dataframe"""
        if output_path.endswith('.xlsx'):
            df.to_excel(output_path, index=False)
        else:
            df.to_csv(output_path, index=False)
