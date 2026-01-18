# 📄 OCR Corrector Web UI - File Index

## 📂 Cấu trúc thư mục

```
web_ui/
├── Core Files (Các file lõi)
│   ├── app.py                  ⭐ Ứng dụng Streamlit chính
│   ├── run.py                  🚀 Script chạy ứng dụng
│   ├── setup.py                ⚙️  Script setup
│   ├── check_env.py            🔍 Kiểm tra môi trường
│   └── __init__.py             📦 Python package init
│
├── Business Logic (Logic xử lý)
│   ├── config_manager.py       ⚙️  Quản lý cấu hình
│   ├── data_handler.py         📥 Xử lý dữ liệu PDF/ảnh
│   ├── ocr_processor.py        👁️  Xử lý OCR/Align/Sửa lỗi
│   ├── pages.py                📄 Component giao diện
│   └── utils.py                🛠️  Hàm tiện ích
│
├── Configuration (Cấu hình)
│   ├── requirements.txt        📦 Thư viện Python
│   ├── .streamlit/
│   │   └── config.toml        ⚙️  Cấu hình Streamlit
│   ├── .gitignore             🚫 Git ignore
│   └── Dockerfile             🐳 Docker configuration
│
├── Documentation (Tài liệu)
│   ├── README.md              📖 Tài liệu ngắn
│   ├── GUIDE.md               📕 Hướng dẫn chi tiết
│   ├── FILE_INDEX.md          📑 File index này
│   ├── docker-compose.yml     🐳 Docker compose
│   └── CHANGELOG.md           📝 Lịch sử thay đổi
│
├── Setup Scripts (Script cài đặt)
│   ├── setup_windows.bat       💻 Setup Windows
│   ├── setup_linux.sh          🐧 Setup Linux/macOS
│   └── setup.py                ⚙️  Python setup
│
└── Runtime
    ├── .streamlit/            ⚙️  Runtime config
    └── logs/                  📝 Log files (tạo khi chạy)
```

## 📄 Chi tiết từng file

### Core Application Files

#### `app.py` ⭐
- **Mục đích:** Ứng dụng Streamlit chính
- **Chức năng:**
  - Giao diện web với các tab
  - Quản lý state và session
  - Xử lý user interaction
- **Kích thước:** ~600 dòng
- **Phụ thuộc:** Streamlit, config_manager, data_handler, ocr_processor

#### `run.py` 🚀
- **Mục đích:** Entry point để chạy ứng dụng
- **Chức năng:**
  - Khởi chạy Streamlit
  - Hiển thị hướng dẫn
- **Kích thước:** ~30 dòng
- **Cách dùng:** `python run.py`

#### `setup.py` ⚙️
- **Mục đích:** Cài đặt một lần
- **Chức năng:**
  - Kiểm tra Python version
  - Tạo thư mục
  - Cài đặt thư viện
- **Kích thước:** ~70 dòng

#### `check_env.py` 🔍
- **Mục đích:** Kiểm tra môi trường trước khi chạy
- **Chức năng:**
  - Kiểm tra Python
  - Kiểm tra package
  - Kiểm tra file cấu hình
  - Kiểm tra folder
- **Kích thước:** ~200 dòng
- **Cách dùng:** `python check_env.py`

### Business Logic Files

#### `config_manager.py` ⚙️
- **Mục đích:** Quản lý cấu hình hệ thống
- **Lớp chính:** `ConfigManager`
- **Phương thức:**
  - `read_info()` - Đọc thông tin từ JSON
  - `write_info()` - Ghi thông tin vào JSON
  - `get_status()` - Lấy trạng thái các phase
  - `clear_output_folder()` - Xóa output
- **Kích thước:** ~80 dòng

#### `data_handler.py` 📥
- **Mục đích:** Xử lý dữ liệu từ PDF đến ảnh
- **Lớp chính:** `DataHandler`
- **Phương thức:**
  - `extract_pdf()` - Trích xuất PDF
  - `crop_images()` - Cắt ảnh
  - `crop_folder()` - Cắt folder ảnh
  - `edge_detection_crop()` - Cắt bằng edge detection
  - `align_images()` - Căn chỉnh ảnh
  - `check_num_pages()` - Kiểm tra số trang
- **Kích thước:** ~220 dòng

#### `ocr_processor.py` 👁️
- **Mục đích:** Xử lý OCR, Align, Sửa lỗi
- **Lớp chính:** `OCRProcessor`
- **Phương thức:**
  - `ocr_quoc_ngu()` - OCR Quốc Ngữ
  - `ocr_han_nom()` - OCR Hán Nôm
  - `ocr_both()` - OCR cả hai
  - `align_text()` - Align text
  - `correct_text()` - Sửa lỗi
- **Kích thước:** ~150 dòng

#### `pages.py` 📄
- **Mục đích:** Component giao diện Streamlit
- **Lớp chính:** `PageManager`
- **Phương thức:**
  - `render_status_indicator()` - Hiển thị trạng thái
  - `render_progress_section()` - Hiển thị progress
- **Kích thước:** ~60 dòng

#### `utils.py` 🛠️
- **Mục đích:** Hàm tiện ích chung
- **Hàm chính:**
  - `create_default_env()` - Tạo .env mặc định
  - `ensure_directories()` - Tạo thư mục
  - `format_file_size()` - Định dạng kích thước
  - `get_file_info()` - Lấy thông tin file
  - `validate_pdf()` - Kiểm tra PDF
- **Kích thước:** ~80 dòng

### Configuration Files

#### `requirements.txt` 📦
- Streamlit v1.28.1
- Flask v3.0.0
- OpenCV
- Pandas, NumPy
- PDF processing libraries
- Tổng cộng: ~18 packages

#### `.streamlit/config.toml` ⚙️
- Cấu hình theme (color, font)
- Cấu hình client
- Cấu hình server
- Cấu hình logger

#### `.gitignore` 🚫
- `__pycache__/`
- `venv/`
- `.venv/`
- `output/`
- `temp/`
- `logs/`
- `*.xlsx`, `*.json`, `*.txt`

### Documentation Files

#### `README.md` 📖
- Tài liệu ngắn gọn
- Hướng dẫn cài đặt nhanh
- Cách sử dụng cơ bản
- Cấu trúc thư mục

#### `GUIDE.md` 📕
- Hướng dẫn chi tiết 40+ trang
- Mô tả từng phase
- Ví dụ thực tế
- Khắc phục sự cố

#### `FILE_INDEX.md` 📑
- File này
- Index tất cả file
- Mô tả chi tiết mỗi file

### Setup Scripts

#### `setup_windows.bat` 💻
- Tạo virtual environment
- Cài đặt thư viện
- Tạo thư mục cần thiết
- Hướng dẫn chạy

#### `setup_linux.sh` 🐧
- Phiên bản Linux/macOS
- Hoạt động giống setup_windows.bat

### Docker Files

#### `Dockerfile` 🐳
- Base: Python 3.9-slim
- Install dependencies
- Setup Streamlit
- Port: 8501

#### `docker-compose.yml` 🐳
- Service definition
- Volume mounting
- Port mapping
- Health check

## 🔄 Luồng dữ liệu

```
app.py
  ├── config_manager.py (quản lý cấu hình)
  ├── data_handler.py (xử lý PDF/ảnh)
  ├── ocr_processor.py (xử lý OCR)
  ├── pages.py (component UI)
  └── utils.py (tiện ích)
       │
       └── Parent modules:
           ├── Proccess_pdf/
           ├── vi_ocr/
           ├── nom_ocr/
           └── align/
```

## 📊 Thống kê code

| File | Dòng | Loại |
|------|------|------|
| app.py | ~700 | Core |
| data_handler.py | ~220 | Logic |
| ocr_processor.py | ~150 | Logic |
| config_manager.py | ~80 | Config |
| utils.py | ~80 | Utility |
| pages.py | ~60 | UI |
| Tổng | ~1,300 | |

## 🚀 Cách bắt đầu

### Lần đầu tiên
```bash
cd web_ui
python setup.py
```

### Kiểm tra môi trường
```bash
python check_env.py
```

### Chạy ứng dụng
```bash
python run.py
```

## 🔗 Quan hệ giữa các file

```
User
  ↓
app.py (Giao diện)
  ├→ config_manager.py → .env, JSON file
  ├→ data_handler.py → Proccess_pdf, cv2
  ├→ ocr_processor.py → vi_ocr, nom_ocr, align
  ├→ pages.py → Streamlit components
  └→ utils.py → Utility functions
```

## 📝 Naming Convention

- **File:** `snake_case.py`
- **Class:** `PascalCase`
- **Function:** `snake_case()`
- **Variable:** `snake_case`
- **Constant:** `UPPER_CASE`

## 🔐 File Permissions

- `setup_windows.bat` - Executable
- `setup_linux.sh` - Executable (chmod +x)
- `*.py` - Read/Execute

## 💾 Backup Important Files

- `.env` - Cấu hình
- `before_handle_data.json` - Thông tin xử lý
- `output/` - Kết quả xử lý

---

**Phiên bản:** 1.0  
**Cập nhật:** Tháng 1, 2026
