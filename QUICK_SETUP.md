# ⚡ Quick Setup Guide - OCR Corrector

## 🚀 Cài Đặt Một Lần (First Time)

### Option 1: Sử dụng Setup Script (Khuyến nghị)
```bash
cd d:\learning\C.VAnh\tool\ocr_corrector
python web_ui/setup.py
```

### Option 2: Manual Install
```bash
cd d:\learning\C.VAnh\tool\ocr_corrector
pip install -r requirements.txt --upgrade
```

## 🎯 Chạy Ứng Dụng

### Từ thư mục gốc (ocr_corrector):
```bash
cd d:\learning\C.VAnh\tool\ocr_corrector
python -m streamlit run web_ui/app.py --server.port 8503
```

### Hoặc từ thư mục web_ui:
```bash
cd d:\learning\C.VAnh\tool\ocr_corrector\web_ui
streamlit run app.py
```

Mở browser và truy cập: **http://localhost:8503**

---

## ✅ Kiểm Tra Cài Đặt

Để kiểm tra xem tất cả imports có hoạt động không:
```bash
cd d:\learning\C.VAnh\tool\ocr_corrector
python test_imports.py
```

Kết quả:
```
[1] Testing: from Proccess_pdf.extract_page import ExtractPages
✅ SUCCESS: ExtractPages imported

[2] Testing: from Proccess_pdf.edge_detection import EdgeDetection
✅ SUCCESS: EdgeDetection imported

[3] Checking required dependencies...
✅ google.cloud.vision is installed
✅ ultralytics is installed
✅ cv2 is installed
✅ fitz is installed
```

---

## 📦 Dependencies Chính

| Package | Purpose | Version |
|---------|---------|---------|
| streamlit | Web UI | >=1.28.0 |
| opencv-python | Image Processing | >=4.8.0 |
| PyMuPDF (fitz) | PDF Rendering | >=1.23.0 |
| pypdf | PDF Reading | >=3.17.0 |
| google-cloud-vision | OCR API | >=3.4.0 |
| ultralytics | YOLOv8 (Edge Detection) | >=8.0.0 |
| torch, torchvision | Model Inference | >=2.0.0 |
| pandas | Data Processing | >=2.0.0 |
| tqdm | Progress Bar | >=4.65.0 |

---

## 🔧 Troubleshooting

### Lỗi: "No module named 'X'"
**Giải pháp:** Cài lại requirements
```bash
pip install -r requirements.txt --upgrade
```

### Lỗi: "Could not import Proccess_pdf"
**Kiểm tra:**
1. Đảm bảo chạy từ thư mục gốc (ocr_corrector)
2. Kiểm tra import: `python test_imports.py`

### Lỗi: Google Cloud Vision API
**Cần:**
1. Cài package: `pip install google-cloud-vision`
2. Setup credentials (xem GUIDE.md)

### Lỗi: Port 8503 bị dùng
**Giải pháp:** Dùng port khác
```bash
python -m streamlit run web_ui/app.py --server.port 8504
```

---

## 📝 Note

- Requirements.txt có tất cả dependencies cần thiết
- Không cần tải đi tải lại gì nữa nếu dùng setup script
- Lần chạy sau chỉ cần: `python -m streamlit run web_ui/app.py`
