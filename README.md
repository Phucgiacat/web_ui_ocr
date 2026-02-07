<p align="center">
  <img src="hcmus-logo.png" alt="Logo" width="200"/>
</p>

# OCR Corrector - Công Cụ OCR và Căn Chỉnh Hán Nôm - Quốc Ngữ

OCR Corrector là công cụ đa phương thức để căn chỉnh câu cho tài liệu song ngữ Hán Nôm - Quốc Ngữ. Hệ thống sử dụng [LASER](https://github.com/facebookresearch/LASER) embeddings và VecAlign để tìm các cặp câu tương đồng về nghĩa, kết hợp thuật toán căn chỉnh dựa trên Levenshtein để tìm ra sự căn chỉnh tối ưu.

## ✨ Tính Năng Mới (2026-01-21)

### 🚀 OCR Progress Tracking & Crash Recovery
- **Theo dõi tiến độ OCR real-time**: Xem số file đã OCR, phần trăm hoàn thành
- **Khôi phục tự động sau crash**: Tự động bỏ qua file đã OCR, tiếp tục từ file mới
- **Tách ảnh đã OCR**: Tổ chức file thành 2 thư mục rõ ràng (image/ và ocr/)
- **Giao diện Streamlit trực quan**: Buttons và metrics dễ sử dụng

📚 **Xem thêm:** [START_OCR_PROGRESS_TRACKING.md](START_OCR_PROGRESS_TRACKING.md) | [README_OCR_PROGRESS.md](README_OCR_PROGRESS.md) 

## 📋 Mục Lục

- [Tính Năng Mới](#-tính-năng-mới-2026-01-21)
- [Cài Đặt Môi Trường](#-cài-đặt-môi-trường)
- [Cấu Hình .env](#-cấu-hình-env)
- [Cách Sử Dụng](#-cách-sử-dụng)
  - [Phương Pháp 1: Streamlit Web UI (Khuyến Nghị)](#phương-pháp-1-streamlit-web-ui-khuyến-nghị-)
  - [Phương Pháp 2: Command Line](#phương-pháp-2-command-line)
- [Tính Năng OCR Progress Tracking](#-tính-năng-ocr-progress-tracking)
- [Cấu Trúc Thư Mục](#-cấu-trúc-thư-mục)
- [Troubleshooting](#-troubleshooting)

---

## 🛠️ Cài Đặt Môi Trường

## ✅ Chạy nhanh sau khi clone (Khuyến nghị)

Chạy từ thư mục gốc của repo:

```bash
# 1) Tạo file cấu hình môi trường
copy .env.example .env

# 2) Cài đặt dependencies và tạo thư mục cần thiết
python web_ui/setup.py

# 3) Chạy Web UI
python web_ui/run.py
```

> Lưu ý: File `.env` không được đưa lên GitHub. Hãy chỉnh sửa `.env` theo môi trường của bạn.

If you haven't already check out the repository:
```bash
https://github.com/davidle2810/nom_ocr_corrector.git
cd nom_ocr_corrector
```

The environment can be built using the provided environment.yml file:
```bash
conda env create -f environment.yml
conda activate ocr_corrector
python -m laserembeddings download-models
```

---

## ⚙️ Cấu Hình .env
```
NOM_SIMILARITY_DICTIONARY = dict\SinoNom_similar_Dic_v2.xlsx
QN2NOM_DICTIONARY = dict\QuocNgu_SinoNom_Dic.xlsx

SN_DOMAIN = tools.clc.hcmus.edu.vn

OUTPUT_FOLDER = Output
GOOGLE_APPLICATION_CREDENTIALS = 
LOG_DIR = vi_ocr/logs
SYLLABLE = model\tokenization\syllable.txt

NAME_FILE_INFO = before_handle_data.json

NUM_CROP_QN = 1
NUM_CROP_HN = 1

VI_MODEL = model\vi\best.pt
NOM_MODEL = model\nom\best_v2.pt

TYPE_QN = 2 
```

**Giải thích các tham số:**
- `NUM_CROP_QN`: Chia 1 trang thành n trang con cho phần Quốc Ngữ
- `NUM_CROP_HN`: Chia 1 trang thành n trang con cho phần Hán Nôm
- `TYPE_QN`: Kiểu tô màu (0: không màu, 1: highlight âm tiết không có trong danh sách, 2: màu theo ký tự Hán Nôm tương ứng)

---

## 🚀 Cách Sử Dụng

### Phương Pháp 1: Streamlit Web UI (Khuyến Nghị) ⭐

**Cách chạy:**
```bash
# Activate virtual environment
.venv\Scripts\Activate.ps1

# Chạy ứng dụng Streamlit
python -m streamlit run web_ui/app.py --server.port 8503

# Hoặc dùng script launch
.\launch_windows.ps1
```

**Truy cập:** Mở trình duyệt tại `http://localhost:8503`

#### 📱 Giao Diện Web UI

**Tab 1: 📄 Extract PDF**
- Upload file PDF
- Extract trang thành ảnh
- Tách Quốc Ngữ và Hán Nôm

**Tab 2: ✂️ Crop Ảnh**
- Crop ảnh Quốc Ngữ (tùy chọn)
- Crop ảnh Hán Nôm (khuyến nghị)
- Cài đặt số lượng cắt

**Tab 3: 🈳 OCR Hán Nôm**
- OCR Quốc Ngữ
- OCR Hán Nôm
- **🆕 Theo dõi tiến độ OCR**
  - Click **🔄 Cập nhật tiến độ** để xem:
    - Số file đã OCR / Tổng số file
    - Phần trăm hoàn thành
    - File tiếp theo cần xử lý
  - Click **📦 Tách ảnh đã OCR** để tổ chức file

**Tab 4: 🔗 Align**
- Căn chỉnh text Hán Nôm - Quốc Ngữ
- Cấu hình tham số k (1: dọc, 2: có mapping)
- Upload file mapping (nếu k=2)

**Tab 5: ✏️ Sửa Lỗi**
- Chạy correction và tạo Excel
- Đánh dấu lỗi tự động

**Tab 6: ⚙️ Settings**
- Cấu hình OCR Hán Nôm (ocr_id, lang_type, epitaph)
- Quản lý config file

**Tab 7: 📊 Debug**
- Xem thông tin hệ thống
- Debug và logs

---

### Phương Pháp 2: Command Line

#### Bước 1: Extract PDF
```bash
python handle_data.py --input "data/truyen_cac_thanh.pdf"
```

#### Bước 2: Crop Ảnh (Tùy chọn)
```bash
# crop_qn crop_hn
python handle_data.py --crop false true
```

#### Bước 3: Đánh Số Index (Bắt buộc)
```bash
# reverse: true/false
python handle_data.py --align_number_reverse true
```

#### Bước 4: OCR
```bash
# ocr_qn ocr_hn
python ocr_corrector.py --ocr true true
```

#### Bước 5: Align
```bash
# k: tham số align (1=dọc, 4=ngang)
python ocr_corrector.py --align 1
```

#### Bước 6: Correction
```bash
python ocr_corrector.py --corrector false
```

---

## 🎯 Tính Năng OCR Progress Tracking

### Tính Năng Chính

#### 1️⃣ Theo Dõi Tiến Độ
```
Trong Web UI → Tab 🈳 OCR Hán Nôm
Click: 🔄 Cập nhật tiến độ

Hiển thị:
├─ Đã OCR: 150 file
├─ Tổng cộng: 500 file
├─ Tiến độ: 30%
├─ [Progress Bar]
└─ Tiếp theo: image_151.jpg
```

#### 2️⃣ Khôi Phục Sau Crash
```
Khi OCR bị crash:
1. Click "🔄 Cập nhật tiến độ" để xem đã làm được bao nhiêu
2. Click "🈳 OCR Hán Nôm" lại
3. Hệ thống tự động:
   - Bỏ qua file đã OCR
   - Tiếp tục từ file mới
   - ✅ Khôi phục thành công!
```

#### 3️⃣ Tách Ảnh Đã OCR
```
Click: 📦 Tách ảnh đã OCR

Kết quả:
output_folder/extracted/
├── image/     (ảnh gốc đã OCR)
└── ocr/       (file .json tương ứng)

---

## ⚙️ Cấu Hình Rate Limiting

### Tạo file `.env` để tùy chỉnh delay và retry:

```env
# ===== DELAY CONFIGURATION =====
DELAY_BEFORE_UPLOAD=2      # Delay trước khi upload (giây)
DELAY_AFTER_UPLOAD=3       # Delay sau khi upload (giây)
DELAY_BEFORE_DOWNLOAD=2    # Delay trước khi download (giây)
DELAY_BETWEEN_FILES=3      # Delay giữa các file (giây)

# ===== RETRY CONFIGURATION =====
OCR_MAX_RETRIES=3          # Số lần thử lại tối đa
INITIAL_RETRY_DELAY=5      # Delay ban đầu khi retry (giây)
MAX_RETRY_DELAY=60         # Delay tối đa (giây)

# ===== CIRCUIT BREAKER =====
MAX_CONSECUTIVE_FAILURES=5           # Số lỗi liên tiếp trước khi dừng
CIRCUIT_BREAKER_COOLDOWN=30          # Thời gian cooldown (giây)

# ===== ADAPTIVE DELAY =====
ENABLE_ADAPTIVE_DELAY=true           # Bật/tắt adaptive delay
ADAPTIVE_DELAY_MULTIPLIER=1.0        # Hệ số điều chỉnh ban đầu
```

### 5 Chiến Lược Tránh Rate Limiting:

1. ⏰ **Exponential Backoff** - Tăng delay khi lỗi (5s → 60s)
2. 🔌 **Circuit Breaker** - Dừng 30s sau 5 lỗi liên tiếp  
3. 📊 **Adaptive Delay** - Tự điều chỉnh delay (1.0× → 3.0×)
4. 🕒 **Multi-Phase Delays** - Delay tại 4 điểm (upload, OCR, download, between)
5. 🔁 **Retry Mechanism** - Thử lại 3 lần với exponential backoff

📚 **Xem chi tiết:** [RATE_LIMITING_STRATEGY.md](RATE_LIMITING_STRATEGY.md)

---
```

### Tài Liệu Chi Tiết

- **Quick Start (2 min):** [START_OCR_PROGRESS_TRACKING.md](START_OCR_PROGRESS_TRACKING.md)
- **Hướng dẫn đầy đủ (15 min):** [OCR_PROGRESS_TRACKING_GUIDE.md](OCR_PROGRESS_TRACKING_GUIDE.md)
- **Code examples:** [CODE_EXAMPLES.md](CODE_EXAMPLES.md)
- **Kỹ thuật:** [TECHNICAL_IMPLEMENTATION.md](TECHNICAL_IMPLEMENTATION.md)

---

## 📁 Cấu Trúc Thư Mục

```
ocr_corrector/
├── align/                    # Module căn chỉnh
├── dict/                     # Từ điển Hán Nôm
├── model/                    # Models OCR
│   ├── nom/                  # Model Hán Nôm
│   ├── vi/                   # Model Quốc Ngữ
│   └── tokenization/         # Syllable tokenizer
├── nom_ocr/                  # Module OCR Hán Nôm
├── vi_ocr/                   # Module OCR Quốc Ngữ
├── Proccess_pdf/             # Module xử lý PDF
├── web_ui/                   # Streamlit Web UI
│   ├── app.py               # Main app
│   ├── config_manager.py    # Config management
│   ├── data_handler.py      # Data handling
│   ├── ocr_processor.py     # OCR processing
│   └── pages.py             # UI pages
├── output/                   # Thư mục output
│   └── extracted/           # Ảnh đã tách (mới)
│       ├── image/           # Ảnh gốc
│       └── ocr/             # File JSON
├── requirements.txt         # Python packages
├── environment.yml          # Conda environment
├── .env                     # Environment variables
└── before_handle_data.json  # Config file

📚 Documentation:
├── README.md                              # Bạn đang đọc
├── START_OCR_PROGRESS_TRACKING.md         # Quick start (2 min)
├── README_OCR_PROGRESS.md                 # OCR Progress guide
├── QUICK_REFERENCE_OCR_PROGRESS.md        # Quick reference
├── OCR_PROGRESS_TRACKING_GUIDE.md         # Hướng dẫn đầy đủ
├── TECHNICAL_IMPLEMENTATION.md            # Chi tiết kỹ thuật
├── CODE_EXAMPLES.md                       # Code examples
├── VISUAL_DIAGRAMS.md                     # Biểu đồ
├── DOCUMENTATION_INDEX.md                 # Chỉ mục tài liệu
└── FINAL_DELIVERY_REPORT.md              # Báo cáo hoàn thành
```

---

## 🐛 Troubleshooting

### Vấn đề 1: OCR Crash
**Giải pháp:**
1. Click "🔄 Cập nhật tiến độ" để xem đã OCR bao nhiêu
2. Click "🈳 OCR Hán Nôm" lại để tiếp tục
3. Hệ thống tự động bỏ qua file đã xử lý

### Vấn đề 2: Không thấy tiến độ OCR
**Giải pháp:**
- Click nút "🔄 Cập nhật tiến độ" trong tab OCR Hán Nôm
- Kiểm tra thư mục `output/ocr/Han_Nom_ocr/` có file `.json` không

### Vấn đề 3: Module import error
**Giải pháp:**
```bash
# Chạy từ thư mục gốc ocr_corrector
cd d:\learning\C.VAnh\tool\ocr_corrector
python -m streamlit run web_ui/app.py --server.port 8503
```

### Vấn đề 4: Thiếu dependencies
**Giải pháp:**
```bash
conda activate ocr_corrector
pip install -r requirements.txt
```

---

## 📊 Workflow Tổng Quan

```
1. Extract PDF
   ↓
2. Crop ảnh (nếu cần)
   ↓
3. OCR Hán Nôm & Quốc Ngữ
   ├─ 🔄 Theo dõi tiến độ
   ├─ 🔄 Khôi phục nếu crash
   └─ 📦 Tách ảnh khi xong
   ↓
4. Align text
   ↓
5. Correction & Export Excel
   ↓
6. ✅ Hoàn thành!
```

---

## 🎓 Quick Start (5 Phút)

```bash
# 1. Activate environment
.venv\Scripts\Activate.ps1

# 2. Chạy Streamlit
python -m streamlit run web_ui/app.py --server.port 8503

# 3. Truy cập http://localhost:8503

# 4. Làm theo các tab từ trái qua phải:
#    Extract PDF → Crop → OCR → Align → Sửa lỗi

# 5. Sử dụng tính năng mới:
#    - 🔄 Cập nhật tiến độ: Xem progress
#    - 📦 Tách ảnh: Organize files
```

---

## 📞 Support & Documentation

- **Hướng dẫn nhanh:** [README_OCR_PROGRESS.md](README_OCR_PROGRESS.md)
- **Hướng dẫn đầy đủ:** [OCR_PROGRESS_TRACKING_GUIDE.md](OCR_PROGRESS_TRACKING_GUIDE.md)
- **Code examples:** [CODE_EXAMPLES.md](CODE_EXAMPLES.md)
- **Troubleshooting:** Xem section trên hoặc [QUICK_REFERENCE_OCR_PROGRESS.md](QUICK_REFERENCE_OCR_PROGRESS.md)

---

## ✅ Checklist Sử Dụng

- [ ] Đã cài đặt môi trường (conda/venv)
- [ ] Đã cấu hình file `.env`
- [ ] Đã chạy Streamlit app
- [ ] Đã extract PDF thành công
- [ ] Đã OCR (có thể dùng progress tracking)
- [ ] Đã align text
- [ ] Đã export kết quả

---

## 🆕 What's New (2026-01-21)

✨ **OCR Progress Tracking Features:**
- Real-time progress monitoring
- Automatic crash recovery
- Image extraction & organization
- Comprehensive documentation (2,700+ lines)

📚 **New Documentation:**
- 11 comprehensive guides
- 10+ code examples
- 10 detailed diagrams
- Quick references & troubleshooting

🔧 **Code Updates:**
- `nom_ocr/nom_ocr.py` - Progress tracking functions
- `web_ui/ocr_processor.py` - Progress & extract methods
- `web_ui/app.py` - New UI sections with buttons

---

**Version:** 1.1.0  
**Last Updated:** 2026-01-21  
**Status:** Production Ready ✅

***Note: Going through each step carefully will lead to better results.***


