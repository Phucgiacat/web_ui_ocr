# Hướng dẫn chi tiết: Cấu hình path, tham số `before_handle_data.json` và luồng input/output

Tài liệu này giải thích **thực tế chương trình đang chạy như thế nào** trong dự án `web_ui_ocr`:

- Tool đọc input từ đâu
- Output được ghi vào đâu
- Key nào trong `before_handle_data.json` do bước nào sinh ra
- Khi nào path trong JSON được giữ nguyên, khi nào bị ghi đè theo `.env`
- Cách chỉnh để output luôn lưu đúng vị trí mong muốn

---

## 1) Tổng quan nhanh (rất quan trọng)

Trong project này, có 3 nguồn cấu hình path chính:

1. **`.env`** (ví dụ `OUTPUT_FOLDER`, `NAME_FILE_INFO`)
2. **`before_handle_data.json`** (state runtime, cập nhật sau mỗi bước)
3. **UI Config** `web_ui/project_config.json` (dùng trong Web UI)

Về bản chất:

- `.env` quyết định **mặc định ban đầu**
- `before_handle_data.json` là **state pipeline đang chạy**
- Web UI có thể lấy từ `project_config.json`, sau đó ghi ngược vào `before_handle_data.json`

> Khuyến nghị: luôn chạy từ thư mục gốc `web_ui_ocr` để tránh lệch đường dẫn tương đối.

---

## 2) File nào điều khiển gì

### 2.1 `handle_data.py` (Extract/Crop/Align image index)

- Đọc `.env` bằng `load_dotenv('.env')`
- Dùng:
  - `OUTPUT_FOLDER`
  - `NAME_FILE_INFO` (mặc định `before_handle_data.json`)
  - `NUM_CROP_QN`, `NUM_CROP_HN`
- Khi chạy `--input`, chương trình:
  1. Xóa `OUTPUT_FOLDER` cũ
  2. Extract PDF ra ảnh
  3. Ghi `vi_dir`, `nom_dir` vào `before_handle_data.json`

### 2.2 `ocr_corrector.py` (OCR/Align/Correction qua CLI)

- Đọc `.env` bằng `load_dotenv('.env')`
- Đọc state từ `before_handle_data.json`
- Ghi output theo `OUTPUT_FOLDER`:
  - `ocr/Quoc_Ngu_ocr`
  - `ocr/Han_Nom_ocr`
  - `ocr/image_bbox`
  - `result.txt`
  - `result.xlsx`

### 2.3 `web_ui/config_manager.py` + `web_ui/ocr_processor.py` (Web UI)

- `ConfigManager` load từ `.env`, sau đó override bởi `web_ui/project_config.json` nếu có.
- Các tab UI đọc/ghi `before_handle_data.json` thông qua `OCRProcessor`.
- Một số path trong JSON được **ưu tiên giữ nguyên** (nếu bạn set tay trước).

---

## 3) Luồng dữ liệu chuẩn (end-to-end)

1. **Extract PDF**
   - Input: file PDF
   - Output:
     - `<OUTPUT_FOLDER>/image/Quoc Ngu`
     - `<OUTPUT_FOLDER>/image/Han Nom`
   - Ghi JSON: `file_name`, `vi_dir`, `nom_dir`

2. **Crop / Align số ảnh**
   - Input: `vi_dir`, `nom_dir`
   - Output: ảnh đã cắt/đổi tên trong chính thư mục ảnh hoặc thư mục processed
   - JSON có thể thêm `vi_dir_processed`, `nom_dir_processed`

3. **OCR Quốc Ngữ**
   - Input: `vi_dir`
   - Output TXT: `ocr_txt_qn` (mặc định `<OUTPUT_FOLDER>/ocr/Quoc_Ngu_ocr`)
   - Ghi JSON: `ocr_txt_qn`

4. **OCR Hán Nôm**
   - Input: `nom_dir`
   - Output JSON: `ocr_json_nom` (mặc định `<OUTPUT_FOLDER>/ocr/Han_Nom_ocr`)
   - Output bbox image: `ocr_image_nom` (mặc định `<OUTPUT_FOLDER>/ocr/image_bbox` hoặc cùng cấp `ocr_json_nom`)
   - Ghi JSON: `ocr_json_nom`, `ocr_image_nom`, `ocr_id`, `lang_type`, `epitaph`

5. **Align text**
   - Input: `ocr_json_nom` + `ocr_txt_qn`
   - Output: `output_txt` (mặc định `<OUTPUT_FOLDER>/result.txt`)
   - Ghi JSON: `output_txt`, `align_param`, `align_reverse`, `mapping_path` (nếu có)

6. **Correction**
   - Input: `output_txt`
   - Output Excel:
     - Web UI: key `result_xlsx` = `<OUTPUT_FOLDER>/result.xlsx`
     - CLI: key `Result` = `<OUTPUT_FOLDER>/result.xlsx`

---

## 4) Bảng tham số đầy đủ của `before_handle_data.json`

Lưu ý: không phải key nào cũng xuất hiện ngay từ đầu; key được thêm dần theo từng bước.

| Key | Ý nghĩa | Ai ghi | Ai đọc | Bắt buộc ở bước |
|---|---|---|---|---|
| `file_name` | Tên tài liệu (stem PDF) | Extract | Align/Correction | Align trở đi |
| `vi_dir` | Thư mục ảnh Quốc Ngữ đầu vào | Extract hoặc set tay/UI | OCR VI, crop, align index | OCR VI |
| `nom_dir` | Thư mục ảnh Hán Nôm đầu vào | Extract hoặc set tay/UI | OCR HN, crop, align index | OCR HN |
| `vi_dir_processed` | Thư mục ảnh QN sau xử lý | Crop/Edge detection | (tuỳ luồng) | Tuỳ chọn |
| `nom_dir_processed` | Thư mục ảnh HN sau xử lý | Crop/Edge detection | (tuỳ luồng) | Tuỳ chọn |
| `ocr_txt_qn` | Folder TXT OCR Quốc Ngữ | OCR bước VI hoặc set tay | Align | Align |
| `ocr_json_nom` | Folder JSON OCR Hán Nôm | OCR bước HN hoặc set tay | Align, progress OCR | Align |
| `ocr_image_nom` | Folder ảnh bbox OCR HN | OCR bước HN | extract_processed_images | Tuỳ chọn |
| `ocr_id` | Kiểu OCR API HN (engine mode) | OCR HN | nom_ocr/ocr_client | OCR HN |
| `lang_type` | Loại ngôn ngữ HN/Nôm | OCR HN | nom_ocr/ocr_client | OCR HN |
| `epitaph` | Cờ văn bia | OCR HN | nom_ocr/ocr_client | OCR HN |
| `output_txt` | File align đầu ra | Align | Correction | Correction |
| `align_param` | Tham số align `k` (1 hoặc 2) | Align | Theo dõi/ghi nhận pipeline | Align |
| `align_reverse` | Đảo thứ tự align (chủ yếu k=1) | Align | Align runtime | Align |
| `mapping_path` | File mapping (k=2 bắt buộc) | Align hoặc set tay | Align | Align k=2 |
| `result_xlsx` | Output Excel (Web UI) | Corrector (UI) | UI hiển thị kết quả | Sau correction |
| `Result` | Output Excel (CLI) | Corrector (CLI) | CLI flow | Sau correction |
| `extracted_image_dir` | Folder chứa ảnh đã OCR tách ra | OCRProcessor.extract_processed_images | UI/debug | Tuỳ chọn |
| `extracted_json_dir` | Folder chứa JSON OCR đã tách ra | OCRProcessor.extract_processed_images | UI/debug | Tuỳ chọn |

---

## 5) Cách chương trình quyết định input/output path (thứ tự ưu tiên)

## 5.1 Trong Web UI (`web_ui/ocr_processor.py`)

### OCR Quốc Ngữ

- Nếu `before_handle_data.json` đã có `ocr_txt_qn` -> **giữ nguyên path đó**
- Nếu chưa có -> tạo mặc định: `<OUTPUT_FOLDER>/ocr/Quoc_Ngu_ocr`

### OCR Hán Nôm

- Nếu đã có `ocr_json_nom` -> dùng path bạn đã đặt
- Nếu chưa có -> mặc định `<OUTPUT_FOLDER>/ocr/Han_Nom_ocr`
- `ocr_image_nom`:
  - Nếu đã có -> giữ nguyên
  - Nếu chưa có -> đặt cùng cấp với `ocr_json_nom`, tên folder `image_bbox`

### Align

- Nếu không truyền path từ UI function call:
  - Lấy `ocr_json_nom`, `ocr_txt_qn` từ JSON
- `output_txt` nếu không truyền -> `<OUTPUT_FOLDER>/result.txt`

### Correction

- Bắt buộc cần `output_txt` tồn tại
- Luôn ghi `result_xlsx = <OUTPUT_FOLDER>/result.xlsx`

## 5.2 Trong CLI (`ocr_corrector.py`)

- OCR/Align/Correction thường ghi theo `OUTPUT_FOLDER` (ít ưu tiên giữ custom path hơn Web UI).
- Nếu bạn muốn output custom theo CLI, nên sửa `before_handle_data.json` và truyền tham số phù hợp trước khi chạy align.

---

## 6) Cách chỉnh để output lưu đúng vị trí bạn muốn

## Cách A (khuyến nghị): set toàn cục qua `.env`

Ví dụ `.env`:

```env
OUTPUT_FOLDER=D:\learning\C.VAnh\Data\VBTM
NAME_FILE_INFO=before_handle_data.json
```

Khi đó mặc định output sẽ đi theo cây:

- `D:\learning\C.VAnh\Data\VBTM\image\...`
- `D:\learning\C.VAnh\Data\VBTM\ocr\...`
- `D:\learning\C.VAnh\Data\VBTM\result.txt`
- `D:\learning\C.VAnh\Data\VBTM\result.xlsx`

## Cách B: set chi tiết từng nhánh trong `before_handle_data.json`

Bạn có thể ép trực tiếp:

```json
{
  "vi_dir": "D:\\data\\custom\\images_vi",
  "nom_dir": "D:\\data\\custom\\images_nom",
  "ocr_txt_qn": "D:\\data\\custom\\ocr_qn",
  "ocr_json_nom": "D:\\data\\custom\\ocr_nom_json",
  "ocr_image_nom": "D:\\data\\custom\\ocr_nom_bbox",
  "output_txt": "D:\\data\\custom\\align\\result.txt",
  "mapping_path": "D:\\data\\custom\\mapping.xlsx",
  "ocr_id": 3,
  "lang_type": 1,
  "epitaph": 1
}
```

### Lưu ý quan trọng

- Web UI thường **tôn trọng** các key trên nếu đã có.
- Một số bước vẫn có thể ghi đè (`result_xlsx`, hoặc flow extract xóa output cũ).
- Nếu chạy lại `Extract PDF`, `vi_dir` và `nom_dir` sẽ được tạo lại theo `OUTPUT_FOLDER`.

---

## 7) Chạy từ đâu để không bị sai path

Khuyến nghị chạy tại thư mục gốc:

```powershell
cd D:\learning\C.VAnh\web_ui_ocr
```

Vì nhiều module dùng:

- `load_dotenv('.env')` (phụ thuộc current working directory)
- `NAME_FILE_INFO=before_handle_data.json` (đường dẫn tương đối)

Nếu chạy từ thư mục khác, có thể xảy ra:

- Không đọc đúng `.env`
- Ghi `before_handle_data.json` sang vị trí khác ngoài ý muốn
- Dùng default path sai

---

## 8) Ý nghĩa các tham số OCR Hán Nôm

Trong code hiện tại (`ConfigManager`):

- `ocr_id`:
  - `1`: thông thường dọc
  - `2`: hành chính
  - `3`: ngoại cảnh
  - `4`: thông thường ngang
- `lang_type`:
  - `0`: chưa biết
  - `1`: Hán
  - `2`: Nôm
- `epitaph`:
  - `0`: văn bản thường
  - `1`: văn bia

Các giá trị này được truyền vào API OCR Hán Nôm và cũng được ghi vào metadata mỗi file JSON OCR.

---

## 9) Mẫu `before_handle_data.json` theo từng giai đoạn

## 9.1 Sau Extract

```json
{
  "file_name": "BIA_TIENLANG",
  "vi_dir": "D:\\learning\\C.VAnh\\Data\\VBTL\\image\\Quoc Ngu",
  "nom_dir": "D:\\learning\\C.VAnh\\Data\\VBTL\\image\\Han Nom"
}
```

## 9.2 Sau OCR

```json
{
  "file_name": "BIA_TIENLANG",
  "vi_dir": "D:\\learning\\C.VAnh\\Data\\VBTL\\image\\Quoc Ngu",
  "nom_dir": "D:\\learning\\C.VAnh\\Data\\VBTL\\image\\Han Nom",
  "ocr_txt_qn": "D:\\learning\\C.VAnh\\Data\\VBTL\\ocr\\Quoc_Ngu_ocr",
  "ocr_json_nom": "D:\\learning\\C.VAnh\\Data\\VBTL\\ocr\\Han_Nom_ocr",
  "ocr_image_nom": "D:\\learning\\C.VAnh\\Data\\VBTL\\ocr\\image_bbox",
  "ocr_id": 1,
  "lang_type": 2,
  "epitaph": 1
}
```

## 9.3 Sau Align + Correction

```json
{
  "file_name": "BIA_TIENLANG",
  "vi_dir": "D:\\learning\\C.VAnh\\Data\\VBTL\\image\\Quoc Ngu",
  "nom_dir": "D:\\learning\\C.VAnh\\Data\\VBTL\\image\\Han Nom",
  "ocr_txt_qn": "D:\\learning\\C.VAnh\\Data\\VBTL\\ocr\\Quoc_Ngu_ocr",
  "ocr_json_nom": "D:\\learning\\C.VAnh\\Data\\VBTL\\ocr\\Han_Nom_ocr",
  "output_txt": "D:\\learning\\C.VAnh\\Data\\VBTL\\result.txt",
  "align_param": 1,
  "align_reverse": false,
  "result_xlsx": "D:\\learning\\C.VAnh\\Data\\VBTL\\result.xlsx"
}
```

---

## 10) Checklist cấu hình nhanh trước khi chạy

1. Đứng đúng thư mục gốc `web_ui_ocr`
2. Kiểm tra `.env` có `OUTPUT_FOLDER`, `NAME_FILE_INFO`
3. Nếu muốn custom path chi tiết, sửa `before_handle_data.json` trước bước OCR/Align
4. Chạy theo đúng thứ tự:
   - Extract -> Crop/Align ảnh -> OCR -> Align text -> Correction
5. Nếu đổi tài liệu mới, nên xóa state cũ (`output` + `before_handle_data.json`) rồi chạy lại

---

## 11) Lệnh CLI mẫu

```powershell
# 1) Extract PDF
python handle_data.py --input "D:\path\to\file.pdf"

# 2) (Tuỳ chọn) crop
python handle_data.py --crop false true

# 3) Đánh số để align ảnh
python handle_data.py --align_number_reverse false

# 4) OCR QN + HN
python ocr_corrector.py --ocr true true

# 5) Align (k=1 hoặc 2)
python ocr_corrector.py --align 1

# 6) Correction
python ocr_corrector.py --corrector false
```

---

## 12) Các lỗi path thường gặp

### Lỗi `Không tìm thấy file info: before_handle_data.json`

- Chưa chạy Extract
- Hoặc chạy ở sai working directory

### Lỗi `Không tìm thấy thư mục JSON/TXT`

- `ocr_json_nom` / `ocr_txt_qn` trong JSON đang trỏ nhầm folder
- Hoặc OCR chưa chạy xong

### Lỗi output ghi sai nơi

- `OUTPUT_FOLDER` trong `.env` khác với bạn nghĩ
- Hoặc `before_handle_data.json` đang giữ path cũ từ lần chạy trước

---

## 13) Quy tắc vàng để tránh loạn path

- Dùng **đường dẫn tuyệt đối** trong `before_handle_data.json` khi chạy dữ liệu thật
- Mỗi project/tập dữ liệu nên có `OUTPUT_FOLDER` riêng
- Không dùng chung `before_handle_data.json` cho nhiều job đồng thời
- Trước mỗi run lớn: backup hoặc xóa state cũ

---

Nếu bạn muốn, mình có thể tạo thêm một file mẫu `before_handle_data.template.json` theo đúng cấu trúc chuẩn để chỉ cần điền path và chạy.
