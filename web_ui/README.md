# OCR Corrector - Web UI

Công cụ web hiện đại để chạy các phase của OCR Corrector cho tài liệu Quốc Ngữ và Hán Nôm.

## 🌟 Tính năng

- ✅ **Trích xuất PDF** - Chuyển PDF thành ảnh
- ✅ **Cắt ảnh** - Cắt ảnh bằng 2 phương pháp: thường và Edge Detection
- ✅ **OCR** - Nhận diện ký tự cho Quốc Ngữ và Hán Nôm
- ✅ **Align** - Căn chỉnh và sắp xếp text
- ✅ **Sửa lỗi** - Sửa lỗi OCR và tạo file Excel
- ✅ **Quản lý** - Theo dõi trạng thái và quản lý dữ liệu

## 📋 Yêu cầu

- Python 3.8+
- Các thư viện được liệt kê trong `requirements.txt`

## 🚀 Cài đặt

### 1. Cài đặt thư viện

```bash
cd web_ui
pip install -r requirements.txt
```

### 2. Chạy ứng dụng

```bash
python run.py
```

Hoặc trực tiếp:

```bash
streamlit run app.py
```

Ứng dụng sẽ mở trên: **http://localhost:8501**

## 📁 Cấu trúc thư mục

```
web_ui/
├── app.py                  # Ứng dụng Streamlit chính
├── run.py                  # Script chạy ứng dụng
├── requirements.txt        # Các thư viện cần thiết
├── config_manager.py       # Quản lý cấu hình
├── data_handler.py         # Xử lý dữ liệu PDF & ảnh
├── ocr_processor.py        # Xử lý OCR & Align
└── README.md              # Tài liệu này
```

## 🎯 Quy trình sử dụng

### Bước 1: Trích xuất PDF
- Chọn tab "📥 Trích xuất PDF"
- Tải lên file PDF
- Nhấn "Bắt đầu trích xuất"

### Bước 2: Cắt ảnh
- Chọn tab "✂️ Cắt ảnh"
- Chọn số lượng cắt cho Quốc Ngữ và Hán Nôm
- Hoặc sử dụng Edge Detection
- Nhấn "Bắt đầu cắt ảnh"

### Bước 3: OCR
- Chọn tab "👁️ OCR"
- Nhấn "OCR Quốc Ngữ", "OCR Hán Nôm", hoặc "OCR Cả hai"

### Bước 4: Align
- Chọn tab "🔗 Align"
- Điều chỉnh tham số Align nếu cần
- Nhấn "Bắt đầu căn chỉnh"

### Bước 5: Sửa lỗi
- Chọn tab "✏️ Sửa lỗi"
- Nhấn "Bắt đầu sửa lỗi"
- File Excel kết quả sẽ được tạo

### Bước 6: Quản lý
- Chọn tab "📊 Quản lý"
- Xem thống kê trạng thái
- Kiểm tra số trang
- Xóa dữ liệu nếu cần

## ⚙️ Cấu hình

Các cấu hình được đọc từ file `.env` trong thư mục gốc:

```
OUTPUT_FOLDER=./output
NAME_FILE_INFO=before_handle_data.json
NUM_CROP_HN=1
NUM_CROP_QN=1
VI_MODEL=./model/vi
NOM_MODEL=./model/nom
TYPE_QN=1
```

## 🔧 Khắc phục sự cố

### Lỗi: "Cannot read image"
- Đảm bảo file PDF hợp lệ
- Thử trích xuất lại

### Lỗi: "OCR models not found"
- Kiểm tra đường dẫn model trong `.env`
- Đảm bảo các model được tải đúng vị trí

### Lỗi: "Module not found"
- Kiểm tra `.env` có đúng đường dẫn tuyệt đối
- Cài đặt lại các thư viện: `pip install -r requirements.txt`

## 📝 Ghi chú

- Mỗi phase phải hoàn thành trước khi chuyển sang phase tiếp theo
- Có thể xóa dữ liệu và bắt đầu lại bất kỳ lúc nào
- Trạng thái được lưu trong file JSON
- Sidebar hiển thị trạng thái thực tế của mỗi phase

## 📞 Liên hệ

Nếu gặp vấn đề, vui lòng kiểm tra:
1. File `.env` có đúng cấu hình
2. Tất cả thư viện đã được cài đặt
3. Đường dẫn models có đúng

---

**Phiên bản:** 1.0  
**Cập nhật:** 2026
