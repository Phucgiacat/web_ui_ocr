"""
OCR Corrector Web UI Package
"""

__version__ = "1.0.0"
__author__ = "OCR Corrector Team"
__description__ = "Web UI for OCR Corrector - Vietnamese and Sino-Vietnamese Document Processing"

from web_ui.config_manager import ConfigManager
from web_ui.data_handler import DataHandler
from web_ui.ocr_processor import OCRProcessor

__all__ = [
    'ConfigManager',
    'DataHandler',
    'OCRProcessor',
]
