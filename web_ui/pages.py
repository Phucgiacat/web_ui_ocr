"""
OCR Corrector Web UI - Pages Module
Chứa các trang riêng biệt cho giao diện
"""

import streamlit as st
from typing import Callable, Optional

class PageManager:
    """Quản lý các trang trong ứng dụng"""
    
    @staticmethod
    def render_status_indicator(title: str, completed: bool, icon: str = ""):
        """Hiển thị chỉ số trạng thái"""
        status = "✅ Hoàn thành" if completed else "⏳ Chưa hoàn thành"
        color = "#d4edda" if completed else "#fff3cd"
        
        st.markdown(f"""
        <div style="padding: 10px; border-radius: 5px; background-color: {color}; border-left: 5px solid {'#28a745' if completed else '#ffc107'};">
            <strong>{icon} {title}</strong><br/>
            {status}
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_progress_section(title: str, button_text: str, on_click: Callable, 
                               params: Optional[dict] = None, disabled: bool = False):
        """Hiển thị section xử lý"""
        st.markdown(f"### {title}")
        
        # Render parameters nếu có
        if params:
            cols = st.columns(len(params))
            for idx, (key, (param_type, default, kwargs)) in enumerate(params.items()):
                with cols[idx]:
                    if param_type == 'slider':
                        st.slider(key, key=f"param_{key}", **kwargs)
                    elif param_type == 'checkbox':
                        st.checkbox(key, value=default, key=f"param_{key}")
                    elif param_type == 'number':
                        st.number_input(key, value=default, key=f"param_{key}", **kwargs)
        
        if st.button(button_text, disabled=disabled, use_container_width=True):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            def progress_callback(message: str, current: int, total: int):
                if total > 0:
                    progress_bar.progress(current / total)
                status_text.write(f"📝 {message}")
            
            return {
                'progress_bar': progress_bar,
                'status_text': status_text,
                'progress_callback': progress_callback
            }
        
        return None
