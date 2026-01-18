# 📋 JSON Config Schema - before_handle_data.json

## 📝 Cấu Trúc File

File `before_handle_data.json` là trung tâm quản lý dữ liệu cho toàn bộ pipeline OCR. Mỗi phase sẽ cập nhật các field tương ứng.

---

## 🔑 Fields Chi Tiết

### 1. **file_name** (string)
- **Mô tả:** Tên file PDF gốc (không bao gồm extension)
- **Ví dụ:** `"temp_TuNguyenYeuLy"`
- **Được set bởi:** `extract_pdf()` phase

### 2. **vi_dir** (string)
- **Mô tả:** Đường dẫn folder chứa ảnh Quốc Ngữ (từ PDF extraction)
- **Ví dụ:** `"D:\\learning\\C.VAnh\\tool\\output\\ocr\\Quoc_Ngu_ocr"`
- **Được set bởi:** `extract_pdf()` phase
- **Update bởi:** `crop_images()` (nếu không dùng edge detection)

### 3. **nom_dir** (string)
- **Mô tả:** Đường dẫn folder chứa ảnh Hán Nôm (từ PDF extraction)
- **Ví dụ:** `"D:\\learning\\C.VAnh\\tool\\output\\ocr\\Han_Nom_ocr"`
- **Được set bởi:** `extract_pdf()` phase
- **Update bởi:** `crop_images()` (nếu không dùng edge detection)

### 4. **vi_dir_processed** (string)
- **Mô tả:** Đường dẫn folder chứa ảnh Quốc Ngữ sau xử lý (crop hoặc edge detection)
- **Ví dụ:** `"D:\\learning\\C.VAnh\\tool\\output\\image_processed\\Quoc Ngu"`
- **Được set bởi:** `crop_images()` hoặc `edge_detection_crop()`
- **Sử dụng bởi:** Phases sau (OCR, align)

### 5. **nom_dir_processed** (string)
- **Mô tả:** Đường dẫn folder chứa ảnh Hán Nôm sau xử lý (crop hoặc edge detection)
- **Ví dụ:** `"D:\\learning\\C.VAnh\\tool\\output\\image_processed\\Han Nom"`
- **Được set bởi:** `crop_images()` hoặc `edge_detection_crop()`
- **Sử dụng bởi:** Phases sau (OCR, align)

### 6. **ocr_json_nom** (string)
- **Mô tả:** Đường dẫn folder/file chứa output JSON từ OCR Hán Nôm
- **Ví dụ:** `"D:\\learning\\C.VAnh\\tool\\output\\ocr\\Han_Nom_ocr"`
- **Được set bởi:** `ocr_han_nom()` phase hoặc `set_align_paths()` method
- **Sử dụng bởi:** `align_text()` phase
- **Note:** Nếu không có từ OCR, user có thể chọn manually qua `set_align_paths()`

### 7. **ocr_image_nom** (string)
- **Mô tả:** Đường dẫn folder chứa bounding box images từ OCR Hán Nôm
- **Ví dụ:** `"D:\\learning\\C.VAnh\\tool\\output\\ocr\\image_bbox"`
- **Được set bởi:** `ocr_han_nom()` phase

### 8. **ocr_txt_qn** (string)
- **Mô tả:** Đường dẫn folder/file chứa output TXT từ OCR Quốc Ngữ
- **Ví dụ:** `"D:\\learning\\C.VAnh\\tool\\output\\ocr\\Quoc_Ngu_ocr"`
- **Được set bởi:** `ocr_quoc_ngu()` phase hoặc `set_align_paths()` method
- **Sử dụng bởi:** `align_text()` phase
- **Note:** Nếu không có từ OCR, user có thể chọn manually qua `set_align_paths()`

### 9. **output_txt** (string)
- **Mô tả:** Đường dẫn file TXT output sau align
- **Ví dụ:** `"D:\\learning\\C.VAnh\\tool\\output\\result.txt"`
- **Được set bởi:** `align_text()` phase

### 10. **result_xlsx** (string)
- **Mô tả:** Đường dẫn file XLSX output cuối cùng (sau sửa lỗi)
- **Ví dụ:** `"D:\\learning\\C.VAnh\\tool\\output\\result.xlsx"`
- **Được set bởi:** `correct_text()` phase

### 11. **ocr_id** (integer)
- **Mô tả:** ID loại OCR cho Hán Nôm (1=default)
- **Giá trị:** `1`
- **Được set bởi:** `ocr_han_nom()` phase (từ config)

### 12. **lang_type** (integer)
- **Mô tả:** Loại ngôn ngữ cho OCR (0=Hán, 1=Quốc Ngữ, 2=Hỗn hợp)
- **Giá trị:** `0`, `1`, `2`
- **Được set bởi:** `ocr_han_nom()` phase (từ config)

### 13. **epitaph** (integer)
- **Mô tả:** Flag cho OCR inscription (1=có, 0=không)
- **Giá trị:** `0` hoặc `1`
- **Được set bởi:** `ocr_han_nom()` phase (từ config)

---

## 🔄 Pipeline Các Phase

```
1. extract_pdf()
   └─ Set: file_name, vi_dir, nom_dir

2. crop_images() / edge_detection_crop()
   └─ Set: vi_dir_processed, nom_dir_processed

3. align_images()
   └─ Sửa tên files trong vi_dir/nom_dir hoặc vi_dir_processed/nom_dir_processed

4. ocr_quoc_ngu()
   └─ Set: ocr_txt_qn

5. ocr_han_nom()
   └─ Set: ocr_json_nom, ocr_image_nom, ocr_id, lang_type, epitaph

6a. set_align_paths() (nếu user chọn folder manually)
    └─ Update: ocr_json_nom, ocr_txt_qn

6b. align_text()
    └─ Đọc: ocr_json_nom, ocr_txt_qn từ config
    └─ Nếu không có, throw error
    └─ Set: output_txt

7. correct_text()
   └─ Set: result_xlsx
```

## 🎯 Flow Align Chi Tiết

```
align_text() được gọi:
  ├─ Nếu user cung cấp paths: sử dụng paths đó
  ├─ Nếu không: lấy từ config file (ocr_json_nom, ocr_txt_qn)
  ├─ Nếu config không có: throw error
  │  └─ "Chưa set đường dẫn JSON/TXT. Chọn folder hoặc chạy OCR trước"
  └─ Sau khi align xong: 
     └─ Lưu paths vào config (để reference sau này)
     └─ Lưu output_txt vào config
```

## 💡 Cách Sử Dụng

### Option 1: Chạy OCR (tự động set paths)
```python
processor = OCRProcessor(output_folder, config_file)

# OCR sẽ tự động set ocr_txt_qn và ocr_json_nom
processor.ocr_quoc_ngu()
processor.ocr_han_nom()

# align_text() sẽ lấy paths từ config
processor.align_text()
```

### Option 2: Chọn folder manually
```python
processor = OCRProcessor(output_folder, config_file)

# User chọn folder qua UI, gọi set_align_paths()
result = processor.set_align_paths(
    ocr_json_nom="user_selected_json_folder",
    ocr_txt_qn="user_selected_txt_folder"
)

# Config đã được update, align_text() sẽ hoạt động
processor.align_text()
```

### Option 3: Kết hợp (OCR + chọn folder)
```python
processor = OCRProcessor(output_folder, config_file)

# Nếu chỉ có JSON từ OCR, nhưng TXT từ folder khác
processor.ocr_han_nom()  # Set ocr_json_nom
processor.set_align_paths(ocr_txt_qn="folder_txt_khac")  # Set ocr_txt_qn

processor.align_text()
```

---

## 📊 Ví Dụ File Sau Mỗi Phase

### Sau extract_pdf()
```json
{
    "file_name": "temp_TuNguyenYeuLy",
    "vi_dir": "D:\\output\\ocr\\Quoc_Ngu_ocr",
    "nom_dir": "D:\\output\\ocr\\Han_Nom_ocr",
    "vi_dir_processed": "",
    "nom_dir_processed": ""
}
```

### Sau crop_images()
```json
{
    "file_name": "temp_TuNguyenYeuLy",
    "vi_dir": "D:\\output\\ocr\\Quoc_Ngu_ocr",
    "nom_dir": "D:\\output\\ocr\\Han_Nom_ocr",
    "vi_dir_processed": "D:\\output\\ocr\\Quoc_Ngu_ocr",
    "nom_dir_processed": "D:\\output\\ocr\\Han_Nom_ocr"
}
```

### Sau align_text()
```json
{
    "file_name": "temp_TuNguyenYeuLy",
    "vi_dir": "D:\\output\\ocr\\Quoc_Ngu_ocr",
    "nom_dir": "D:\\output\\ocr\\Han_Nom_ocr",
    "vi_dir_processed": "D:\\output\\ocr\\Quoc_Ngu_ocr",
    "nom_dir_processed": "D:\\output\\ocr\\Han_Nom_ocr",
    "ocr_txt_qn": "D:\\output\\ocr\\Quoc_Ngu_ocr",
    "ocr_json_nom": "D:\\output\\ocr\\Han_Nom_ocr",
    "ocr_image_nom": "D:\\output\\ocr\\image_bbox",
    "output_txt": "D:\\output\\result.txt"
}
```

### Sau correct_text()
```json
{
    "file_name": "temp_TuNguyenYeuLy",
    "vi_dir": "D:\\output\\ocr\\Quoc_Ngu_ocr",
    "nom_dir": "D:\\output\\ocr\\Han_Nom_ocr",
    "vi_dir_processed": "D:\\output\\ocr\\Quoc_Ngu_ocr",
    "nom_dir_processed": "D:\\output\\ocr\\Han_Nom_ocr",
    "ocr_txt_qn": "D:\\output\\ocr\\Quoc_Ngu_ocr",
    "ocr_json_nom": "D:\\output\\ocr\\Han_Nom_ocr",
    "ocr_image_nom": "D:\\output\\ocr\\image_bbox",
    "output_txt": "D:\\output\\result.txt",
    "result_xlsx": "D:\\output\\result.xlsx",
    "ocr_id": 1,
    "lang_type": 2,
    "epitaph": 1
}
```

---

## 🔐 Validation Rules

| Field | Required | Type | Validation |
|-------|----------|------|-----------|
| file_name | Yes | string | Non-empty |
| vi_dir | Yes | string | Must exist after extract_pdf |
| nom_dir | Yes | string | Must exist after extract_pdf |
| vi_dir_processed | No | string | Set after crop/edge-detect |
| nom_dir_processed | No | string | Set after crop/edge-detect |
| ocr_json_nom | No | string | Set after ocr_han_nom |
| ocr_txt_qn | No | string | Set after ocr_quoc_ngu |
| output_txt | No | string | Set after align_text |
| result_xlsx | No | string | Set after correct_text |
| ocr_id | No | integer | Default 1 |
| lang_type | No | integer | Default 0-2 |
| epitaph | No | integer | Default 0-1 |

---

## 💡 Tips

1. **Không xóa file JSON** khi đang chạy pipeline - tất cả phases dựa vào file này
2. **Các path phải absolute** (full path), không dùng relative path
3. **Tự động cập nhật** - Mỗi phase tự động update JSON, không cần manual edit
4. **Reuse cho multiple runs** - Có thể dùng lại file JSON từ previous run (nếu folder vẫn tồn tại)
