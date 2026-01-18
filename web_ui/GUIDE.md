# OCR Corrector Web UI - Hướng dẫn chi tiết

## 📋 Mục lục

1. [Giới thiệu](#giới-thiệu)
2. [Yêu cầu hệ thống](#yêu-cầu-hệ-thống)
3. [Cài đặt](#cài-đặt)
4. [Sử dụng](#sử-dụng)
5. [Kiến trúc](#kiến-trúc)
6. [Khắc phục sự cố](#khắc-phục-sự-cố)

## 🎯 Giới thiệu

OCR Corrector Web UI là một công cụ web hiện đại được xây dựng với **Streamlit** để quản lý toàn bộ quy trình OCR từ trích xuất PDF đến sửa lỗi và xuất kết quả cho tài liệu Quốc Ngữ và Hán Nôm.

### Ưu điểm:
- ✅ Giao diện trực quan, dễ sử dụng
- ✅ Hỗ trợ tất cả các phase xử lý
- ✅ Theo dõi trạng thái thực tế
- ✅ Xử lý lỗi toàn diện
- ✅ Hiển thị tiến độ cho từng phase
- ✅ Quản lý dữ liệu linh hoạt

## 💻 Yêu cầu hệ thống

- **OS:** Windows / Linux / macOS
- **Python:** 3.8 hoặc cao hơn
- **RAM:** Tối thiểu 4GB (khuyến nghị 8GB+)
- **Disk:** Tối thiểu 2GB cho output
- **Internet:** Cần thiết khi tải thư viện

## 🚀 Cài đặt

### Bước 1: Cài đặt Python
Tải Python 3.8+ từ [python.org](https://www.python.org/downloads/)

### Bước 2: Clone/Tải code
```bash
# Vào thư mục web_ui
cd path/to/ocr_corrector/web_ui
```

### Bước 3: Cài đặt thư viện
```bash
# Tạo virtual environment (tùy chọn nhưng khuyến nghị)
python -m venv venv

# Kích hoạt virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Cài đặt thư viện
pip install -r requirements.txt
```

### Bước 4: Cấu hình
Kiểm tra/cập nhật file `.env` trong thư mục gốc project:
```ini
OUTPUT_FOLDER=./output
NAME_FILE_INFO=before_handle_data.json
NUM_CROP_HN=1
NUM_CROP_QN=1
VI_MODEL=./model/vi
NOM_MODEL=./model/nom
TYPE_QN=1
```

### Bước 5: Chạy ứng dụng
```bash
python run.py
```

Hoặc:
```bash
streamlit run app.py
```

Ứng dụng sẽ mở tại: **http://localhost:8501**

## 📖 Sử dụng

### 1. Trích xuất PDF (Phase 1)

**Mục đích:** Chuyển tài liệu PDF thành ảnh

**Các bước:**
1. Vào tab "📥 Trích xuất PDF"
2. Tải lên file PDF cần xử lý
3. (Tùy chọn) Nhấn "🗑️ Xóa dữ liệu cũ" nếu có dữ liệu trước
4. Nhấn "▶️ Bắt đầu trích xuất"
5. Đợi cho đến khi xuất hiện "✅ Trích xuất PDF thành công!"

**Kết quả:** 
- Folder output được tạo
- File `before_handle_data.json` chứa thông tin
- Hai thư mục ảnh: `Quoc Ngu` và `Han Nom`

### 2. Cắt ảnh (Phase 2)

**Mục đích:** Cắt ảnh thành nhiều phần nhỏ hơn

**Hai lựa chọn:**

#### A. Cắt ảnh thường
1. Vào tab "✂️ Cắt ảnh" → Tab "Cắt ảnh thường"
2. Nhập số lượng cắt:
   - **Quốc Ngữ:** Số phần cần cắt chiều ngang
   - **Hán Nôm:** Số phần cần cắt chiều ngang
3. Nhấn "▶️ Bắt đầu cắt ảnh"

#### B. Edge Detection
1. Vào tab "✂️ Cắt ảnh" → Tab "Edge Detection"
2. Chọn những phần cần xử lý
3. Nhấn "▶️ Bắt đầu xử lý"

**Lưu ý:**
- Edge Detection hoạt động tốt hơn cho các tài liệu có bóng mềm
- Cắt ảnh thường nhanh hơn nhưng có thể ít chính xác hơn

### 3. OCR - Nhận diện ký tự (Phase 3)

**Mục đích:** Chuyển ảnh thành text

**Các bước:**
1. Vào tab "👁️ OCR"
2. Chọn một trong ba tùy chọn:
   - "🔤 OCR Quốc Ngữ" - Chỉ xử lý Quốc Ngữ
   - "🈳 OCR Hán Nôm" - Chỉ xử lý Hán Nôm
   - "🔤🈳 OCR Cả hai" - Xử lý cả hai (khuyến nghị)
3. Đợi quá trình hoàn thành

**Lưu ý:**
- Đây là bước dài nhất, có thể mất vài phút
- Kết quả phụ thuộc vào chất lượng ảnh
- Cần đủ dung lượng ổ đĩa cho output

### 4. Align - Căn chỉnh (Phase 4)

**Mục đích:** Sắp xếp và so khớp text Quốc Ngữ với Hán Nôm

**Các bước:**
1. Vào tab "🔗 Align"
2. Điều chỉnh tham số Align (threshold):
   - **Giá trị thấp (5-10):** Align chặt, ít dòng
   - **Giá trị vừa (20-30):** Cân bằng
   - **Giá trị cao (50-100):** Align lỏng, nhiều dòng
3. (Tùy chọn) Bật "Đảo chiều Hán Nôm" nếu cần
4. Nhấn "▶️ Bắt đầu căn chỉnh"

**Tham số Align:**
- Threshold cao: Bỏ qua các dòng không khớp
- Threshold thấp: Cố gắng khớp tất cả dòng

### 5. Sửa lỗi (Phase 5)

**Mục đích:** Sửa lỗi OCR và tạo file Excel cuối cùng

**Các bước:**
1. Vào tab "✏️ Sửa lỗi"
2. (Tùy chọn) Bật "Chế độ Debug" để xem chi tiết
3. Nhấn "▶️ Bắt đầu sửa lỗi"
4. File Excel sẽ được tạo trong output

**Kết quả:** File `result.xlsx` chứa:
- Cột Quốc Ngữ
- Cột Hán Nôm
- Cột đánh dấu (nếu bật debug)

### 6. Quản lý (Phase 6)

**Mục đích:** Theo dõi và quản lý dữ liệu

**Tab "📈 Thống kê":**
- Xem quy trình xử lý với các phase
- Các phase xanh (🟢) = hoàn thành
- Các phase đỏ (🔴) = chưa hoàn thành

**Tab "📋 Kiểm tra":**
- Kiểm tra số trang Quốc Ngữ vs Hán Nôm
- Cảnh báo nếu số trang không bằng nhau

**Tab "🗑️ Xóa":**
- Xóa folder output để bắt đầu lại
- Xóa file thông tin
- ⚠️ Hành động này không thể hoàn tác!

## 🏗️ Kiến trúc

### Cấu trúc thư mục:
```
web_ui/
├── app.py                  # Ứng dụng Streamlit chính
├── run.py                  # Script chạy
├── setup.py                # Script cấu hình
├── requirements.txt        # Thư viện
├── README.md              # Tài liệu ngắn
├── GUIDE.md               # Hướng dẫn chi tiết (file này)
├── config_manager.py      # Quản lý cấu hình
├── data_handler.py        # Xử lý dữ liệu
├── ocr_processor.py       # Xử lý OCR
├── pages.py               # Component giao diện
├── utils.py               # Hàm tiện ích
└── .gitignore
```

### Các module chính:

#### config_manager.py
- Quản lý cấu hình từ `.env`
- Đọc/ghi thông tin JSON
- Kiểm tra trạng thái các phase

#### data_handler.py
- Trích xuất PDF
- Cắt ảnh
- Căn chỉnh tên ảnh
- Edge detection

#### ocr_processor.py
- OCR Quốc Ngữ
- OCR Hán Nôm
- Align text
- Sửa lỗi

#### app.py
- Giao diện Streamlit chính
- Quản lý các tab
- Xử lý tương tác người dùng

## 🔧 Khắc phục sự cố

### ❌ Lỗi: "Module 'X' not found"
**Nguyên nhân:** Thư viện chưa được cài đặt

**Giải pháp:**
```bash
pip install -r requirements.txt
```

### ❌ Lỗi: "Cannot read image"
**Nguyên nhân:** PDF không hợp lệ hoặc ảnh bị hỏng

**Giải pháp:**
1. Kiểm tra file PDF
2. Xóa dữ liệu cũ
3. Thử lại

### ❌ Lỗi: "No module named 'Proccess_pdf'"
**Nguyên nhân:** Đường dẫn import sai hoặc chưa configure

**Giải pháp:**
1. Đảm bảo chạy từ thư mục `ocr_corrector`
2. Kiểm tra file `.env`

### ❌ Lỗi: "File not found"
**Nguyên nhân:** Chưa hoàn thành phase trước

**Giải pháp:**
1. Kiểm tra sidebar - xem phase nào chưa xong
2. Hoàn thành các phase theo thứ tự

### ⏱️ Ứng dụng chạy chậm
**Nguyên nhân:** OCR đòi hỏi tài nguyên cao

**Giải pháp:**
1. Đảm bảo RAM đủ (8GB+)
2. Giảm kích thước ảnh
3. Giảm số lượng ảnh

### 🔄 Muốn bắt đầu lại
1. Vào tab "📊 Quản lý"
2. Tab "🗑️ Xóa"
3. Nhấn "🗑️ Xóa folder output"
4. Nhấn "🗑️ Xóa file info"

## 📊 Ví dụ thực tế

**Quy trình xử lý tài liệu Hán Nôm:**

1. ✅ Tải PDF lên (10 trang)
   - Output: 10 ảnh QN + 10 ảnh HN

2. ✅ Cắt ảnh với cắt 2x
   - Output: 20 ảnh QN + 20 ảnh HN

3. ✅ OCR cả hai
   - Output: 20 file text QN + 20 file JSON HN

4. ✅ Align với threshold=25
   - Output: 1 file result.txt

5. ✅ Sửa lỗi
   - Output: result.xlsx (20 dòng dữ liệu)

6. ✅ Xem kết quả trong Excel

## 📞 Hỗ trợ

Nếu gặp vấn đề:

1. Kiểm tra file `.env`
2. Xem log trong console
3. Kiểm tra yêu cầu hệ thống
4. Thử cài đặt lại thư viện

## 📝 Ghi chú quan trọng

- Luôn backup dữ liệu quan trọng
- Mỗi phase phải hoàn thành trước khi chuyển sang phase tiếp theo
- Có thể xóa dữ liệu và bắt đầu lại bất kỳ lúc nào
- File Excel kết quả nên được kiểm tra trước khi sử dụng

---

**Phiên bản:** 1.0  
**Cập nhật:** Tháng 1, 2026  
**Hỗ trợ:** Xem README.md hoặc liên hệ support
