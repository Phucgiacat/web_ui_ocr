#!/usr/bin/env python3
"""
Quick Reference - OCR Corrector Web UI
Một số lệnh và mẹo nhanh
"""

QUICK_START = """
╔════════════════════════════════════════════════════════════╗
║      OCR CORRECTOR WEB UI - QUICK REFERENCE               ║
╚════════════════════════════════════════════════════════════╝

📋 INSTALLATION
═════════════════════════════════════════════════════════════

1. Cách nhanh nhất (Windows):
   cd web_ui
   setup_windows.bat
   python run.py

2. Cách nhanh nhất (Linux/macOS):
   cd web_ui
   bash setup_linux.sh
   python run.py

3. Manual:
   cd web_ui
   pip install -r requirements.txt
   streamlit run app.py

🚀 RUNNING THE APP
═════════════════════════════════════════════════════════════

python run.py
# hoặc
streamlit run app.py

App sẽ mở tại: http://localhost:8501

🔍 CHECKING ENVIRONMENT
═════════════════════════════════════════════════════════════

python check_env.py
# Kiểm tra:
# - Python version
# - Packages
# - Directories
# - Configuration

📁 IMPORTANT DIRECTORIES
═════════════════════════════════════════════════════════════

./output/              - Kết quả xử lý
./temp/                - File tạm thời  
./logs/                - Log files
./model/               - Model files
./web_ui/              - Web UI code

📄 IMPORTANT FILES
═════════════════════════════════════════════════════════════

.env                   - Configuration
before_handle_data.json - Processing info
web_ui/app.py         - Main application
web_ui/config_manager.py - Config manager
web_ui/data_handler.py   - Data handling
web_ui/ocr_processor.py  - OCR processing

🎯 6 PHASES (Thứ tự thực hiện)
═════════════════════════════════════════════════════════════

1. 📥 Trích xuất PDF
   - Upload PDF
   - Click "Bắt đầu trích xuất"
   - Chờ hoàn thành

2. ✂️ Cắt ảnh
   - Chọn cách: thường hoặc edge detection
   - Nhập tham số
   - Click "Bắt đầu cắt ảnh"

3. 👁️ OCR
   - Click "OCR Cả hai"
   - Chờ hoàn thành

4. 🔗 Align
   - Điều chỉnh threshold nếu cần
   - Click "Bắt đầu căn chỉnh"

5. ✏️ Sửa lỗi
   - Click "Bắt đầu sửa lỗi"
   - File .xlsx sẽ được tạo

6. 📊 Quản lý
   - Xem thống kê
   - Kiểm tra số trang
   - Xóa dữ liệu nếu cần

⚙️ CONFIGURATION (.env)
═════════════════════════════════════════════════════════════

OUTPUT_FOLDER=./output
NAME_FILE_INFO=before_handle_data.json
NUM_CROP_HN=1
NUM_CROP_QN=1
VI_MODEL=./model/vi
NOM_MODEL=./model/nom
TYPE_QN=1

Cập nhật các giá trị theo nhu cầu

💻 COMMAND SHORTCUTS
═════════════════════════════════════════════════════════════

# Check environment
python check_env.py

# Run app
python run.py

# Reset (Windows)
del output\\* /q
del before_handle_data.json

# Reset (Linux/macOS)
rm -rf output/*
rm before_handle_data.json

# View logs
tail -f logs/*.log

# Check Python version
python --version

# List packages
pip list | grep -E "streamlit|flask|opencv"

🐳 DOCKER COMMANDS
═════════════════════════════════════════════════════════════

# Build image
docker build -t ocr-corrector-web .

# Run container
docker run -p 8501:8501 ocr-corrector-web

# Using docker-compose
docker-compose up -d
docker-compose down

# Check logs
docker logs <container_id>

📚 DOCUMENTATION FILES
═════════════════════════════════════════════════════════════

README.md          - Quick start (3 pages)
GUIDE.md          - Detailed guide (40+ pages)
FILE_INDEX.md     - File reference (20 pages)
CHANGELOG.md      - Version history
SUMMARY.md        - Project overview
QUICK_REFERENCE.md - This file

🔧 TROUBLESHOOTING
═════════════════════════════════════════════════════════════

1. "Module not found"
   → pip install -r requirements.txt

2. "Cannot read PDF"
   → Check PDF file is valid
   → Delete old output
   → Try again

3. "No module 'Proccess_pdf'"
   → Run from ocr_corrector folder
   → Check .env paths

4. "Port 8501 already in use"
   → streamlit run app.py --server.port 8502

5. App slow
   → Check RAM (need 8GB+)
   → Reduce image size
   → Process fewer pages

6. Reset everything
   → Delete output/
   → Delete before_handle_data.json
   → Start over

📊 PARAMETERS & THRESHOLDS
═════════════════════════════════════════════════════════════

Align Threshold:
  1-10:   Cắt ngắn, chặt (high precision)
  20-30:  Cân bằng (recommended)
  50-100: Lỏng, dài (high recall)

Number of Crops:
  1: Không cắt
  2: Cắt đôi
  3: Cắt ba
  N: Cắt N phần

🎓 LEARNING RESOURCES
═════════════════════════════════════════════════════════════

Streamlit Docs: https://docs.streamlit.io
OpenCV Docs: https://docs.opencv.org
Pandas Docs: https://pandas.pydata.org
Python Docs: https://docs.python.org/3

✅ CHECKLIST - First Run
═════════════════════════════════════════════════════════════

□ Python 3.8+ installed
□ Run setup.py or setup script
□ Check .env configuration
□ Run check_env.py
□ python run.py
□ Open http://localhost:8501
□ Upload test PDF
□ Run through all 6 phases
□ Check result.xlsx

🎯 COMMON TASKS
═════════════════════════════════════════════════════════════

Process a new document:
1. Reset everything (Tab 📊 → 🗑️)
2. Upload PDF (Tab 📥)
3. Follow 6 phases in order

Process multiple pages:
1. Use large PDF
2. Adjust crop numbers in Phase 2
3. Run through phases
4. Check output/

Generate Excel:
1. Complete phases 1-4
2. Run phase 5 (Sửa lỗi)
3. Download result.xlsx

📞 GETTING HELP
═════════════════════════════════════════════════════════════

1. Check GUIDE.md (detailed help)
2. Run check_env.py (diagnose issues)
3. Check console output (error messages)
4. Check .env (configuration)
5. Check logs/ folder (log files)

🚀 NEXT STEPS
═════════════════════════════════════════════════════════════

After first successful run:
1. Test with real document
2. Adjust parameters
3. Optimize for your documents
4. Create backup of results
5. Deploy if needed (Docker)

════════════════════════════════════════════════════════════
Phiên bản: 1.0
Cập nhật: 2026-01-17
════════════════════════════════════════════════════════════
"""

if __name__ == "__main__":
    print(QUICK_START)
