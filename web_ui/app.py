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

# Import modern UI components
try:
    from web_ui.ui_components import ModernUIComponents
    from web_ui.styles import get_main_styles
    UI_AVAILABLE = True
except ImportError:
    UI_AVAILABLE = False
    def get_main_styles(): return ""
    class ModernUIComponents:
        @staticmethod
        def render_header(*args, **kwargs): pass
        @staticmethod
        def render_modern_card(*args, **kwargs): pass

# Check if parent modules are available
DEMO_MODE = False
try:
    from web_ui.config_manager import ConfigManager
    from web_ui.data_handler import DataHandler
    from web_ui.ocr_processor import OCRProcessor
    from web_ui.ai_analyst import AIAnalyst, LLMProcessor
    from web_ui.auto_pipeline import AutoPipeline
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

    class AIAnalyst:
        def __init__(self, *args, **kwargs):
            pass

    class LLMProcessor:
        def __init__(self, *args, **kwargs):
            pass

    class AutoPipeline:
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

# Google Material Design inspired CSS
st.markdown(get_main_styles(), unsafe_allow_html=True)

# Sidebar - Google Material style
st.sidebar.markdown("""
<div style='padding: 24px 0; border-bottom: 1px solid #dadce0;'>
    <h2 style='font-family: "Google Sans", sans-serif; font-size: 20px; font-weight: 400; color: #202124; margin: 0 0 4px 0;'>⚙️ Cấu hình</h2>
    <p style='font-family: "Roboto", sans-serif; font-size: 12px; color: #5f6368; margin: 0;'>Quản lý hệ thống</p>
</div>
""", unsafe_allow_html=True)

# Refresh status
# Display info if available
status = st.session_state.current_status or config.get_status()
st.session_state.current_status = status

st.sidebar.markdown("<div style='margin-top: 16px;'></div>", unsafe_allow_html=True)

refresh_col1, refresh_col2 = st.sidebar.columns([1, 1])
with refresh_col1:
    if st.sidebar.button("🔄 Làm mới", key="refresh_status", use_container_width=True):
        st.session_state.current_status = config.get_status()
        st.rerun()

with refresh_col2:
    if st.sidebar.button("🗑️ Xóa", key="clear_all", use_container_width=True):
        try:
            if config.clear_output_folder():
                if os.path.exists(config.name_file_info):
                    os.remove(config.name_file_info)
                st.success("✅ Đã xóa!")
            else:
                st.error("❌ Lỗi")
        except Exception as e:
            st.error(f"Lỗi: {e}")

st.sidebar.markdown("<div style='margin: 16px 0; height: 1px; background-color: #dadce0;'></div>", unsafe_allow_html=True)

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
    st.sidebar.subheader("📊 Trạng thái hệ thống:")
    
    # Status grid with better styling (now included in main styles)
    
    status_items = [
        ("Trích xuất", status.get('extracted', False), "📥"),
        ("Cắt ảnh", status.get('cropped', False), "✂️"),
        ("OCR QN", status.get('ocr_vi', False), "👁️"),
        ("OCR HN", status.get('ocr_nom', False), "👁️"),
        ("Align", status.get('aligned', False), "🔗"),
        ("Sửa lỗi", status.get('corrected', False), "✏️"),
    ]
    
    st.sidebar.markdown("<p style='font-family: \"Roboto\", sans-serif; font-size: 12px; font-weight: 500; color: #5f6368; margin: 16px 0 8px 0; text-transform: uppercase; letter-spacing: 0.5px;'>Trạng thái</p>", unsafe_allow_html=True)
    
    col1, col2 = st.sidebar.columns(2)
    for idx, (title, completed, emoji) in enumerate(status_items):
        col = col1 if idx % 2 == 0 else col2
        status_class = "status-item-done" if completed else "status-item-pending"
        status_icon = "✅" if completed else "⏳"
        with col:
            st.markdown(f"""
            <div class='status-item {status_class}'>
                <div style='font-size: 16px; margin-bottom: 4px;'>{emoji}</div>
                <div style='font-size: 11px; font-weight: 500;'>{title}</div>
                <div style='font-size: 14px; margin-top: 4px;'>{status_icon}</div>
            </div>
            """, unsafe_allow_html=True)

    st.sidebar.markdown("---")

if status.get('info') and not st.session_state.demo_mode:
    st.sidebar.markdown("---")
    st.sidebar.subheader("📋 Thông tin dự án:")
    with st.sidebar.expander("Chi tiết"):
        st.json(status['info'])

st.sidebar.markdown("<div style='margin: 16px 0; height: 1px; background-color: #dadce0;'></div>", unsafe_allow_html=True)

# Main content - Google style header
st.markdown("<h1 class='main-title'>📄 OCR Corrector</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Công cụ xử lý OCR chuyên nghiệp cho Quốc Ngữ & Hán Nôm</p>", unsafe_allow_html=True)

# Show demo mode notice
if st.session_state.demo_mode:
    st.error("""
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

st.markdown("<div style='margin: 24px 0; height: 1px; background-color: #dadce0;'></div>", unsafe_allow_html=True)

# Main menu - Google Material style
st.markdown("""
<div style='margin-bottom: 2rem;'>
    <p style='color: #666; font-weight: bold; margin-bottom: 1rem;'>⭐ Chọn tính năng:</p>
</div>
""", unsafe_allow_html=True)

selected = option_menu(
    menu_title=None,
    options=["📥 Trích xuất PDF", "✂️ Cắt ảnh", "👁️ OCR", "🔗 Align", "✏️ Sửa lỗi", "🚀 Auto Pipeline", "🏷️ Convert Labels", "🤖 AI Analyst", "⚙️ Chi tiết", "📊 Quản lý"],
    icons=["download", "scissors", "eye", "link", "pencil", "rocket", "tags", "robot", "sliders", "gear"],
    orientation="horizontal",
    styles={
        "container": {
            "padding": "4px",
            "background-color": "transparent",
            "border": "none"
        },
        "icon": {"display": "none"},
        "nav-link": {
            "font-family": "'Roboto', sans-serif",
            "font-size": "14px",
            "font-weight": "500",
            "text-align": "center",
            "margin": "0px 4px",
            "padding": "8px 16px",
            "border-radius": "4px",
            "border-bottom": "2px solid transparent",
            "background-color": "transparent",
            "color": "#5f6368",
            "transition": "all 0.3s cubic-bezier(0.4, 0, 0.2, 1)"
        },
        "nav-link-selected": {
            "background-color": "rgba(26, 115, 232, 0.08)",
            "color": "#1a73e8",
            "border-bottom-color": "#1a73e8",
            "font-weight": "500",
            "transform": "scale(1.02)"
        },
    }
)

st.markdown("<div style='margin: 32px 0; height: 1px; background-color: #dadce0;'></div>", unsafe_allow_html=True)

# =================== TAB 1: TRÍCH XUẤT PDF ===================
if selected == "📥 Trích xuất PDF":
    st.markdown("""
    <div class='tab-content'>
        <h2 class='section-header'>Trích xuất PDF thành ảnh</h2>
        <p style='color: #5f6368; margin-bottom: 24px;'>Chuyển đổi các trang PDF thành hình ảnh riêng lẻ để xử lý OCR</p>
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.demo_mode:
        st.info("💡 **Demo Mode**: Parent modules not available. This feature is disabled.")
        st.markdown("To enable, follow the setup instructions in the sidebar.")
    else:
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.markdown("<p class='column-title'>📁 Chọn file PDF</p>", unsafe_allow_html=True)
            uploaded_file = st.file_uploader("Chọn file PDF", type=['pdf'], label_visibility="collapsed")
        
        with col2:
            st.markdown("<p class='column-title'>🔧 Tùy chọn</p>", unsafe_allow_html=True)
            auto_proceed = st.checkbox("Tự động tiếp tục", value=True)
        
        with col3:
            st.markdown("<p class='column-title'>⚡ Hành động</p>", unsafe_allow_html=True)
            if st.button("🗑️ Xóa dữ liệu", key="clear_extract", use_container_width=True):
                try:
                    if config.clear_output_folder():
                        if os.path.exists(config.name_file_info):
                            os.remove(config.name_file_info)
                        st.success("✅ Đã xóa dữ liệu cũ!")
                    else:
                        st.error("❌ Lỗi khi xóa dữ liệu")
                except Exception as e:
                    st.error(f"❌ Lỗi: {e}")
        
        if uploaded_file:
            st.markdown("---")
            
            col_info1, col_info2 = st.columns(2)
            with col_info1:
                st.markdown(f"**📄 File:** `{uploaded_file.name}`")
                st.markdown(f"**💾 Kích thước:** `{uploaded_file.size / 1024:.2f} KB`")
            with col_info2:
                st.markdown(f"**📅 Loại:** `PDF`")
                st.markdown(f"**⏰ Tải lên:** `{datetime.now().strftime('%H:%M:%S')}`")
            
            st.markdown("---")
            
            if st.button("▶️ Bắt đầu trích xuất", use_container_width=True, key="start_extract"):
                progress_bar = st.progress(0)
                status_text = st.empty()
                temp_path = None
                
                def progress_callback(message, current, total):
                    progress_bar.progress(current / (total or 1))
                    status_text.write(f"📝 {message}")
                
                try:
                    os.makedirs("temp", exist_ok=True)
                    temp_path = os.path.join("temp", uploaded_file.name)
                    with open(temp_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())

                    handler = DataHandler(config.output_folder, config.name_file_info)
                    info = handler.extract_pdf(temp_path, progress_callback=progress_callback)
                    
                    st.success("✅ Trích xuất PDF thành công!")
                    st.json(info)
                    
                    st.session_state.current_status = config.get_status()
                    
                except Exception as e:
                    st.error(f"❌ Lỗi trích xuất: {str(e)}")
                finally:
                    if temp_path:
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
    st.markdown("<div class='tab-content'>", unsafe_allow_html=True)
    ModernUIComponents.render_header("Cắt ảnh", "Chia nhỏ hình ảnh thành các đoạn xử lý", "✂️")
    
    ModernUIComponents.render_info_box("💡 Bạn có thể cắt ảnh từ thư mục tùy chỉnh (không cần phải trích xuất PDF trước)", "info")
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Input directories with modern styling
    st.markdown("### 📁 Cấu hình thư mục")
    col1, col2 = st.columns(2)
    with col1:
        vi_dir_crop = st.text_input("📄 Thư mục ảnh Quốc Ngữ", value=config.vi_dir, help="Đường dẫn thư mục chứa ảnh Quốc Ngữ cần cắt")
    with col2:
        nom_dir_crop = st.text_input("🏯 Thư mục ảnh Hán Nôm", value=config.nom_dir, help="Đường dẫn thư mục chứa ảnh Hán Nôm cần cắt")
    
    st.markdown("---")
    
    tab1, tab2 = st.tabs(["✂️ Cắt ảnh thường", "🎯 Edge Detection"])
    
    # Tab 1: Cắt ảnh thường
    with tab1:
        st.markdown("#### ⚙️ Cài đặt số lượng cắt")
        
        col1, col2 = st.columns([1, 1])
        with col1:
            st.markdown("**📄 Quốc Ngữ**")
            num_crop_qn = st.number_input("Số lượng cắt", min_value=1, value=config.num_crop_qn, key="crop_qn", label_visibility="collapsed")
        with col2:
            st.markdown("**🏯 Hán Nôm**")
            num_crop_hn = st.number_input("Số lượng cắt", min_value=1, value=config.num_crop_hn, key="crop_hn", label_visibility="collapsed")
        
        st.markdown("---")
        
        btn_col1, btn_col2 = st.columns([2, 1])
        with btn_col1:
            if st.button("▶️ Bắt đầu cắt ảnh", use_container_width=True, key="crop_start"):
                progress_bar = st.progress(0)
                status_container = st.empty()
                
                def progress_callback(message, current, total):
                    if total > 0:
                        progress_bar.progress(current / total)
                    status_container.markdown(f"<div style='background: #f0f2f6; padding: 1rem; border-radius: 8px;'>📝 {message}</div>", unsafe_allow_html=True)
                
                try:
                    handler = DataHandler(config.output_folder, config.name_file_info)
                    handler.crop_images(num_crop_qn, num_crop_hn, progress_callback=progress_callback)
                    
                    st.success("✅ Cắt ảnh thành công!")
                    st.session_state.current_status = config.get_status()
                    
                except Exception as e:
                    st.error(f"❌ Lỗi: {str(e)}")
    
    # Tab 2: Edge Detection
    with tab2:
        st.markdown("#### 🎯 Cấu hình Edge Detection")
        
        col1, col2 = st.columns(2)
        with col1:
            crop_qn = st.checkbox("📄 Xử lý Quốc Ngữ", value=True)
        with col2:
            crop_hn = st.checkbox("🏯 Xử lý Hán Nôm", value=True)
        
        st.markdown("---")
        
        if st.button("▶️ Bắt đầu xử lý Edge Detection", use_container_width=True):
            progress_bar = st.progress(0)
            status_container = st.empty()
            
            def progress_callback(message, current, total):
                if total > 0:
                    progress_bar.progress(current / total)
                status_container.markdown(f"<div style='background: #f0f2f6; padding: 1rem; border-radius: 8px;'>📝 {message}</div>", unsafe_allow_html=True)
            
            try:
                handler = DataHandler(config.output_folder, config.name_file_info)
                handler.edge_detection_crop(config.vi_model, config.nom_model, crop_qn, crop_hn, progress_callback=progress_callback)
                
                st.success("✅ Xử lý edge detection thành công!")
                st.session_state.current_status = config.get_status()
                
            except Exception as e:
                st.error(f"❌ Lỗi: {str(e)}")

# =================== TAB 3: OCR ===================
elif selected == "👁️ OCR":
    st.markdown("<div class='tab-content'>", unsafe_allow_html=True)
    ModernUIComponents.render_header("Nhận diện ký tự", "Chuyển hình ảnh thành văn bản (OCR)", "👁️")
    
    ModernUIComponents.render_info_box("💡 Bạn có thể chạy OCR từ các thư mục ảnh tùy chỉnh (không cần phải cắt ảnh trước)", "info")
    st.markdown("</div>", unsafe_allow_html=True)

    def warn_if_no_images(dir_path: str, label: str):
        if not dir_path or not os.path.isdir(dir_path):
            return
        files = [f.lower() for f in os.listdir(dir_path)]
        has_images = any(f.endswith((".jpg", ".jpeg", ".png", ".tif", ".tiff", ".bmp")) for f in files)
        has_txt = any(f.endswith(".txt") for f in files)
        if not has_images:
            if has_txt:
                st.warning(f"⚠️ {label} đang trỏ tới thư mục chỉ có .txt, không có ảnh. Vui lòng chọn thư mục ảnh (.jpg/.png).")
            else:
                st.warning(f"⚠️ {label} không thấy ảnh trong thư mục. Vui lòng kiểm tra đường dẫn.")
    
    # Input directories with improved layout
    st.markdown("### 📁 Cấu hình thư mục")
    col1, col2 = st.columns(2)
    with col1:
        vi_dir_ocr = st.text_input(
            "📄 Thư mục ảnh Quốc Ngữ",
            value=config.vi_dir,
            help="Thư mục chứa ảnh Quốc Ngữ cần OCR",
            key="vi_dir_ocr_input"
        )
        
        # Update config if changed
        if vi_dir_ocr and vi_dir_ocr != config.vi_dir:
            config.vi_dir = vi_dir_ocr
            config.save_paths_to_info()
            st.success("✅ Đã lưu path Quốc Ngữ vào before_handle_data.json")
        warn_if_no_images(vi_dir_ocr, "Thư mục ảnh Quốc Ngữ")
    
    with col2:
        nom_dir_ocr = st.text_input(
            "🏯 Thư mục ảnh Hán Nôm",
            value=config.nom_dir,
            help="Thư mục chứa ảnh Hán Nôm cần OCR",
            key="nom_dir_ocr_input"
        )
        
        # Update config if changed
        if nom_dir_ocr and nom_dir_ocr != config.nom_dir:
            config.nom_dir = nom_dir_ocr
            config.save_paths_to_info()
            st.success("✅ Đã lưu path Hán Nôm vào before_handle_data.json")
        warn_if_no_images(nom_dir_ocr, "Thư mục ảnh Hán Nôm")
    
    st.markdown("---")
    
    st.markdown("### ⚙️ Thiết lập OCR Hán Nôm")
    col_ocr1, col_ocr2, col_ocr3 = st.columns(3)
    
    with col_ocr1:
        st.markdown("**🎯 Loại OCR**")
        ocr_id = st.selectbox(
            "Chọn loại",
            options=[1, 2, 3, 4],
            format_func=lambda x: {
                1: "Thông thường dọc",
                2: "Hành chính",
                3: "Ngoại cảnh",
                4: "Thông thường ngang"
            }[x],
            index=config.ocr_id - 1,
            key="ocr_id_select",
            label_visibility="collapsed"
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
            progress_container = st.container()
            
            with progress_container:
                st.markdown("""
                <div style='background: linear-gradient(135deg, rgba(234, 67, 53, 0.05) 0%, rgba(251, 188, 4, 0.05) 100%);
                            backdrop-filter: blur(10px);
                            padding: 24px;
                            border-radius: 12px;
                            border: 2px solid #ea4335;
                            margin: 16px 0;
                            box-shadow: 0 4px 16px rgba(234, 67, 53, 0.15);'>
                    <div style='display: flex; align-items: center; gap: 12px; margin-bottom: 16px;'>
                        <div style='width: 40px; height: 40px; 
                                    background: linear-gradient(135deg, #ea4335 0%, #fbbc04 100%);
                                    border-radius: 50%;
                                    display: flex;
                                    align-items: center;
                                    justify-content: center;
                                    font-size: 20px;
                                    animation: pulse 2s infinite;'>
                            🔤
                        </div>
                        <div>
                            <h4 style='margin: 0; font-family: "Google Sans", sans-serif; color: #202124;'>
                                Đang OCR Quốc Ngữ
                            </h4>
                            <p style='margin: 4px 0 0 0; color: #5f6368; font-size: 13px;'>
                                Đang khởi tạo...
                            </p>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                progress_bar = st.progress(0)
                status_text = st.empty()
            
            def progress_callback(message, current, total):
                progress_pct = current / (total or 1)
                progress_bar.progress(progress_pct)
                
                status_text.markdown(f"""
                <div style='background: white;
                            padding: 16px 20px;
                            border-radius: 8px;
                            border-left: 4px solid #ea4335;
                            margin: 12px 0;
                            box-shadow: 0 2px 8px rgba(0,0,0,0.08);'>
                    <div style='display: flex; justify-content: space-between; align-items: center;'>
                        <div style='flex: 1;'>
                            <div style='color: #5f6368; font-size: 12px; margin-bottom: 4px;'>TIẾN TRÌNH</div>
                            <div style='color: #202124; font-size: 14px; font-family: monospace;'>{message}</div>
                        </div>
                        <div style='text-align: right; margin-left: 16px;'>
                            <div style='font-size: 24px; font-weight: 700; color: #ea4335; font-family: "Google Sans";'>
                                {current}/{total}
                            </div>
                            <div style='font-size: 12px; color: #5f6368;'>
                                {int(progress_pct * 100)}%
                            </div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            try:
                processor = OCRProcessor(config.output_folder, config.name_file_info, config.ocr_id, config.lang_type, config.epitaph)
                processor.ocr_quoc_ngu(progress_callback=progress_callback)
                
                st.markdown("""
                <div style='background: linear-gradient(135deg, #34a853 0%, #0f9d58 100%);
                            padding: 20px;
                            border-radius: 12px;
                            color: white;
                            text-align: center;
                            box-shadow: 0 4px 16px rgba(52, 168, 83, 0.3);
                            margin: 16px 0;'>
                    <div style='font-size: 48px; margin-bottom: 8px;'>✅</div>
                    <div style='font-size: 20px; font-weight: 500; font-family: "Google Sans";'>
                        OCR Quốc Ngữ thành công!
                    </div>
                </div>
                """, unsafe_allow_html=True)
                st.session_state.current_status = config.get_status()
                
            except Exception as e:
                st.error(f"❌ Lỗi: {str(e)}")
    
    with col2:
        if st.button("🈳 OCR Hán Nôm", key="ocr_hn", use_container_width=True):
            # Modern progress container
            progress_container = st.container()
            
            with progress_container:
                st.markdown("""
                <div style='background: linear-gradient(135deg, rgba(66, 133, 244, 0.05) 0%, rgba(52, 168, 83, 0.05) 100%);
                            backdrop-filter: blur(10px);
                            padding: 24px;
                            border-radius: 12px;
                            border: 2px solid #4285f4;
                            margin: 16px 0;
                            box-shadow: 0 4px 16px rgba(66, 133, 244, 0.15);'>
                    <div style='display: flex; align-items: center; gap: 12px; margin-bottom: 16px;'>
                        <div style='width: 40px; height: 40px; 
                                    background: linear-gradient(135deg, #4285f4 0%, #34a853 100%);
                                    border-radius: 50%;
                                    display: flex;
                                    align-items: center;
                                    justify-content: center;
                                    font-size: 20px;
                                    animation: pulse 2s infinite;'>
                            🈳
                        </div>
                        <div>
                            <h4 style='margin: 0; font-family: "Google Sans", sans-serif; color: #202124;'>
                                Đang OCR Hán Nôm
                            </h4>
                            <p id='ocr-status-text' style='margin: 4px 0 0 0; color: #5f6368; font-size: 13px;'>
                                Đang khởi tạo...
                            </p>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                progress_bar = st.progress(0)
                status_text = st.empty()
            
            def progress_callback(message, current, total):
                progress_pct = current / (total or 1)
                progress_bar.progress(progress_pct)
                
                # Beautiful status display
                status_text.markdown(f"""
                <div style='background: white;
                            padding: 16px 20px;
                            border-radius: 8px;
                            border-left: 4px solid #4285f4;
                            margin: 12px 0;
                            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
                            animation: slideIn 0.3s ease-out;'>
                    <div style='display: flex; justify-content: space-between; align-items: center;'>
                        <div style='flex: 1;'>
                            <div style='color: #5f6368; font-size: 12px; margin-bottom: 4px;'>TIẾN TRÌNH</div>
                            <div style='color: #202124; font-size: 14px; font-family: monospace;'>{message}</div>
                        </div>
                        <div style='text-align: right; margin-left: 16px;'>
                            <div style='font-size: 24px; font-weight: 700; color: #4285f4; font-family: "Google Sans";'>
                                {current}/{total}
                            </div>
                            <div style='font-size: 12px; color: #5f6368;'>
                                {int(progress_pct * 100)}%
                            </div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            try:
                processor = OCRProcessor(config.output_folder, config.name_file_info, config.ocr_id, config.lang_type, config.epitaph)
                processor.ocr_han_nom(progress_callback=progress_callback)
                
                st.markdown("""
                <div style='background: linear-gradient(135deg, #34a853 0%, #0f9d58 100%);
                            padding: 20px;
                            border-radius: 12px;
                            color: white;
                            text-align: center;
                            box-shadow: 0 4px 16px rgba(52, 168, 83, 0.3);
                            margin: 16px 0;
                            animation: fadeIn 0.5s ease-out;'>
                    <div style='font-size: 48px; margin-bottom: 8px;'>✅</div>
                    <div style='font-size: 20px; font-weight: 500; font-family: "Google Sans";'>
                        OCR Hán Nôm thành công!
                    </div>
                </div>
                """, unsafe_allow_html=True)
                st.session_state.current_status = config.get_status()
                
            except Exception as e:
                st.error(f"❌ Lỗi: {str(e)}")
    
    with col3:
        if st.button("🔤🈳 OCR Cả hai", key="ocr_both", use_container_width=True):
            progress_container = st.container()
            
            with progress_container:
                st.markdown("""
                <div style='background: linear-gradient(135deg, rgba(103, 58, 183, 0.05) 0%, rgba(156, 39, 176, 0.05) 100%);
                            backdrop-filter: blur(10px);
                            padding: 24px;
                            border-radius: 12px;
                            border: 2px solid #673ab7;
                            margin: 16px 0;
                            box-shadow: 0 4px 16px rgba(103, 58, 183, 0.15);'>
                    <div style='display: flex; align-items: center; gap: 12px; margin-bottom: 16px;'>
                        <div style='width: 40px; height: 40px; 
                                    background: linear-gradient(135deg, #673ab7 0%, #9c27b0 100%);
                                    border-radius: 50%;
                                    display: flex;
                                    align-items: center;
                                    justify-content: center;
                                    font-size: 18px;
                                    animation: pulse 2s infinite;'>
                            🔤🈳
                        </div>
                        <div>
                            <h4 style='margin: 0; font-family: "Google Sans", sans-serif; color: #202124;'>
                                Đang OCR Cả hai
                            </h4>
                            <p style='margin: 4px 0 0 0; color: #5f6368; font-size: 13px;'>
                                Đang khởi tạo...
                            </p>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                progress_bar = st.progress(0)
                status_text = st.empty()
            
            def progress_callback(message, current, total):
                progress_pct = current / (total or 1)
                progress_bar.progress(progress_pct)
                
                status_text.markdown(f"""
                <div style='background: white;
                            padding: 16px 20px;
                            border-radius: 8px;
                            border-left: 4px solid #673ab7;
                            margin: 12px 0;
                            box-shadow: 0 2px 8px rgba(0,0,0,0.08);'>
                    <div style='display: flex; justify-content: space-between; align-items: center;'>
                        <div style='flex: 1;'>
                            <div style='color: #5f6368; font-size: 12px; margin-bottom: 4px;'>TIẾN TRÌNH</div>
                            <div style='color: #202124; font-size: 14px; font-family: monospace;'>{message}</div>
                        </div>
                        <div style='text-align: right; margin-left: 16px;'>
                            <div style='font-size: 24px; font-weight: 700; color: #673ab7; font-family: "Google Sans";'>
                                {current}/{total}
                            </div>
                            <div style='font-size: 12px; color: #5f6368;'>
                                {int(progress_pct * 100)}%
                            </div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            try:
                processor = OCRProcessor(config.output_folder, config.name_file_info, config.ocr_id, config.lang_type, config.epitaph)
                processor.ocr_both(progress_callback=progress_callback)
                
                st.markdown("""
                <div style='background: linear-gradient(135deg, #34a853 0%, #0f9d58 100%);
                            padding: 20px;
                            border-radius: 12px;
                            color: white;
                            text-align: center;
                            box-shadow: 0 4px 16px rgba(52, 168, 83, 0.3);
                            margin: 16px 0;'>
                    <div style='font-size: 48px; margin-bottom: 8px;'>✅</div>
                    <div style='font-size: 20px; font-weight: 500; font-family: "Google Sans";'>
                        OCR cả hai thành công!
                    </div>
                </div>
                """, unsafe_allow_html=True)
                st.session_state.current_status = config.get_status()
                
            except Exception as e:
                st.error(f"❌ Lỗi: {str(e)}")
    
    # ===== OCR Progress Section =====
    st.markdown("---")
    st.markdown("""
    <div style='background: linear-gradient(135deg, rgba(255,255,255,0.95) 0%, rgba(248,249,250,0.95) 100%); 
                backdrop-filter: blur(10px); 
                padding: 24px; 
                border-radius: 12px; 
                border: 1px solid #dadce0; 
                box-shadow: 0 2px 8px rgba(0,0,0,0.08);
                margin: 24px 0;
                animation: fadeIn 0.5s ease-out;'>
        <h3 style='font-family: "Google Sans", sans-serif; 
                   color: #202124; 
                   margin: 0 0 16px 0; 
                   font-weight: 400;
                   display: flex;
                   align-items: center;
                   gap: 8px;'>
            📊 Tiến độ OCR Hán Nôm
        </h3>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🔄 Cập nhật tiến độ", key="refresh_progress", use_container_width=True):
        try:
            processor = OCRProcessor(config.output_folder, config.name_file_info, config.ocr_id, config.lang_type, config.epitaph)
            progress_info = processor.get_ocr_progress()
            
            if progress_info['status'] == 'success':
                # Modern metrics display
                st.markdown("""
                <div style='display: grid; 
                            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); 
                            gap: 16px; 
                            margin: 24px 0;'>
                """, unsafe_allow_html=True)
                
                col_p1, col_p2, col_p3, col_p4 = st.columns(4)
                
                with col_p1:
                    st.markdown(f"""
                    <div style='background: linear-gradient(135deg, #4285f4 0%, #1a73e8 100%); 
                                padding: 20px; 
                                border-radius: 12px; 
                                color: white;
                                box-shadow: 0 4px 12px rgba(66, 133, 244, 0.3);
                                transition: transform 0.3s ease;'>
                        <div style='font-size: 14px; opacity: 0.9; margin-bottom: 8px;'>Đã OCR</div>
                        <div style='font-size: 32px; font-weight: 700; font-family: "Google Sans";'>{progress_info['processed_count']}</div>
                        <div style='font-size: 12px; opacity: 0.8; margin-top: 4px;'>file</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col_p2:
                    st.markdown(f"""
                    <div style='background: linear-gradient(135deg, #34a853 0%, #0f9d58 100%); 
                                padding: 20px; 
                                border-radius: 12px; 
                                color: white;
                                box-shadow: 0 4px 12px rgba(52, 168, 83, 0.3);
                                transition: transform 0.3s ease;'>
                        <div style='font-size: 14px; opacity: 0.9; margin-bottom: 8px;'>Tổng cộng</div>
                        <div style='font-size: 32px; font-weight: 700; font-family: "Google Sans";'>{progress_info['total_count']}</div>
                        <div style='font-size: 12px; opacity: 0.8; margin-top: 4px;'>file</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col_p3:
                    progress_percent = progress_info['progress_percent']
                    color = '#34a853' if progress_percent == 100 else '#fbbc04' if progress_percent > 50 else '#ea4335'
                    st.markdown(f"""
                    <div style='background: linear-gradient(135deg, {color} 0%, {color}dd 100%); 
                                padding: 20px; 
                                border-radius: 12px; 
                                color: white;
                                box-shadow: 0 4px 12px rgba(255, 193, 7, 0.3);
                                transition: transform 0.3s ease;'>
                        <div style='font-size: 14px; opacity: 0.9; margin-bottom: 8px;'>Tiến độ</div>
                        <div style='font-size: 32px; font-weight: 700; font-family: "Google Sans";'>{progress_percent}%</div>
                        <div style='font-size: 12px; opacity: 0.8; margin-top: 4px;'>hoàn thành</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col_p4:
                    if progress_info['unprocessed_file']:
                        st.markdown(f"""
                        <div style='background: linear-gradient(135deg, rgba(26, 115, 232, 0.1) 0%, rgba(66, 133, 244, 0.05) 100%); 
                                    padding: 20px; 
                                    border-radius: 12px; 
                                    border: 2px solid #4285f4;
                                    transition: transform 0.3s ease;'>
                            <div style='font-size: 14px; color: #1a73e8; margin-bottom: 8px; font-weight: 500;'>Tiếp theo</div>
                            <div style='font-size: 13px; color: #5f6368; font-family: monospace; 
                                        overflow: hidden; text-overflow: ellipsis; white-space: nowrap;' 
                                 title='{progress_info['unprocessed_file']}'>{progress_info['unprocessed_file']}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown("""
                        <div style='background: linear-gradient(135deg, #34a853 0%, #0f9d58 100%); 
                                    padding: 20px; 
                                    border-radius: 12px; 
                                    color: white;
                                    box-shadow: 0 4px 12px rgba(52, 168, 83, 0.3);
                                    text-align: center;'>
                            <div style='font-size: 40px; margin-bottom: 8px;'>✅</div>
                            <div style='font-size: 16px; font-weight: 500;'>Hoàn thành!</div>
                        </div>
                        """, unsafe_allow_html=True)
                
                st.markdown("</div>", unsafe_allow_html=True)
                
                # Beautiful progress bar
                st.markdown(f"""
                <div style='margin: 32px 0 24px 0;'>
                    <div style='background: #e8eaed; 
                                height: 12px; 
                                border-radius: 6px; 
                                overflow: hidden;
                                box-shadow: inset 0 1px 3px rgba(0,0,0,0.1);'>
                        <div style='background: linear-gradient(90deg, #4285f4 0%, #34a853 100%); 
                                    height: 100%; 
                                    width: {progress_percent}%; 
                                    border-radius: 6px;
                                    transition: width 0.6s cubic-bezier(0.4, 0, 0.2, 1);
                                    box-shadow: 0 2px 8px rgba(66, 133, 244, 0.4);
                                    position: relative;
                                    overflow: hidden;'>
                            <div style='position: absolute;
                                        top: 0;
                                        left: 0;
                                        bottom: 0;
                                        right: 0;
                                        background: linear-gradient(90deg, 
                                                                    transparent 0%, 
                                                                    rgba(255,255,255,0.3) 50%, 
                                                                    transparent 100%);
                                        animation: shimmer 2s infinite;'>
                            </div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                unprocessed_files = progress_info.get('unprocessed_files', [])
                unprocessed_count = progress_info.get('unprocessed_count', len(unprocessed_files))

                if unprocessed_count > 0:
                    st.markdown(f"""
                    <div style='background: rgba(251, 188, 4, 0.08);
                                border: 1px solid rgba(251, 188, 4, 0.35);
                                border-radius: 10px;
                                padding: 14px 16px;
                                margin: 8px 0 12px 0;'>
                        <div style='font-weight: 600; color: #5f6368;'>📌 Ảnh chưa OCR: {unprocessed_count} file</div>
                    </div>
                    """, unsafe_allow_html=True)

                    with st.expander("Xem danh sách tên file chưa OCR", expanded=True):
                        st.text_area(
                            "Danh sách file",
                            value="\n".join(unprocessed_files),
                            height=260,
                            disabled=True,
                            label_visibility="collapsed"
                        )
                else:
                    st.success("✅ Không còn file ảnh nào chưa OCR.")
            else:
                st.warning(f"⚠️ {progress_info['status']}")
        except Exception as e:
            st.error(f"❌ Lỗi: {str(e)}")
    
    st.markdown("---")
    st.subheader("📁 Tách ảnh đã OCR")
    st.info("""
    Tính năng này sẽ:
    - Tách ảnh đã OCR từ thư mục gốc
    - Tạo 2 thư mục riêng: **image** (ảnh gốc) và **ocr** (file .json)
    - Chỉ copy ảnh có file .json tương ứng
    """)
    
    if st.button("📦 Tách ảnh đã OCR", key="extract_images", use_container_width=True):
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        def extract_progress_callback(message, current, total):
            progress_bar.progress(current / (total or 1))
            status_text.write(f"📝 {message}")
        
        try:
            processor = OCRProcessor(config.output_folder, config.name_file_info, config.ocr_id, config.lang_type, config.epitaph)
            processor.extract_processed_images(progress_callback=extract_progress_callback)
            
            st.success("✅ Tách ảnh thành công!")
            st.info("""
            ✨ Kết quả:
            - 📁 **image/**: Chứa các ảnh đã OCR
            - 📁 **ocr/**: Chứa các file .json tương ứng
            
            Các file được tổ chức tại: `output_folder/extracted/`
            """)
        except Exception as e:
            st.error(f"❌ Lỗi: {str(e)}")

# =================== TAB 4: ALIGN ===================
elif selected == "🔗 Align":
    st.markdown("<div class='tab-content'>", unsafe_allow_html=True)
    ModernUIComponents.render_header("Căn chỉnh Text", "Align văn bản từ hai nguồn OCR", "🔗")
    
    ModernUIComponents.render_info_box("""
    🎯 **Hướng dẫn sử dụng:**
    • Truyền 2 thư mục: một chứa JSON Hán Nôm, một chứa TXT Quốc Ngữ
    • Các file phải có cùng tên cơ sở (ví dụ: `image_001.json` và `image_001.txt`)
    • Nếu file TXT không tìm thấy, file đó sẽ bị bỏ qua
    """, "info")
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Đọc thông tin từ config
    processor = OCRProcessor(config.output_folder, config.name_file_info)
    info = None
    try:
        info = processor.read_file_info()
        default_json_path = info.get('ocr_json_nom', config.ocr_json_nom or '')
        default_txt_path = info.get('ocr_txt_qn', config.ocr_txt_qn or '')
        default_align_param = info.get('align_param', 1)
        default_reverse = info.get('align_reverse', False)
        default_mapping_path = info.get('mapping_path', '')
        file_name = info.get('file_name', '')
    except:
        default_json_path = config.ocr_json_nom or ''
        default_txt_path = config.ocr_txt_qn or ''
        default_align_param = 1
        default_reverse = False
        default_mapping_path = ''
        file_name = ''
    
    # Display current file info
    if file_name:
        st.markdown(f"<div style='background: #e3f2fd; padding: 1rem; border-radius: 8px; border-left: 4px solid #667eea; margin-bottom: 1rem;'><strong>📖 Tên file:</strong> {file_name}</div>", unsafe_allow_html=True)
    
    st.markdown("### 📁 Cấu hình đường dẫn")
    col1, col2 = st.columns(2)
    with col1:
        ocr_json_nom_align = st.text_input(
            "🏯 JSON Hán Nôm", 
            value=default_json_path, 
            help="Thư mục chứa file JSON từ nom OCR",
            key="ocr_json_nom_align"
        )
    with col2:
        ocr_txt_qn_align = st.text_input(
            "📄 TXT Quốc Ngữ", 
            value=default_txt_path, 
            help="Thư mục chứa file TXT từ vi OCR",
            key="ocr_txt_qn_align"
        )
    
    st.markdown("---")
    
    # Chọn k=1 hoặc k=2
    st.subheader("⚙️ Cấu hình Align")

    # Align type selection
    align_type = st.selectbox(
        "Loại Align",
        options=["Hán Nôm ↔ Quốc Ngữ (từ điển)", "Cùng ngôn ngữ (không từ điển)"],
        index=0,
        help="• 'Hán Nôm ↔ Quốc Ngữ': Dùng từ điển để align, xuất file .txt\n• 'Cùng ngôn ngữ': Không dùng từ điển (ví dụ so khớp 2 nguồn cùng tiếng Việt/Hán Nôm), xuất file .xlsx"
    )
    
    # Display output format info
    if align_type == "Cùng ngôn ngữ (không từ điển)":
        st.info("📊 **Output format:** File Excel (.xlsx) với các cột: ID, File Name, bbox, OCR, SinomChar, rate")
    else:
        st.info("📝 **Output format:** File Text (.txt) với định dạng đặc biệt cho bước xử lý tiếp theo")
    
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
        # Modern progress container
        progress_container = st.container()
        
        with progress_container:
            st.markdown("""
            <div style='background: linear-gradient(135deg, rgba(103, 58, 183, 0.05) 0%, rgba(156, 39, 176, 0.05) 100%);
                        backdrop-filter: blur(10px);
                        padding: 24px;
                        border-radius: 12px;
                        border: 2px solid #673ab7;
                        margin: 16px 0;
                        box-shadow: 0 4px 16px rgba(103, 58, 183, 0.15);'>
                <div style='display: flex; align-items: center; gap: 12px; margin-bottom: 16px;'>
                    <div style='width: 40px; height: 40px; 
                                background: linear-gradient(135deg, #673ab7 0%, #9c27b0 100%);
                                border-radius: 50%;
                                display: flex;
                                align-items: center;
                                justify-content: center;
                                font-size: 20px;
                                animation: pulse 2s infinite;'>
                        🔗
                    </div>
                    <div>
                        <h4 style='margin: 0; font-family: "Google Sans", sans-serif; color: #202124;'>
                            Đang Align văn bản
                        </h4>
                        <p style='margin: 4px 0 0 0; color: #5f6368; font-size: 13px;'>
                            Đang xử lý...
                        </p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            progress_bar = st.progress(0)
            status_text = st.empty()
        
        def progress_callback(message, current, total):
            if total > 0:
                progress_pct = current / total
                progress_bar.progress(progress_pct)
                
                # Beautiful status display
                status_text.markdown(f"""
                <div style='background: white;
                            padding: 16px 20px;
                            border-radius: 8px;
                            border-left: 4px solid #673ab7;
                            margin: 12px 0;
                            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
                            animation: slideIn 0.3s ease-out;'>
                    <div style='display: flex; justify-content: space-between; align-items: center;'>
                        <div style='flex: 1;'>
                            <div style='color: #5f6368; font-size: 12px; margin-bottom: 4px;'>TIẾN TRÌNH</div>
                            <div style='color: #202124; font-size: 14px; font-family: monospace;'>{message}</div>
                        </div>
                        <div style='text-align: right; margin-left: 16px;'>
                            <div style='font-size: 24px; font-weight: 700; color: #673ab7; font-family: "Google Sans";'>
                                {current}/{total}
                            </div>
                            <div style='font-size: 12px; color: #5f6368;'>
                                {int(progress_pct * 100)}%
                            </div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                # No total available, just show message
                status_text.markdown(f"""
                <div style='background: white;
                            padding: 16px 20px;
                            border-radius: 8px;
                            border-left: 4px solid #673ab7;
                            margin: 12px 0;
                            box-shadow: 0 2px 8px rgba(0,0,0,0.08);'>
                    <div style='color: #5f6368; font-size: 12px; margin-bottom: 4px;'>TIẾN TRÌNH</div>
                    <div style='color: #202124; font-size: 14px; font-family: monospace;'>{message}</div>
                </div>
                """, unsafe_allow_html=True)
        
        try:
            # Lấy paths từ input, nếu rỗng thì lấy từ config
            json_path = ocr_json_nom_align.strip() if ocr_json_nom_align.strip() else None
            txt_path = ocr_txt_qn_align.strip() if ocr_txt_qn_align.strip() else None
            # Output path depends on align type
            if align_type == "Cùng ngôn ngữ (không từ điển)":
                output_path = os.path.join(config.output_folder, 'result_han.xlsx')
            else:
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
            
            if align_type == "Cùng ngôn ngữ (không từ điển)":
                processor.align_text_same_language(
                    left_json_dir=json_path,
                    right_txt_dir=txt_path,
                    output_txt=output_path,
                    align_param=align_param,
                    name_book=file_name,
                    reverse=reverse_nom if align_param == 1 else False,
                    mapping_path=mapping_path,
                    progress_callback=progress_callback
                )
            else:
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
            if align_type == "Cùng ngôn ngữ (không từ điển)":
                abs_output_path = os.path.abspath(output_path)
                st.markdown(f"""
                <div style='background: linear-gradient(135deg, #34a853 0%, #0f9d58 100%);
                            padding: 20px;
                            border-radius: 12px;
                            color: white;
                            margin: 16px 0;
                            box-shadow: 0 4px 16px rgba(52, 168, 83, 0.3);'>
                    <div style='font-size: 16px; margin-bottom: 8px;'>📊 File Excel đã lưu:</div>
                    <div style='font-family: monospace; font-size: 14px; background: rgba(255,255,255,0.2); 
                                padding: 8px 12px; border-radius: 6px; margin-top: 8px;'>{abs_output_path}</div>
                </div>
                """, unsafe_allow_html=True)
                skip_report = os.path.join(config.output_folder, 'align_han_skip_report.txt')
                if os.path.exists(skip_report):
                    abs_skip_report = os.path.abspath(skip_report)
                    st.markdown(f"""
                    <div style='background: linear-gradient(135deg, rgba(251, 188, 4, 0.1) 0%, rgba(251, 188, 4, 0.05) 100%);
                                padding: 16px;
                                border-radius: 8px;
                                border-left: 4px solid #fbbc04;
                                margin: 16px 0;'>
                        <div style='color: #b06000; font-weight: 500; margin-bottom: 4px;'>📝 Báo cáo bỏ qua:</div>
                        <div style='font-family: monospace; font-size: 13px; color: #5f6368;'>{abs_skip_report}</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.success("✅ Không có file nào bị bỏ qua!")
            else:
                abs_output_path = os.path.abspath(output_path)
                st.markdown(f"""
                <div style='background: linear-gradient(135deg, #4285f4 0%, #1a73e8 100%);
                            padding: 20px;
                            border-radius: 12px;
                            color: white;
                            margin: 16px 0;
                            box-shadow: 0 4px 16px rgba(66, 133, 244, 0.3);'>
                    <div style='font-size: 16px; margin-bottom: 8px;'>📝 File TXT đã lưu:</div>
                    <div style='font-family: monospace; font-size: 14px; background: rgba(255,255,255,0.2); 
                                padding: 8px 12px; border-radius: 6px; margin-top: 8px;'>{abs_output_path}</div>
                    <div style='font-size: 12px; margin-top: 12px; opacity: 0.9;'>
                        💡 File này sẽ được dùng cho bước "Sửa lỗi" tiếp theo
                    </div>
                </div>
                """, unsafe_allow_html=True)
            st.session_state.current_status = config.get_status()
            
        except Exception as e:
            error_msg = str(e)
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, rgba(234, 67, 53, 0.1) 0%, rgba(234, 67, 53, 0.05) 100%);
                        padding: 20px;
                        border-radius: 12px;
                        border-left: 4px solid #ea4335;
                        margin: 16px 0;'>
                <div style='color: #c5221f; font-weight: 600; font-size: 18px; margin-bottom: 12px;'>
                    ❌ Lỗi khi align
                </div>
                <div style='background: white; padding: 12px; border-radius: 6px; margin-top: 8px;'>
                    <div style='color: #5f6368; font-size: 12px; margin-bottom: 4px;'>CHI TIẾT LỖI:</div>
                    <div style='font-family: monospace; font-size: 13px; color: #ea4335;'>{error_msg}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Thêm hướng dẫn debug
            if "'details'" in error_msg:
                st.markdown("""
                <div style='background: #e3f2fd; padding: 16px; border-radius: 8px; margin: 12px 0; border-left: 4px solid #2196f3;'>
                    <div style='color: #1565c0; font-weight: 500; margin-bottom: 8px;'>💡 Gợi ý khắc phục:</div>
                    <div style='color: #424242; font-size: 14px; line-height: 1.6;'>
                        • Lỗi này xảy ra khi JSON file có cấu trúc không đúng<br>
                        • Kiểm tra file JSON có cấu trúc: <code>{'data': {'details': {'details': [...]}}}</code><br>
                        • Hoặc: <code>{'data': {'result_bbox': [...]}}</code><br>
                        • Đảm bảo files JSON được tạo từ OCR Hán Nôm đúng format
                    </div>
                </div>
                """, unsafe_allow_html=True)

# =================== TAB 5: SỬA LỖI ===================
elif selected == "✏️ Sửa lỗi":
    ModernUIComponents.render_header("Sửa lỗi & Excel", "Sửa lỗi OCR và tạo file Excel", "✏️")
    
    ModernUIComponents.render_info_box("💡 Chạy sửa lỗi từ file TXT tùy chỉnh (không cần phải Align trước)", "info")
    
    st.markdown("### 📁 Cấu hình")
    output_txt_correct = st.text_input("📄 File TXT Align", value=config.output_folder, help="Đường dẫn file TXT từ quá trình align", key="output_txt_correct")
    
    st.markdown("---")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        debug_mode = st.checkbox("🐛 Chế độ Debug", value=False)
    
    if st.button("▶️ Bắt đầu sửa lỗi", use_container_width=True):
        progress_bar = st.progress(0)
        status_container = st.empty()
        
        def progress_callback(message, current, total):
            progress_bar.progress(current / (total or 1))
            status_container.markdown(f"<div style='background: #f0f2f6; padding: 1rem; border-radius: 8px;'>📝 {message}</div>", unsafe_allow_html=True)
        
        try:
            processor = OCRProcessor(config.output_folder, config.name_file_info)
            processor.correct_text(debug=debug_mode, progress_callback=progress_callback)
            
            st.success("✅ Sửa lỗi thành công!")
            st.session_state.current_status = config.get_status()
            
        except Exception as e:
            st.error(f"❌ Lỗi: {str(e)}")

# =================== TAB: AUTO PIPELINE ===================
elif selected == "🚀 Auto Pipeline":
    st.markdown("<div class='tab-content'>", unsafe_allow_html=True)
    ModernUIComponents.render_header("Auto Pipeline", "Tự động hóa toàn bộ quy trình với AI", "🚀")
    st.markdown("</div>", unsafe_allow_html=True)

    st.info("💡 Pipeline tự động: PDF -> Cắt ảnh -> OCR -> AI Alignment -> Excel Dataset")

    # 1. Config AI
    with st.expander("⚙️ Cấu hình AI Model", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            hf_token_pipe = st.text_input(
                "Hugging Face Token",
                type="password",
                value=os.getenv("HF_API_TOKEN", ""),
                key="pipe_token"
            )
        with col2:
            model_id_pipe = st.text_input(
                "Model ID",
                value=os.getenv("HF_MODEL_ID", "meta-llama/Llama-2-7b-chat-hf"),
                key="pipe_model"
            )
        if hf_token_pipe:
            st.caption("✅ LLM: Đang dùng Hugging Face Inference API")
        else:
            st.caption("⚠️ LLM: Chưa có token, sẽ dùng chế độ Mock/Heuristic")

    # 2. Input PDF
    st.markdown("### 📄 Đầu vào PDF")
    pdf_file_pipe = st.file_uploader("Upload PDF song ngữ", type=['pdf'], key="pipe_pdf")

    # 3. Strategy
    st.markdown("### 📐 Chiến lược xử lý")

    layout_mode = st.radio("Chế độ phân tích", ["AI Auto-Detect", "Manual Strategy"], horizontal=True)

    manual_layout_type = "Full Page"
    if layout_mode == "Manual Strategy":
        manual_layout_type = st.selectbox(
            "Bố cục trang PDF (Thủ công)",
            options=["Split Vertical", "Split Horizontal", "Full Page"],
            help="Chọn cách chia trang nếu văn bản song ngữ được trình bày song song."
        )
    else:
        st.info("🤖 AI sẽ tự động phân tích từng trang để quyết định cách cắt ảnh và xử lý tối ưu nhất.")

    if st.button("🚀 Chạy Pipeline", type="primary"):
        if not pdf_file_pipe:
            st.error("Vui lòng upload file PDF!")
        else:
            # Save PDF temporarily
            temp_pdf = os.path.join("temp", pdf_file_pipe.name)
            os.makedirs("temp", exist_ok=True)
            with open(temp_pdf, "wb") as f:
                f.write(pdf_file_pipe.getbuffer())

            # Init components
            llm_proc = LLMProcessor(api_token=hf_token_pipe or None, model_id=model_id_pipe)
            pipeline = AutoPipeline(config.output_folder, config.name_file_info)

            # Progress UI
            progress_bar = st.progress(0)
            status_text = st.empty()

            def pipe_callback(msg, curr, total):
                if total > 0:
                    progress_bar.progress(curr / total)
                status_text.markdown(f"**Status:** {msg}")

            try:
                result_path = pipeline.run_pipeline(
                    temp_pdf,
                    layout_mode,
                    llm_proc,
                    manual_layout_type=manual_layout_type,
                    progress_callback=pipe_callback
                )

                st.success("✅ Pipeline hoàn thành xuất sắc!")
                st.markdown(f"### 📥 Kết quả: `{result_path}`")

                # Preview Result
                if os.path.exists(result_path):
                    df_res = pd.read_excel(result_path)
                    st.dataframe(df_res.head(10))

            except Exception as e:
                st.error(f"❌ Lỗi Pipeline: {e}")
                import traceback
                st.error(traceback.format_exc())


# =================== TAB 6: CONVERT LABELS ===================
elif selected == "🏷️ Convert Labels":
    st.markdown("<div class='tab-content'>", unsafe_allow_html=True)
    ModernUIComponents.render_header("Convert Labels", "Chuyển đổi sang PaddleOCR Labels", "🏷️")
    st.markdown("</div>", unsafe_allow_html=True)
    
    import pandas as pd
    from web_ui.convert_to_labels import (
        read_excel_any, read_excel_columns,
        convert_data_to_labeltxt, create_filestate_txt,
        validate_image_sizes
    )
    
    ModernUIComponents.render_feature_grid([
        {"icon": "📤", "title": "Upload Excel", "description": "Tải file dữ liệu OCR", "color": "#667eea"},
        {"icon": "🔍", "title": "Kiểm tra", "description": "Xác minh dữ liệu", "color": "#764ba2"},
        {"icon": "🏷️", "title": "Tạo Label", "description": "Generate PaddleOCR labels", "color": "#f093fb"},
    ])
    
    st.markdown("---")
    
    # Step 1: Upload Excel file
    st.markdown("### 📤 Bước 1: Upload file Excel")
    
    # Option 1: Upload file
    col1, col2 = st.columns([3, 1])
    with col1:
        excel_file = st.file_uploader(
            "Chọn file Excel (.xlsx, .xls)", 
            type=["xlsx", "xls"],
            accept_multiple_files=False,
            label_visibility="collapsed"
        )
    
    with col2:
        st.write("")  # spacing
        st.write("")  # spacing
        use_path = st.checkbox("📝 Nhập đường dẫn", value=False)
    
    # Option 2: File path input
    file_path_input = None
    if use_path:
        file_path_input = st.text_input(
            "Đường dẫn file Excel",
            help="Ví dụ: D:/path/to/result_han.xlsx",
            label_visibility="collapsed"
        )
    
    # Determine which source to use
    df = None
    if excel_file or file_path_input:
        # Read Excel with engine detection (openpyxl/xlrd)
        try:
            if file_path_input:
                # Read from file path
                df = read_excel_any(file_path_input)
            else:
                # Read from uploaded file
                df = read_excel_any(excel_file)
        except ImportError as e:
            st.error(f"❌ {e}")
            st.info("Chạy trong môi trường ảo đang kích hoạt:")
            st.code("pip install openpyxl xlrd>=2.0.1", language="bash")
            st.stop()
        except FileNotFoundError:
            st.error("❌ Không tìm thấy file! Kiểm tra lại đường dẫn.")
            st.stop()
        except Exception as e:
            st.error(f"❌ Lỗi đọc file: {e}")
            st.stop()
        
        
        columns = df.columns.tolist()
        
        st.success(f"✅ Đã load {len(df)} rows, {len(columns)} columns")
        
        # Step 2: Column mapping
        st.subheader("🔍 Bước 2: Chọn cột tương ứng")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            image_name_col = st.selectbox(
                "Cột Tên Ảnh (_ImageName_Column)",
                options=columns,
                help="Cột chứa tên file ảnh"
            )
        
        with col2:
            bbox_col = st.selectbox(
                "Cột BBox (_PositionBBoxName_Column)",
                options=columns,
                help="Cột chứa tọa độ bounding box"
            )
        
        with col3:
            ocr_col = st.selectbox(
                "Cột OCR Text (_OCRName_Column)",
                options=columns,
                help="Cột chứa text OCR"
            )
        
        st.info("💡 Xem trước 5 rows:")
        st.dataframe(df[[image_name_col, bbox_col, ocr_col]].head())
        
        # Step 3: Check folder paths
        st.subheader("📁 Bước 3: Kiểm tra thư mục")
        
        base_dir = Path(config.output_folder)
        extracted_image_dir = base_dir / "extracted" / "image"
        json_dir = base_dir / "ocr" / "Han_Nom_ocr"  # JSON folder
        
        col1, col2 = st.columns(2)
        
        with col1:
            if extracted_image_dir.exists():
                num_images = len(list(extracted_image_dir.glob("*.jpg")))
                st.success(f"✅ Thư mục extracted/image (.jpg): {num_images} ảnh")
            else:
                st.error(f"❌ Thư mục extracted/image không tồn tại!\n**Path:** {extracted_image_dir}")
                st.info("💡 Đây là nơi chứa file .jpg ảnh")
        
        with col2:
            if json_dir.exists():
                num_json = len(list(json_dir.glob("*.json")))
                st.success(f"✅ Thư mục ocr/Han_Nom_ocr (.json): {num_json} file")
            else:
                st.warning(f"⚠️ Thư mục ocr/Han_Nom_ocr không tồn tại!")
                st.info("💡 Nhập đường dẫn folder JSON nếu khác")
                json_dir = st.text_input(
                    "Hoặc nhập đường dẫn folder JSON",
                    value=str(json_dir),
                    help="Ví dụ: D:/path/to/ocr/Han_Nom_ocr"
                )
                if json_dir:
                    json_dir = Path(json_dir)
        
        # Step 4: Validate files (optional)
        st.subheader("🔍 Bước 4: Kiểm tra file (tùy chọn)")
        
        if extracted_image_dir.exists() and json_dir.exists():
            if st.button("🔍 Validate File", use_container_width=True):
                with st.spinner("Đang kiểm tra..."):
                    image_names = df[image_name_col].unique().tolist()
                    validation_results = validate_image_sizes(
                        str(extracted_image_dir),
                        str(json_dir),
                        image_names
                    )
                
                # Show results
                valid_count = sum(1 for v in validation_results.values() if v['valid'])
                st.write(f"**Kết quả:** {valid_count}/{len(validation_results)} ảnh hợp lệ")
                
                # Show valid images
                valid_images = [img for img, res in validation_results.items() if res['valid']]
                if valid_images:
                    with st.expander("✅ Ảnh hợp lệ", expanded=False):
                        for img in valid_images[:10]:
                            st.write(f"  ✓ {img}")
                        if len(valid_images) > 10:
                            st.write(f"  ... và {len(valid_images) - 10} ảnh khác")
                
                # Show invalid images
                invalid_images = {img: res for img, res in validation_results.items() if not res['valid']}
                if invalid_images:
                    with st.expander(f"❌ Ảnh không hợp lệ ({len(invalid_images)})", expanded=True):
                        for img, res in list(invalid_images.items())[:20]:
                            st.write(f"  ✗ {img}: {res['reason']}")
                        if len(invalid_images) > 20:
                            st.write(f"  ... và {len(invalid_images) - 20} ảnh khác")
                
                st.session_state['validation_results'] = validation_results
        
        # Step 5: Convert to labels
        st.subheader("🏷️ Bước 5: Convert to Labels")
        
        st.info("💡 Bạn có thể convert ngay mà không cần validate ảnh. Validation chỉ để kiểm tra trước.")
        
        if st.button("🏷️ Tạo Label.txt", use_container_width=True, type="primary"):
            try:
                output_dir = base_dir / "check_label" / "images_label"
                
                with st.spinner("Đang convert..."):
                    # Filter only valid images nếu có validation results
                    df_to_convert = df.copy()
                    
                    if 'validation_results' in st.session_state:
                        valid_images = [
                            img for img, res in st.session_state['validation_results'].items()
                            if res['valid']
                        ]
                        df_to_convert = df_to_convert[
                            df_to_convert[image_name_col].isin(valid_images)
                        ]
                        st.info(f"💡 Convert chỉ {len(df_to_convert)} rows (có ảnh hợp lệ)")
                    else:
                        st.info(f"💡 Convert tất cả {len(df_to_convert)} rows (không validate trước)")
                    
                    # Convert without checking image existence
                    image_names, validation_results = convert_data_to_labeltxt(
                        df_to_convert,
                        str(extracted_image_dir) if extracted_image_dir.exists() else "",
                        str(output_dir),
                        image_name_col=image_name_col,
                        bbox_col=bbox_col,
                        ocr_col=ocr_col,
                        file_name_prefix="extracted"
                    )
                    
                    # Create fileState.txt
                    filestate_path = create_filestate_txt(
                        str(output_dir),
                        image_names,
                        file_name_prefix="extracted"
                    )
                
                st.success(f"✅ Đã tạo {len(image_names)} items!")
                st.info(f"📁 **Output folders:**\n- `{output_dir / 'Label.txt'}`\n- `{output_dir / 'fileState.txt'}`")
                
                # Show sample
                with st.expander("📋 Xem mẫu Label.txt", expanded=False):
                    with open(output_dir / "Label.txt", "r", encoding="utf-8") as f:
                        sample = "\n".join(f.readlines()[:5])
                    st.code(sample, language="text")
            
            except Exception as e:
                st.error(f"❌ Lỗi: {e}")
                import traceback
                st.error(traceback.format_exc())

# =================== TAB 7: AI ANALYST ===================
elif selected == "🤖 AI Analyst":
    st.markdown("<div class='tab-content'>", unsafe_allow_html=True)
    ModernUIComponents.render_header("AI Analyst", "Phân tích và Tự động làm sạch Dữ liệu", "🤖")
    st.markdown("</div>", unsafe_allow_html=True)

    st.info("💡 Tính năng này sử dụng AI để tự động phát hiện và sửa lỗi trong dữ liệu OCR của bạn.")

    # Configuration Section
    with st.expander("⚙️ Cấu hình LLM (Hugging Face)", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            hf_token = st.text_input(
                "Hugging Face API Token",
                type="password",
                value=os.getenv("HF_API_TOKEN", ""),
                help="Nhập token của bạn để sử dụng model thật. Để trống để dùng chế độ Demo (Mock)."
            )
        with col2:
            model_id = st.text_input(
                "Model ID",
                value=os.getenv("HF_MODEL_ID", "meta-llama/Llama-2-7b-chat-hf"),
                help="Ví dụ: 'meta-llama/Llama-2-7b-chat-hf' hoặc 'Qwen/Qwen-7B'"
            )
        if hf_token:
            st.caption("✅ LLM: Đang dùng Hugging Face Inference API")
        else:
            st.caption("⚠️ LLM: Chưa có token, sẽ dùng chế độ Mock/Heuristic")

    # Initialize classes
    llm_processor = LLMProcessor(api_token=hf_token or None, model_id=model_id)

    # File Selection
    st.markdown("### 📂 Chọn dữ liệu đầu vào")

    col1, col2 = st.columns([3, 1])
    with col1:
        default_file = os.path.join(config.output_folder, "result.xlsx")
        input_file = st.text_input("Đường dẫn file Excel/CSV", value=default_file if os.path.exists(default_file) else "")

    with col2:
        uploaded_file = st.file_uploader("Upload File", type=['xlsx', 'xls', 'csv'], label_visibility="collapsed")

    # Load Data
    analyst = None
    if uploaded_file:
        # Save uploaded file temporarily
        temp_path = os.path.join("temp", uploaded_file.name)
        os.makedirs("temp", exist_ok=True)
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        analyst = AIAnalyst(temp_path)
        st.success(f"✅ Đã tải file: {uploaded_file.name}")
    elif input_file and os.path.exists(input_file):
        analyst = AIAnalyst(input_file)
        st.success(f"✅ Đã tải file: {input_file}")

    # Analysis & Cleaning
    if analyst and analyst.df is not None:
        tab1, tab2 = st.tabs(["📊 Phân tích", "✨ Tự động làm sạch"])

        with tab1:
            stats = analyst.get_statistics()
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Tổng số dòng", stats.get('rows', 0))
            with col2:
                st.metric("Số cột", len(stats.get('columns', [])))
            with col3:
                st.metric("Dòng trùng lặp", stats.get('duplicates', 0))

            st.markdown("#### 📉 Missing Values")
            st.bar_chart(stats.get('missing_values', {}))

            st.markdown("#### 📋 Preview Dữ liệu")
            st.dataframe(analyst.df.head())

        with tab2:
            st.markdown("#### 🛠️ Pipeline Tự động")

            # Column selection
            cols = analyst.df.columns.tolist()
            target_cols = st.multiselect("Chọn cột cần làm sạch (OCR Correction)", options=cols, default=[cols[0]] if cols else [])

            if st.button("🚀 Chạy AI Cleaning", type="primary"):
                if not target_cols:
                    st.warning("Vui lòng chọn ít nhất một cột!")
                else:
                    progress_bar = st.progress(0)
                    status_text = st.empty()

                    status_text.text("Đang khởi tạo AI Model...")
                    progress_bar.progress(10)

                    # Run cleaning
                    try:
                        status_text.text("Đang xử lý dữ liệu với LLM...")
                        cleaned_df = analyst.run_cleaning_pipeline(target_cols, llm_processor)
                        progress_bar.progress(90)

                        # Save result
                        output_clean_path = os.path.join(config.output_folder, "result_cleaned.xlsx")
                        analyst.save_cleaned_data(cleaned_df, output_clean_path)
                        progress_bar.progress(100)

                        st.success("✅ Hoàn thành!")
                        st.markdown(f"**File kết quả:** `{output_clean_path}`")

                        # Show comparison
                        st.markdown("#### 🔍 So sánh kết quả")
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown("**Gốc**")
                            st.dataframe(analyst.df[target_cols].head())
                        with col2:
                            st.markdown("**Đã làm sạch**")
                            cleaned_cols = [f"{c}_cleaned" for c in target_cols]
                            st.dataframe(cleaned_df[cleaned_cols].head())

                    except Exception as e:
                        st.error(f"Lỗi: {e}")

# =================== TAB 8: CHI TIẾT DỰ ÁN ===================
elif selected == "⚙️ Chi tiết":
    st.markdown("<div class='tab-content'>", unsafe_allow_html=True)
    ModernUIComponents.render_header("Chi tiết Dự án", "Cấu hình và tùy chỉnh hệ thống", "⚙️")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("### 📁 Đường dẫn dự án")
    col1, col2 = st.columns([3, 1])

    with col1:
        output_folder = st.text_input(
            "📁 Thư mục Output",
            value=config.output_folder,
            help="Nơi lưu kết quả xử lý",
            label_visibility="collapsed"
        )
        if output_folder != config.output_folder:
            config.output_folder = output_folder

    with col2:
        if st.button("📂 Chọn folder", use_container_width=True):
            st.info("💡 Sử dụng đường dẫn tuyệt đối hoặc tương đối từ thư mục gốc")

    st.markdown("---")
    
    st.markdown("### 📁 Đường dẫn nguồn dữ liệu")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("**📄 Quốc Ngữ & Thông tin**")
        name_file_info = st.text_input("File thông tin (JSON)", value=getattr(config, 'name_file_info', 'before_handle_data.json'), label_visibility="collapsed")
        config.name_file_info = name_file_info
        vi_dir = st.text_input("Thư mục ảnh Quốc Ngữ", value=getattr(config, 'vi_dir', ''), label_visibility="collapsed")
        config.vi_dir = vi_dir
    with col2:
        st.markdown("**🏯 Hán Nôm**")
        ocr_json_nom = st.text_input("Thư mục JSON Hán Nôm", value=getattr(config, 'ocr_json_nom', ''), label_visibility="collapsed")
        config.ocr_json_nom = ocr_json_nom
        nom_dir = st.text_input("Thư mục ảnh Hán Nôm", value=getattr(config, 'nom_dir', ''), label_visibility="collapsed")
        config.nom_dir = nom_dir
    with col3:
        st.markdown("**📝 Văn bản**")
        ocr_txt_qn = st.text_input("Thư mục TXT Quốc Ngữ", value=getattr(config, 'ocr_txt_qn', ''), label_visibility="collapsed")
        config.ocr_txt_qn = ocr_txt_qn
        st.caption("Đường dẫn tuyệt đối hoặc tương đối từ thư mục dự án")

    st.markdown("---")

    st.markdown("### ✂️ Thiết lập cắt ảnh")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**📄 Quốc Ngữ**")
        num_crop_qn = st.number_input(
            "Số cắt ảnh",
            min_value=1,
            max_value=10,
            value=config.num_crop_qn,
            help="Số lần cắt ngang cho ảnh Quốc Ngữ",
            label_visibility="collapsed"
        )
        config.num_crop_qn = num_crop_qn

    with col2:
        st.markdown("**🏯 Hán Nôm**")
        num_crop_hn = st.number_input(
            "Số cắt ảnh",
            min_value=1,
            max_value=10,
            value=config.num_crop_hn,
            help="Số lần cắt ngang cho ảnh Hán Nôm",
            label_visibility="collapsed"
        )
        config.num_crop_hn = num_crop_hn

    st.markdown("---")

    st.markdown("### 👁️ Thiết lập OCR Hán Nôm")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**🎯 Loại OCR**")
        ocr_id_detail = st.selectbox(
            "Chọn loại",
            options=[1, 2, 3, 4],
            format_func=lambda x: {
                1: "Thông thường dọc",
                2: "Hành chính",
                3: "Ngoại cảnh",
                4: "Thông thường ngang"
            }[x],
            index=config.ocr_id - 1,
            key="ocr_id_detail",
            label_visibility="collapsed"
        )
        config.ocr_id = ocr_id_detail

    with col2:
        st.markdown("**📚 Loại ngôn ngữ**")
        lang_type_detail = st.selectbox(
            "Chọn ngôn ngữ",
            options=[0, 1, 2],
            format_func=lambda x: {
                0: "Chưa biết",
                1: "Hán",
                2: "Nôm"
            }[x],
            index=config.lang_type,
            key="lang_type_detail",
            label_visibility="collapsed"
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
    st.markdown("<div class='tab-content'>", unsafe_allow_html=True)
    ModernUIComponents.render_header("Quản lý Dữ liệu", "Theo dõi và quản lý quy trình xử lý", "📊")
    st.markdown("</div>", unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["📈 Thống kê", "📋 Kiểm tra", "🗑️ Xóa"])

    with tab1:
        st.markdown("#### 📊 Quy trình xử lý")
        
        pipeline_stages = [
            ("📥 Trích xuất", status['extracted']),
            ("✂️ Cắt ảnh", status['cropped']),
            ("🔤 OCR QN", status['ocr_vi']),
            ("🈳 OCR HN", status['ocr_nom']),
            ("🔗 Align", status['aligned']),
            ("✏️ Sửa lỗi", status['corrected']),
        ]
        
        ModernUIComponents.render_process_steps([
            {
                "number": i + 1,
                "title": stage.split(" ", 1)[1],
                "status": "completed" if completed else "pending",
                "icon": stage.split()[0],
                "description": "Hoàn thành ✅" if completed else "Chưa thực hiện ⏳"
            }
            for i, (stage, completed) in enumerate(pipeline_stages)
        ])

    with tab2:
        st.markdown("#### 📋 Kiểm tra số trang")
        
        if status['extracted']:
            if st.button("🔍 Kiểm tra số trang", use_container_width=True):
                try:
                    handler = DataHandler(config.output_folder, config.name_file_info)
                    pages = handler.check_num_pages()
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("📄 Trang Quốc Ngữ", pages['vi'], delta=None)
                    with col2:
                        st.metric("🏯 Trang Hán Nôm", pages['nom'], delta=None)
                    
                    st.markdown("---")
                    
                    if pages['vi'] != pages['nom']:
                        ModernUIComponents.render_info_box(f"⚠️ Số trang không bằng nhau! QN: {pages['vi']}, HN: {pages['nom']}", "warning")
                    else:
                        ModernUIComponents.render_info_box(f"✅ Số trang bằng nhau: {pages['vi']}", "info")
                
                except Exception as e:
                    st.error(f"❌ Lỗi: {str(e)}")
        else:
            ModernUIComponents.render_info_box("Vui lòng trích xuất PDF trước!", "info")

    with tab3:
        st.markdown("#### 🗑️ Xóa dữ liệu")
        
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

# Modern footer
ModernUIComponents.render_footer()

