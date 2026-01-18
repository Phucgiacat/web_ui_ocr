import streamlit as st
from streamlit_option_menu import option_menu
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import json
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Check if parent modules are available
DEMO_MODE = False
try:
    from web_ui.config_manager import ConfigManager
    from web_ui.data_handler import DataHandler
    from web_ui.ocr_processor import OCRProcessor
except ImportError as e:
    st.error(f"❌ Import Error: {e}")
    st.info("""
    ### 🔧 Setup Issues Detected
    
    **How to fix:**
    1. Make sure you're running from the `ocr_corrector` root directory:
       ```bash
       cd d:\\learning\\C.VAnh\\tool\\ocr_corrector
       python -m streamlit run web_ui/app.py --server.port 8503
       ```
    
    2. Ensure all parent modules exist:
       - Proccess_pdf/
       - vi_ocr/
       - nom_ocr/
       - align/
    
    3. If running from elsewhere, the app can start in DEMO MODE
    """)
    DEMO_MODE = True

# Load environment
try:
    load_dotenv(Path(__file__).parent.parent / '.env')
except:
    pass

# For demo mode, create mock classes
if DEMO_MODE:
    class ConfigManager:
        def __init__(self):
            self.output_folder = "./output"
            self.name_file_info = "before_handle_data.json"
            self.vi_dir = ""
            self.nom_dir = ""
            self.ocr_json_nom = ""
            self.ocr_txt_qn = ""
            self.num_crop_hn = 1
            self.num_crop_qn = 1
            self.ocr_id = 1
            self.lang_type = 0
            self.epitaph = 0
            self.config_file = None
        def get_status(self):
            return {
                'extracted': False,
                'cropped': False,
                'ocr_vi': False,
                'ocr_nom': False,
                'aligned': False,
                'corrected': False,
                'info': None
            }
        def save_config(self):
            return True
        def clear_output_folder(self):
            return True
    
    class DataHandler:
        def __init__(self, *args, **kwargs):
            pass
    
    class OCRProcessor:
        def __init__(self, *args, **kwargs):
            pass

# Initialize session state
if 'config' not in st.session_state:
    st.session_state.config = ConfigManager()
if 'current_status' not in st.session_state:
    st.session_state.current_status = None
if 'demo_mode' not in st.session_state:
    st.session_state.demo_mode = DEMO_MODE

config = st.session_state.config

# Page config
st.set_page_config(
    page_title="OCR Corrector - Web UI",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
    }
    .main-title {
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
    }
    .status-box {
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .status-completed {
        background-color: #d4edda;
        border-left: 5px solid #28a745;
    }
    .status-pending {
        background-color: #fff3cd;
        border-left: 5px solid #ffc107;
    }
    </style>
    """, unsafe_allow_html=True)

# Sidebar
st.sidebar.title("⚙️ Cấu Hình")
st.sidebar.markdown("---")

# Refresh status
# Display info if available
status = st.session_state.current_status or config.get_status()
st.session_state.current_status = status

if st.sidebar.button("🔄 Làm mới trạng thái"):
    st.session_state.current_status = config.get_status()
    st.rerun()

st.sidebar.markdown("---")

# Show demo mode warning
if st.session_state.demo_mode:
    st.sidebar.warning("""
    ⚠️ **DEMO MODE**
    
    Parent modules not found.
    
    To enable full functionality:
    ```bash
    cd ocr_corrector
    python -m streamlit run \\
      web_ui/app.py
    ```
    """)
else:
    st.sidebar.subheader("📊 Trạng thái hiện tại:")
    col1, col2 = st.sidebar.columns(2)
    with col1:
        st.metric("Trích xuất", "✅" if status['extracted'] else "⏳")
        st.metric("OCR Quốc Ngữ", "✅" if status['ocr_vi'] else "⏳")
        st.metric("Align", "✅" if status['aligned'] else "⏳")
    with col2:
        st.metric("Cắt ảnh", "✅" if status['cropped'] else "⏳")
        st.metric("OCR Hán Nôm", "✅" if status['ocr_nom'] else "⏳")
        st.metric("Sửa lỗi", "✅" if status['corrected'] else "⏳")

    st.sidebar.markdown("---")

if status.get('info') and not st.session_state.demo_mode:
    st.sidebar.markdown("---")
    st.sidebar.subheader("📋 Thông tin dự án:")
    with st.sidebar.expander("Chi tiết"):
        st.json(status['info'])

st.sidebar.markdown("---")

# Main content
st.markdown("<h1 class='main-title'>📄 OCR Corrector - Web Tool</h1>", unsafe_allow_html=True)
st.markdown("Công cụ xử lý OCR cho tài liệu Quốc Ngữ và Hán Nôm")

# Show demo mode notice
if st.session_state.demo_mode:
    st.warning("""
    ### ⚠️ DEMO MODE - Parent Modules Not Available
    
    The application is running in **demo mode** because parent modules could not be imported.
    
    #### To use full functionality:
    
    1. **Ensure you're in the correct directory:**
       ```bash
       cd d:\\learning\\C.VAnh\\tool\\ocr_corrector
       ```
    
    2. **Make sure these folders exist:**
       - `Proccess_pdf/` - PDF processing
       - `vi_ocr/` - Vietnamese OCR
       - `nom_ocr/` - Sino-Vietnamese OCR  
       - `align/` - Text alignment
    
    3. **Run the app:**
       ```bash
       python -m streamlit run web_ui/app.py
       ```
    
    You can still explore the UI in demo mode, but the actual processing functions will show errors.
    """)

st.markdown("---")

# Main menu
selected = option_menu(
    menu_title=None,
    options=["📥 Trích xuất PDF", "✂️ Cắt ảnh", "👁️ OCR", "🔗 Align", "✏️ Sửa lỗi", "⚙️ Chi tiết", "📊 Quản lý"],
    icons=["download", "scissors", "eye", "link", "pencil", "sliders", "gear"],
    orientation="horizontal",
    styles={
        "container": {"padding": "0!important", "background-color": "#fafafa"},
        "icon": {"color": "orange", "font-size": "25px"},
        "nav-link": {"font-size": "16px", "text-align": "left", "margin": "0px", "--hover-color": "#eee"},
        "nav-link-selected": {"background-color": "#1f77b4", "color": "white"},
    }
)

# =================== TAB 1: TRÍCH XUẤT PDF ===================
if selected == "📥 Trích xuất PDF":
    st.header("📥 Trích xuất PDF thành ảnh")

    if st.session_state.demo_mode:
        st.info("💡 **Demo Mode**: Parent modules not available. This feature is disabled.")
        st.markdown("To enable, follow the setup instructions in the sidebar.")
    else:
        col1, col2 = st.columns([3, 1])
        
        with col1:
            uploaded_file = st.file_uploader("Chọn file PDF", type=['pdf'])
        
        with col2:
            if st.button("🗑️ Xóa dữ liệu cũ", key="clear_old"):
                try:
                    if config.clear_output_folder():
                        if os.path.exists(config.name_file_info):
                            os.remove(config.name_file_info)
                        st.success("Đã xóa dữ liệu cũ!")
                    else:
                        st.error("Lỗi khi xóa dữ liệu")
                except Exception as e:
                    st.error(f"Lỗi: {e}")
        
        if uploaded_file:
            try:
                # Create temp directory if not exists
                import tempfile
                temp_dir = os.path.join(os.getcwd(), "temp")
                os.makedirs(temp_dir, exist_ok=True)
                
                # Save uploaded file with absolute path
                temp_path = os.path.join(temp_dir, f"temp_{uploaded_file.name}")
                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                st.success(f"✅ Tải file thành công: {uploaded_file.name}")
                
            except Exception as e:
                st.error(f"❌ Lỗi khi tải file: {str(e)}")
                temp_path = None
            
            if 'temp_path' in locals() and temp_path and st.button("▶️ Bắt đầu trích xuất"):
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                def progress_callback(message, current, total):
                    progress_bar.progress(current / (total or 1))
                    status_text.write(f"📝 {message}")
                
                try:
                    handler = DataHandler(config.output_folder, config.name_file_info)
                    info = handler.extract_pdf(temp_path, progress_callback=progress_callback)
                    
                    st.success("✅ Trích xuất PDF thành công!")
                    st.json(info)
                    
                    # Cleanup temp file with retry logic for locked files
                    if 'temp_path' in locals() and temp_path:
                        import time
                        for attempt in range(3):
                            try:
                                if os.path.exists(temp_path):
                                    os.remove(temp_path)
                                break
                            except PermissionError:
                                if attempt < 2:
                                    time.sleep(1)  # Wait before retry
                                # Silently fail on final attempt
                    
                    st.session_state.current_status = config.get_status()
                    
                except Exception as e:
                    st.error(f"❌ Lỗi trích xuất: {str(e)}")
                    # Cleanup on error with same retry logic
                    if 'temp_path' in locals() and temp_path:
                        import time
                        for attempt in range(3):
                            try:
                                if os.path.exists(temp_path):
                                    os.remove(temp_path)
                                break
                            except PermissionError:
                                if attempt < 2:
                                    time.sleep(1)

# =================== TAB 2: CẮT ẢNH ===================
elif selected == "✂️ Cắt ảnh":
    st.header("✂️ Cắt ảnh")
    
    st.info("💡 Bạn có thể cắt ảnh từ thư mục tùy chỉnh (không cần phải trích xuất PDF trước)")
    
    # Allow user to specify input directories
    col1, col2 = st.columns(2)
    with col1:
        vi_dir_crop = st.text_input("Thư mục ảnh Quốc Ngữ", value=config.vi_dir, help="Đường dẫn thư mục chứa ảnh Quốc Ngữ cần cắt")
    with col2:
        nom_dir_crop = st.text_input("Thư mục ảnh Hán Nôm", value=config.nom_dir, help="Đường dẫn thư mục chứa ảnh Hán Nôm cần cắt")
    
    st.markdown("---")
    
    tab1, tab2 = st.tabs(["Cắt ảnh thường", "Edge Detection"])
    
    # Tab 1: Cắt ảnh thường
    with tab1:
        st.subheader("Cắt ảnh thường")
        
        col1, col2 = st.columns(2)
        with col1:
            num_crop_qn = st.number_input("Số lượng cắt Quốc Ngữ", min_value=1, value=config.num_crop_qn, key="crop_qn")
        with col2:
            num_crop_hn = st.number_input("Số lượng cắt Hán Nôm", min_value=1, value=config.num_crop_hn, key="crop_hn")
        
        if st.button("▶️ Bắt đầu cắt ảnh"):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            def progress_callback(message, current, total):
                if total > 0:
                    progress_bar.progress(current / total)
                status_text.write(f"📝 {message}")
            
            try:
                handler = DataHandler(config.output_folder, config.name_file_info)
                handler.crop_images(num_crop_qn, num_crop_hn, progress_callback=progress_callback)
                
                st.success("✅ Cắt ảnh thành công!")
                st.session_state.current_status = config.get_status()
                
            except Exception as e:
                st.error(f"❌ Lỗi: {str(e)}")
    
    # Tab 2: Edge Detection
    with tab2:
        st.subheader("Cắt ảnh bằng Edge Detection")
        
        col1, col2 = st.columns(2)
        with col1:
            crop_qn = st.checkbox("Xử lý Quốc Ngữ", value=True)
        with col2:
            crop_hn = st.checkbox("Xử lý Hán Nôm", value=True)
        
        if st.button("▶️ Bắt đầu xử lý"):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            def progress_callback(message, current, total):
                if total > 0:
                    progress_bar.progress(current / total)
                status_text.write(f"📝 {message}")
            
            try:
                handler = DataHandler(config.output_folder, config.name_file_info)
                handler.edge_detection_crop(config.vi_model, config.nom_model, crop_qn, crop_hn, progress_callback=progress_callback)
                
                st.success("✅ Xử lý edge detection thành công!")
                st.session_state.current_status = config.get_status()
                
            except Exception as e:
                st.error(f"❌ Lỗi: {str(e)}")

# =================== TAB 3: OCR ===================
elif selected == "👁️ OCR":
    st.header("👁️ Nhận diện ký tự (OCR)")
    
    st.info("💡 Bạn có thể chạy OCR từ các thư mục ảnh tùy chỉnh (không cần phải cắt ảnh trước)")
    
    # Allow user to specify input directories
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Thư mục ảnh Quốc Ngữ (OCR)**")
        
        vi_dir_ocr = st.text_input(
            "📁 Nhập đường dẫn thư mục",
            value=config.vi_dir,
            help="Thư mục chứa ảnh Quốc Ngữ cần OCR",
            key="vi_dir_ocr_input"
        )
        
        # Update config if changed
        if vi_dir_ocr and vi_dir_ocr != config.vi_dir:
            config.vi_dir = vi_dir_ocr
            config.save_paths_to_info()
            st.success("✅ Đã lưu path Quốc Ngữ vào before_handle_data.json")
    
    with col2:
        st.markdown("**Thư mục ảnh Hán Nôm (OCR)**")
        
        nom_dir_ocr = st.text_input(
            "📁 Nhập đường dẫn thư mục",
            value=config.nom_dir,
            help="Thư mục chứa ảnh Hán Nôm cần OCR",
            key="nom_dir_ocr_input"
        )
        
        # Update config if changed
        if nom_dir_ocr and nom_dir_ocr != config.nom_dir:
            config.nom_dir = nom_dir_ocr
            config.save_paths_to_info()
            st.success("✅ Đã lưu path Hán Nôm vào before_handle_data.json")
    
    st.markdown("---")
    
    st.subheader("⚙️ Thiết lập OCR Hán Nôm")
    col_ocr1, col_ocr2, col_ocr3 = st.columns(3)
    
    with col_ocr1:
        ocr_id = st.selectbox(
            "Loại OCR",
            options=[1, 2, 3, 4],
            format_func=lambda x: {
                1: "1: Thông thường dọc",
                2: "2: Hành chính",
                3: "3: Ngoại cảnh",
                4: "4: Thông thường ngang"
            }[x],
            index=config.ocr_id - 1,
            key="ocr_id_select"
        )
        config.ocr_id = ocr_id
    
    with col_ocr2:
        lang_type = st.selectbox(
            "Loại ngôn ngữ",
            options=[0, 1, 2],
            format_func=lambda x: {
                0: "0: Chưa biết",
                1: "1: Hán",
                2: "2: Nôm"
            }[x],
            index=config.lang_type,
            key="lang_type_select"
        )
        config.lang_type = lang_type
    
    with col_ocr3:
        epitaph = st.selectbox(
            "Loại văn bản",
            options=[0, 1],
            format_func=lambda x: {
                0: "0: Văn bản thông thường",
                1: "1: Văn bia"
            }[x],
            index=config.epitaph,
            key="epitaph_select"
        )
        config.epitaph = epitaph
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔤 OCR Quốc Ngữ", key="ocr_qn", use_container_width=True):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            def progress_callback(message, current, total):
                progress_bar.progress(current / (total or 1))
                status_text.write(f"📝 {message}")
            
            try:
                processor = OCRProcessor(config.output_folder, config.name_file_info, config.ocr_id, config.lang_type, config.epitaph)
                processor.ocr_quoc_ngu(progress_callback=progress_callback)
                
                st.success("✅ OCR Quốc Ngữ thành công!")
                st.session_state.current_status = config.get_status()
                
            except Exception as e:
                st.error(f"❌ Lỗi: {str(e)}")
    
    with col2:
        if st.button("🈳 OCR Hán Nôm", key="ocr_hn", use_container_width=True):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            def progress_callback(message, current, total):
                progress_bar.progress(current / (total or 1))
                status_text.write(f"📝 {message}")
            
            try:
                processor = OCRProcessor(config.output_folder, config.name_file_info, config.ocr_id, config.lang_type, config.epitaph)
                processor.ocr_han_nom(progress_callback=progress_callback)
                
                st.success("✅ OCR Hán Nôm thành công!")
                st.session_state.current_status = config.get_status()
                
            except Exception as e:
                st.error(f"❌ Lỗi: {str(e)}")
    
    with col3:
        if st.button("🔤🈳 OCR Cả hai", key="ocr_both", use_container_width=True):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            def progress_callback(message, current, total):
                progress_bar.progress(current / (total or 1))
                status_text.write(f"📝 {message}")
            
            try:
                processor = OCRProcessor(config.output_folder, config.name_file_info, config.ocr_id, config.lang_type, config.epitaph)
                processor.ocr_both(progress_callback=progress_callback)
                
                st.success("✅ OCR cả hai thành công!")
                st.session_state.current_status = config.get_status()
                
            except Exception as e:
                st.error(f"❌ Lỗi: {str(e)}")

# =================== TAB 4: ALIGN ===================
elif selected == "🔗 Align":
    st.header("🔗 Căn chỉnh và Align text")
    
    st.info("""
    💡 **Cách sử dụng Align:**
    - Truyền 2 thư mục: một chứa file JSON Hán Nôm, một chứa file TXT Quốc Ngữ
    - **Yêu cầu quan trọng**: Các file phải có cùng tên cơ sở (ví dụ: `image_001.json` và `image_001.txt`)
    - Nếu file TXT không tìm thấy, file đó sẽ bị bỏ qua (xem cảnh báo)
    - Thông tin sẽ được lấy từ file `before_handle_data.json` nếu có
    """)
    
    # Đọc thông tin từ config
    processor = OCRProcessor(config.output_folder, config.name_file_info)
    info = None
    try:
        info = processor.read_file_info()
        default_json_path = info.get('ocr_json_nom', config.ocr_json_nom or '')
        default_txt_path = info.get('ocr_txt_qn', config.ocr_txt_qn or '')
        default_align_param = info.get('align_param', 1)  # Mặc định k=1
        default_reverse = info.get('align_reverse', False)
        default_mapping_path = info.get('mapping_path', '')
        file_name = info.get('file_name', '')
    except:
        default_json_path = config.ocr_json_nom or ''
        default_txt_path = config.ocr_txt_qn or ''
        default_align_param = 1  # Mặc định k=1
        default_reverse = False
        default_mapping_path = ''
        file_name = ''
    
    # Hiển thị thông tin từ config
    if file_name:
        st.info(f"📖 **Tên file hiện tại:** {file_name}")
    
    col1, col2 = st.columns(2)
    with col1:
        ocr_json_nom_align = st.text_input(
            "File/Thư mục JSON Hán Nôm", 
            value=default_json_path, 
            help="Đường dẫn thư mục chứa file JSON từ nom OCR (tự động lấy từ config nếu có)",
            key="ocr_json_nom_align"
        )
    with col2:
        ocr_txt_qn_align = st.text_input(
            "File/Thư mục TXT Quốc Ngữ", 
            value=default_txt_path, 
            help="Đường dẫn thư mục chứa file TXT từ vi OCR (phải có cùng tên với JSON, tự động lấy từ config nếu có)",
            key="ocr_txt_qn_align"
        )
    
    st.markdown("---")
    
    # Chọn k=1 hoặc k=2
    st.subheader("⚙️ Cấu hình Align")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        align_param = st.radio(
            "Chọn phương thức Align (k)",
            options=[1, 2],
            index=0 if default_align_param == 1 else 1,
            format_func=lambda x: f"k={x}: {'Không có file mapping' if x == 1 else 'Có file mapping (mapping.xlsx)'}",
            help="k=1: Align thông thường không cần mapping file\nk=2: Align với file mapping.xlsx (tự động lấy từ config nếu có)"
        )
    
    with col2:
        reverse_nom = st.checkbox("Đảo chiều Hán Nôm", value=default_reverse, help="Chỉ áp dụng khi k=1. Tự động lấy từ config nếu có")
    
    # Nếu k=2, hiển thị nút chọn file mapping
    mapping_path_input = None
    
    if align_param == 2:
        st.markdown("---")
        st.info("📋 **k=2 yêu cầu file mapping.xlsx** - File này chứa thông tin mapping giữa file Hán Nôm và Quốc Ngữ")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            mapping_path_input = st.text_input(
                "Đường dẫn file mapping.xlsx",
                value=default_mapping_path,
                help="Chọn file mapping.xlsx hoặc nhập đường dẫn. File phải có cột 'hannom' và 'quocngu' chứa danh sách files",
                key="mapping_path_input"
            )
        with col2:
            # Nút chọn file (Streamlit file uploader không hỗ trợ chọn file từ hệ thống, nên dùng text input)
            st.caption("Nhập đường dẫn tuyệt đối hoặc tương đối")
    
    if st.button("▶️ Bắt đầu căn chỉnh"):
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        def progress_callback(message, current, total):
            if total > 0:
                progress_bar.progress(current / total)
            status_text.write(f"📝 {message}")
        
        try:
            # Lấy paths từ input, nếu rỗng thì lấy từ config
            json_path = ocr_json_nom_align.strip() if ocr_json_nom_align.strip() else None
            txt_path = ocr_txt_qn_align.strip() if ocr_txt_qn_align.strip() else None
            output_path = os.path.join(config.output_folder, 'result.txt')
            
            # Lấy mapping_path nếu k=2
            mapping_path = None
            if align_param == 2:
                if not mapping_path_input or not mapping_path_input.strip():
                    st.error("❌ Vui lòng nhập đường dẫn file mapping.xlsx khi chọn k=2")
                    st.stop()
                mapping_path = mapping_path_input.strip()
                if not os.path.exists(mapping_path):
                    st.error(f"❌ Không tìm thấy file mapping: {mapping_path}")
                    st.stop()
            
            processor.align_text(
                ocr_json_nom=json_path,
                ocr_txt_qn=txt_path,
                output_txt=output_path,
                align_param=align_param,
                name_book=file_name,  # Truyền file_name từ config
                reverse=reverse_nom if align_param == 1 else False,  # reverse chỉ áp dụng khi k=1
                mapping_path=mapping_path,
                progress_callback=progress_callback
            )
            
            st.success("✅ Align thành công!")
            st.info(f"📝 Output được lưu tại: `{output_path}`")
            st.session_state.current_status = config.get_status()
            
        except Exception as e:
            st.error(f"❌ Lỗi: {str(e)}")

# =================== TAB 5: SỬA LỖI ===================
elif selected == "✏️ Sửa lỗi":
    st.header("✏️ Sửa lỗi và tạo Excel")
    
    st.info("💡 Bạn có thể chạy Sửa lỗi từ file TXT tùy chỉnh (không cần phải Align trước)")
    
    output_txt_correct = st.text_input("File TXT Align", value=config.output_folder, help="Đường dẫn file TXT từ quá trình align", key="output_txt_correct")
    
    st.markdown("---")
    
    debug_mode = st.checkbox("Chế độ Debug", value=False)
    
    if st.button("▶️ Bắt đầu sửa lỗi"):
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        def progress_callback(message, current, total):
            progress_bar.progress(current / (total or 1))
            status_text.write(f"📝 {message}")
        
        try:
            processor = OCRProcessor(config.output_folder, config.name_file_info)
            processor.correct_text(debug=debug_mode, progress_callback=progress_callback)
            
            st.success("✅ Sửa lỗi thành công!")
            st.session_state.current_status = config.get_status()
            
        except Exception as e:
            st.error(f"❌ Lỗi: {str(e)}")

# =================== TAB 6: CHI TIẾT DỰ ÁN ===================
elif selected == "⚙️ Chi tiết":
    st.header("⚙️ Chi tiết dự án")

    st.subheader("📁 Đường dẫn dự án")
    col1, col2 = st.columns([3, 1])

    with col1:
        output_folder = st.text_input(
            "Thư mục Output",
            value=config.output_folder,
            help="Nơi lưu kết quả xử lý"
        )
        if output_folder != config.output_folder:
            config.output_folder = output_folder

    with col2:
        if st.button("📂 Chọn folder", use_container_width=True):
            st.info("💡 Sử dụng đường dẫn tuyệt đối hoặc tương đối từ thư mục gốc")

    # allow choosing input directories
    st.markdown("---")
    st.subheader("📁 Đường dẫn nguồn dữ liệu")
    col1, col2, col3 = st.columns(3)
    with col1:
        name_file_info = st.text_input("File thông tin (JSON)", value=getattr(config, 'name_file_info', 'before_handle_data.json'))
        config.name_file_info = name_file_info
        vi_dir = st.text_input("Thư mục ảnh Quốc Ngữ (vi_dir)", value=getattr(config, 'vi_dir', ''))
        config.vi_dir = vi_dir
    with col2:
        ocr_json_nom = st.text_input("Thư mục JSON Hán Nôm (ocr_json_nom)", value=getattr(config, 'ocr_json_nom', ''))
        config.ocr_json_nom = ocr_json_nom
        nom_dir = st.text_input("Thư mục ảnh Hán Nôm (nom_dir)", value=getattr(config, 'nom_dir', ''))
        config.nom_dir = nom_dir
        st.caption("Bạn có thể nhập đường dẫn tuyệt đối hoặc tương đối từ thư mục dự án.")
    with col3:
        ocr_txt_qn = st.text_input("Thư mục TXT Quốc Ngữ (ocr_txt_qn)", value=getattr(config, 'ocr_txt_qn', ''))
        config.ocr_txt_qn = ocr_txt_qn

    st.markdown("---")

    st.subheader("🔧 Thiết lập cắt ảnh")
    col1, col2 = st.columns(2)

    with col1:
        num_crop_qn = st.number_input(
            "Số cắt ảnh Quốc Ngữ",
            min_value=1,
            max_value=10,
            value=config.num_crop_qn,
            help="Số lần cắt ngang cho ảnh Quốc Ngữ"
        )
        config.num_crop_qn = num_crop_qn

    with col2:
        num_crop_hn = st.number_input(
            "Số cắt ảnh Hán Nôm",
            min_value=1,
            max_value=10,
            value=config.num_crop_hn,
            help="Số lần cắt ngang cho ảnh Hán Nôm"
        )
        config.num_crop_hn = num_crop_hn

    st.markdown("---")

    st.subheader("🈳 Thiết lập OCR Hán Nôm")
    col1, col2, col3 = st.columns(3)

    with col1:
        ocr_id_detail = st.selectbox(
            "Loại OCR",
            options=[1, 2, 3, 4],
            format_func=lambda x: {
                1: "1: Thông thường dọc",
                2: "2: Hành chính",
                3: "3: Ngoại cảnh",
                4: "4: Thông thường ngang"
            }[x],
            index=config.ocr_id - 1,
            key="ocr_id_detail"
        )
        config.ocr_id = ocr_id_detail

    with col2:
        lang_type_detail = st.selectbox(
            "Loại ngôn ngữ",
            options=[0, 1, 2],
            format_func=lambda x: {
                0: "0: Chưa biết",
                1: "1: Hán",
                2: "2: Nôm"
            }[x],
            index=config.lang_type,
            key="lang_type_detail"
        )
        config.lang_type = lang_type_detail

    with col3:
        epitaph_detail = st.selectbox(
            "Loại văn bản",
            options=[0, 1],
            format_func=lambda x: {
                0: "0: Văn bản thông thường",
                1: "1: Văn bia"
            }[x],
            index=config.epitaph,
            key="epitaph_detail"
        )
        config.epitaph = epitaph_detail

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("💾 Lưu cấu hình", use_container_width=True):
            if config.save_config():
                st.success("✅ Lưu cấu hình thành công!")
                st.rerun()
            else:
                st.error("❌ Lỗi khi lưu cấu hình")

    with col2:
        if st.button("🔄 Tải lại mặc định", use_container_width=True):
            config.output_folder = './output'
            config.num_crop_hn = 1
            config.num_crop_qn = 1
            config.ocr_id = 1
            config.lang_type = 0
            config.epitaph = 0
            config.save_config()
            st.success("✅ Đã tải lại mặc định!")
            st.rerun()

    st.markdown("---")
    st.info("""
    📌 **Hướng dẫn:**
    - **Thư mục Output**: Nơi lưu các kết quả xử lý (ảnh, JSON, text)
    - **Số cắt ảnh**: Chia một trang ảnh thành nhiều phần nhỏ để OCR
    - **Loại OCR**: Loại tài liệu (dọc/ngang/hành chính)
    - **Loại ngôn ngữ**: Loại chữ trong tài liệu
    - **Loại văn bản**: Văn bản thường hoặc bia

    Các thay đổi sẽ được lưu tự động khi bạn nhấn "Lưu cấu hình"
    """)

# =================== TAB 7: QUẢN LÝ ===================
elif selected == "📊 Quản lý":
    st.header("📊 Quản lý dữ liệu")

    tab1, tab2, tab3 = st.tabs(["📈 Thống kê", "📋 Kiểm tra", "🗑️ Xóa"])

    with tab1:
        st.subheader("Thống kê trạng thái")
        
        # Draw pipeline
        st.markdown("""
        #### Quy trình xử lý:
        """)
        
        pipeline_stages = [
            ("📥 Trích xuất", status['extracted']),
            ("✂️ Cắt ảnh", status['cropped']),
            ("🔤 OCR QN", status['ocr_vi']),
            ("🈳 OCR HN", status['ocr_nom']),
            ("🔗 Align", status['aligned']),
            ("✏️ Sửa lỗi", status['corrected']),
        ]
        
        cols = st.columns(6)
        for i, (stage, completed) in enumerate(pipeline_stages):
            with cols[i]:
                color = "🟢" if completed else "🔴"
                st.markdown(f"<h4 style='text-align: center;'>{color}<br/>{stage}</h4>", unsafe_allow_html=True)

    with tab2:
        st.subheader("Kiểm tra số trang")
        
        if status['extracted']:
            if st.button("🔍 Kiểm tra"):
                try:
                    handler = DataHandler(config.output_folder, config.name_file_info)
                    pages = handler.check_num_pages()
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Trang Quốc Ngữ", pages['vi'])
                    with col2:
                        st.metric("Trang Hán Nôm", pages['nom'])
                    
                    if pages['vi'] != pages['nom']:
                        st.warning(f"⚠️ Số trang không bằng nhau! QN: {pages['vi']}, HN: {pages['nom']}")
                    else:
                        st.success(f"✅ Số trang bằng nhau: {pages['vi']}")
                
                except Exception as e:
                    st.error(f"❌ Lỗi: {str(e)}")
        else:
            st.info("ℹ️ Vui lòng trích xuất PDF trước!")

    with tab3:
        st.subheader("🗑️ Xóa dữ liệu")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🗑️ Xóa folder output", use_container_width=True):
                if config.clear_output_folder():
                    st.success("✅ Đã xóa folder output!")
                    st.session_state.current_status = config.get_status()
                    st.rerun()
                else:
                    st.error("❌ Lỗi khi xóa")
        
        with col2:
            if st.button("🗑️ Xóa file info", use_container_width=True):
                try:
                    if os.path.exists(config.name_file_info):
                        os.remove(config.name_file_info)
                    st.success("✅ Đã xóa file thông tin!")
                    st.session_state.current_status = config.get_status()
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Lỗi: {str(e)}")
        
        st.markdown("---")
        st.warning("⚠️ Hành động này không thể hoàn tác!")

st.markdown("---")
st.markdown("<p style='text-align: center; color: gray; font-size: 12px;'>OCR Corrector v1.0 | Phát triển 2026</p>", unsafe_allow_html=True)
