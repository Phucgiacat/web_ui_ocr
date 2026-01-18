import inspect
from nom_ocr.nom_ocr import nom_ocr
from nom_ocr.ocr_client import OCR
print('nom_ocr signature:', inspect.signature(nom_ocr))
print('OCR.ocr signature:', inspect.signature(OCR.ocr))
