# Modern UI Theme Configuration
# This file contains theme settings for the OCR Corrector Web UI

THEME_CONFIG = {
    "colors": {
        "primary": "#667eea",
        "secondary": "#764ba2",
        "success": "#28a745",
        "warning": "#ffc107",
        "danger": "#dc3545",
        "info": "#17a2b8",
        "light": "#f8f9fa",
        "dark": "#212529",
        "gradient_primary": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
        "gradient_success": "linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%)",
        "gradient_warning": "linear-gradient(135deg, #fa709a 0%, #fee140 100%)",
    },
    "spacing": {
        "xs": "0.5rem",
        "sm": "1rem",
        "md": "1.5rem",
        "lg": "2rem",
        "xl": "2.5rem",
    },
    "border_radius": {
        "small": "8px",
        "medium": "12px",
        "large": "15px",
        "full": "50%",
    },
    "shadows": {
        "light": "0 2px 4px rgba(0,0,0,0.05)",
        "medium": "0 2px 8px rgba(0,0,0,0.1)",
        "large": "0 4px 12px rgba(0,0,0,0.15)",
        "hover": "0 4px 15px rgba(102, 126, 234, 0.4)",
    },
    "transitions": {
        "fast": "0.2s ease",
        "normal": "0.3s ease",
        "smooth": "0.5s ease-in-out",
    },
}

# CSS Components Library
CSS_COMPONENTS = {
    "card": """
    <div style='
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        margin: 1rem 0;
        border-top: 4px solid #667eea;
        transition: all 0.3s ease;
    '>
        {content}
    </div>
    """,
    
    "button_success": """
    <button style='
        background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%);
        color: white;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 8px;
        font-weight: bold;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 2px 8px rgba(132, 250, 176, 0.3);
    ' onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 4px 12px rgba(132, 250, 176, 0.4)'"
      onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 2px 8px rgba(132, 250, 176, 0.3)'">
        {text}
    </button>
    """,
    
    "badge_success": """
    <span style='
        background: #d4edda;
        color: #155724;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: bold;
        border: 1px solid #c3e6cb;
    '>
        {text}
    </span>
    """,
    
    "badge_warning": """
    <span style='
        background: #fff3cd;
        color: #856404;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: bold;
        border: 1px solid #ffeaa7;
    '>
        {text}
    </span>
    """,
    
    "progress_bar": """
    <div style='
        width: 100%;
        height: 8px;
        background: #e9ecef;
        border-radius: 10px;
        overflow: hidden;
        margin: 1rem 0;
    '>
        <div style='
            width: {percentage}%;
            height: 100%;
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            transition: width 0.3s ease;
            border-radius: 10px;
        '></div>
    </div>
    """,
}

# Status Display Helper
def get_status_badge(status: bool, label: str) -> str:
    """Generate status badge HTML"""
    if status:
        return f'<span style="background: #d4edda; color: #155724; padding: 0.25rem 0.75rem; border-radius: 20px; font-size: 0.85rem; font-weight: bold;">✅ {label}</span>'
    else:
        return f'<span style="background: #fff3cd; color: #856404; padding: 0.25rem 0.75rem; border-radius: 20px; font-size: 0.85rem; font-weight: bold;">⏳ {label}</span>'

# Layout Helper
def create_modern_card(title: str, emoji: str, content: str, color: str = "#667eea") -> str:
    """Create a modern card component"""
    return f"""
    <div style='
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        margin: 1rem 0;
        border-top: 4px solid {color};
        transition: all 0.3s ease;
    '>
        <h3 style='color: {color}; margin-bottom: 1rem; display: flex; align-items: center; gap: 0.5rem;'>
            <span style='font-size: 1.5rem;'>{emoji}</span>
            {title}
        </h3>
        <p style='color: #666; line-height: 1.6;'>{content}</p>
    </div>
    """

# Modern Info Box
def create_info_box(message: str, info_type: str = "info") -> str:
    """Create modern info/warning/error boxes"""
    colors = {
        "success": {"bg": "#d4edda", "border": "#28a745", "icon": "✅"},
        "warning": {"bg": "#fff3cd", "border": "#ffc107", "icon": "⚠️"},
        "error": {"bg": "#f8d7da", "border": "#dc3545", "icon": "❌"},
        "info": {"bg": "#d1ecf1", "border": "#17a2b8", "icon": "ℹ️"},
    }
    color = colors.get(info_type, colors["info"])
    
    return f"""
    <div style='
        background: {color["bg"]};
        border-left: 5px solid {color["border"]};
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    '>
        <p style='margin: 0; font-weight: bold;'>{color["icon"]} {message}</p>
    </div>
    """
