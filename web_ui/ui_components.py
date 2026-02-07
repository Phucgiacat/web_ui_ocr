"""
Modern UI Components for OCR Corrector
Streamlit helper functions for creating modern, responsive UI elements
"""

import streamlit as st
from typing import Optional, List, Dict, Callable
from modern_theme import THEME_CONFIG, CSS_COMPONENTS, create_modern_card, create_info_box

class ModernUIComponents:
    """Collection of modern UI components for Streamlit"""
    
    @staticmethod
    def render_header(title: str, subtitle: str, emoji: str = "📄"):
        """Render modern header with gradient"""
        st.markdown(f"""
        <div style='
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem;
            border-radius: 15px;
            margin-bottom: 2rem;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            text-align: center;
        '>
            <h1 style='margin: 0 0 0.5rem 0; font-size: 2.5rem; letter-spacing: 1px;'>
                {emoji} {title}
            </h1>
            <p style='margin: 0; font-size: 1rem; opacity: 0.95;'>{subtitle}</p>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_modern_card(title: str, emoji: str, content: str, color: str = "#667eea"):
        """Render a modern card with title and content"""
        st.markdown(create_modern_card(title, emoji, content, color), unsafe_allow_html=True)
    
    @staticmethod
    def render_status_grid(status_items: List[tuple]):
        """
        Render status items in a grid
        status_items: List of (title, is_completed, emoji) tuples
        """
        col_count = min(3, len(status_items))
        cols = st.columns(col_count)
        
        for idx, (title, is_completed, emoji) in enumerate(status_items):
            col = cols[idx % col_count]
            with col:
                status_class = "status-done" if is_completed else "status-pending"
                status_icon = "✅" if is_completed else "⏳"
                gradient = "linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%)" if is_completed else "linear-gradient(135deg, #fa709a 0%, #fee140 100%)"
                
                st.markdown(f"""
                <div style='
                    background: {gradient};
                    color: white;
                    padding: 1.5rem;
                    border-radius: 10px;
                    text-align: center;
                    font-weight: bold;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                    transition: all 0.3s ease;
                '>
                    <div style='font-size: 2rem; margin-bottom: 0.5rem;'>{emoji}</div>
                    <div>{title}</div>
                    <div style='font-size: 1.2rem; margin-top: 0.5rem;'>{status_icon}</div>
                </div>
                """, unsafe_allow_html=True)
    
    @staticmethod
    def render_process_steps(steps: List[Dict]):
        """
        Render process steps with status
        steps: List of {"number": int, "title": str, "status": "pending/active/completed", "icon": str}
        """
        st.markdown("""
        <style>
        .step-container {
            display: flex;
            align-items: center;
            margin: 1rem 0;
            position: relative;
        }
        .step-number {
            width: 50px;
            height: 50px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            color: white;
            font-size: 1.2rem;
            margin-right: 1rem;
            flex-shrink: 0;
        }
        .step-completed {
            background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%);
        }
        .step-active {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            animation: pulse 1.5s infinite;
        }
        .step-pending {
            background: #ddd;
        }
        @keyframes pulse {
            0% { box-shadow: 0 0 0 0 rgba(102, 126, 234, 0.7); }
            70% { box-shadow: 0 0 0 10px rgba(102, 126, 234, 0); }
            100% { box-shadow: 0 0 0 0 rgba(102, 126, 234, 0); }
        }
        .step-info {
            flex: 1;
        }
        .step-title {
            font-weight: bold;
            font-size: 1.1rem;
            margin: 0;
        }
        .step-description {
            color: #666;
            font-size: 0.9rem;
            margin: 0.25rem 0 0 0;
        }
        </style>
        """, unsafe_allow_html=True)
        
        for step in steps:
            status_class = f"step-{step['status']}"
            st.markdown(f"""
            <div class='step-container'>
                <div class='step-number {status_class}'>{step.get('icon', step['number'])}</div>
                <div class='step-info'>
                    <p class='step-title'>{step['title']}</p>
                    <p class='step-description'>{step.get('description', '')}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    @staticmethod
    def render_info_box(message: str, info_type: str = "info"):
        """Render modern info/warning/error boxes"""
        st.markdown(create_info_box(message, info_type), unsafe_allow_html=True)
    
    @staticmethod
    def render_progress_with_steps(current: int, total: int, message: str = ""):
        """Render progress bar with steps"""
        percentage = (current / total * 100) if total > 0 else 0
        
        st.markdown(f"""
        <div style='margin: 1.5rem 0;'>
            <div style='display: flex; justify-content: space-between; margin-bottom: 0.5rem;'>
                <span style='font-weight: bold;'>{message}</span>
                <span style='color: #667eea; font-weight: bold;'>{current}/{total}</span>
            </div>
            <div style='
                width: 100%;
                height: 8px;
                background: #e9ecef;
                border-radius: 10px;
                overflow: hidden;
            '>
                <div style='
                    width: {percentage}%;
                    height: 100%;
                    background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
                    transition: width 0.3s ease;
                    border-radius: 10px;
                '></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_feature_grid(features: List[Dict]):
        """
        Render feature grid
        features: List of {"icon": str, "title": str, "description": str, "color": str}
        """
        cols = st.columns(min(3, len(features)))
        
        for idx, feature in enumerate(features):
            with cols[idx % len(cols)]:
                st.markdown(f"""
                <div style='
                    background: white;
                    border-radius: 12px;
                    padding: 1.5rem;
                    text-align: center;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
                    border-top: 4px solid {feature.get("color", "#667eea")};
                    transition: all 0.3s ease;
                '>
                    <div style='font-size: 2.5rem; margin-bottom: 0.5rem;'>{feature['icon']}</div>
                    <h4 style='margin: 0.5rem 0; color: {feature.get("color", "#667eea")};'>{feature['title']}</h4>
                    <p style='color: #666; margin: 0; font-size: 0.9rem;'>{feature['description']}</p>
                </div>
                """, unsafe_allow_html=True)
    
    @staticmethod
    def render_file_info(filename: str, filesize: int, filetype: str, upload_time: str = ""):
        """Render file information display"""
        filesize_mb = filesize / (1024 * 1024)
        
        st.markdown(f"""
        <div style='
            background: white;
            border-radius: 10px;
            padding: 1rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
            border-left: 4px solid #667eea;
        '>
            <div style='display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;'>
                <div>
                    <p style='color: #999; font-size: 0.9rem; margin: 0;'>📄 File</p>
                    <p style='color: #333; font-weight: bold; margin: 0.25rem 0 0 0;'>{filename}</p>
                </div>
                <div>
                    <p style='color: #999; font-size: 0.9rem; margin: 0;'>💾 Kích thước</p>
                    <p style='color: #333; font-weight: bold; margin: 0.25rem 0 0 0;'>{filesize_mb:.2f} MB</p>
                </div>
                <div>
                    <p style='color: #999; font-size: 0.9rem; margin: 0;'>📝 Loại</p>
                    <p style='color: #333; font-weight: bold; margin: 0.25rem 0 0 0;'>{filetype}</p>
                </div>
                <div>
                    <p style='color: #999; font-size: 0.9rem; margin: 0;'>⏰ Thời gian</p>
                    <p style='color: #333; font-weight: bold; margin: 0.25rem 0 0 0;'>{upload_time or "N/A"}</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_footer():
        """Render modern footer"""
        st.markdown("---")
        st.markdown("""
        <div style='
            text-align: center;
            padding: 2rem;
            color: #999;
            border-top: 1px solid #e0e0e0;
            margin-top: 2rem;
        '>
            <p style='margin: 0.25rem 0;'>
                <strong>OCR Corrector Tool</strong> | Phiên bản 2.0
            </p>
            <p style='margin: 0.25rem 0; font-size: 0.9rem;'>
                Công cụ xử lý OCR chuyên nghiệp cho Quốc Ngữ & Hán Nôm
            </p>
            <p style='margin: 1rem 0 0 0; font-size: 0.85rem; color: #bbb;'>
                © 2026 | <a href='#' style='color: #667eea; text-decoration: none;'>Documentation</a> | 
                <a href='#' style='color: #667eea; text-decoration: none;'>Support</a>
            </p>
        </div>
        """, unsafe_allow_html=True)
