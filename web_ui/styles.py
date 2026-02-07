def get_main_styles():
    """
    Returns the main CSS styles for the application.
    Inspired by Google Material Design.
    """
    return """
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500;700&family=Roboto:wght@300;400;500;700&display=swap');

    /* Root variables - Material Design colors */
    :root {
        --google-blue: #4285f4;
        --google-red: #ea4335;
        --google-yellow: #fbbc04;
        --google-green: #34a853;
        --primary: #1a73e8;
        --primary-hover: #1765cc;
        --surface: #ffffff;
        --background: #f8f9fa;
        --on-surface: #202124;
        --on-surface-variant: #5f6368;
        --border: #dadce0;
        --elevation-1: 0 1px 2px 0 rgba(60,64,67,0.3), 0 1px 3px 1px rgba(60,64,67,0.15);
        --elevation-2: 0 1px 2px 0 rgba(60,64,67,0.3), 0 2px 6px 2px rgba(60,64,67,0.15);
        --elevation-3: 0 4px 8px 3px rgba(60,64,67,0.15), 0 1px 3px 0 rgba(60,64,67,0.3);
    }

    /* Animations */
    @keyframes fadeIn {
        from {
            opacity: 0;
            transform: translateY(10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateX(-20px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }

    @keyframes shimmer {
        0% {
            background-position: -1000px 0;
        }
        100% {
            background-position: 1000px 0;
        }
    }

    @keyframes pulse {
        0%, 100% {
            opacity: 1;
        }
        50% {
            opacity: 0.5;
        }
    }

    /* Global styles */
    * {
        font-family: 'Roboto', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }

    h1, h2, h3, h4, h5, h6 {
        font-family: 'Google Sans', 'Roboto', sans-serif;
        font-weight: 500;
        color: var(--on-surface);
    }

    /* Beautiful minimal background */
    body {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        background-attachment: fixed;
    }

    .main {
        background: linear-gradient(135deg, #667eea15 0%, #764ba215 25%, #f09343 10 50%, #4285f410 100%);
        background-size: 400% 400%;
        animation: gradientShift 15s ease infinite;
        padding: 2rem 3rem;
        min-height: 100vh;
        position: relative;
    }

    .main::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background-image:
            radial-gradient(circle at 20% 30%, rgba(66, 133, 244, 0.08) 0%, transparent 50%),
            radial-gradient(circle at 80% 70%, rgba(234, 67, 53, 0.06) 0%, transparent 50%),
            radial-gradient(circle at 40% 80%, rgba(52, 168, 83, 0.06) 0%, transparent 50%);
        pointer-events: none;
        z-index: 0;
    }

    @keyframes gradientShift {
        0% {
            background-position: 0% 50%;
        }
        50% {
            background-position: 100% 50%;
        }
        100% {
            background-position: 0% 50%;
        }
    }

    /* Content animation */
    .main > div {
        animation: fadeIn 0.6s ease-out;
        position: relative;
        z-index: 1;
    }

    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Google-style header */
    .main-title {
        font-family: 'Google Sans', sans-serif;
        font-size: 2.75rem;
        font-weight: 400;
        color: var(--on-surface);
        text-align: center;
        margin: 0 0 0.5rem 0;
        letter-spacing: -0.5px;
    }

    .subtitle {
        font-family: 'Roboto', sans-serif;
        font-size: 1rem;
        font-weight: 400;
        color: var(--on-surface-variant);
        text-align: center;
        margin-bottom: 3rem;
    }

    /* Material Design Cards */
    .material-card {
        background: var(--surface);
        border-radius: 8px;
        padding: 24px;
        margin: 16px 0;
        box-shadow: var(--elevation-1);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        border: 1px solid var(--border);
        animation: fadeIn 0.5s ease-out;
        backdrop-filter: blur(10px);
        background-color: rgba(255, 255, 255, 0.95);
    }

    .material-card:hover {
        box-shadow: var(--elevation-3);
        transform: translateY(-2px);
    }

    /* Status indicators - Google style */
    .status-chip {
        display: inline-flex;
        align-items: center;
        padding: 6px 12px;
        border-radius: 16px;
        font-size: 0.875rem;
        font-weight: 500;
        margin: 4px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        animation: slideIn 0.4s ease-out;
    }

    .status-chip:hover {
        transform: scale(1.05);
    }

    .status-success {
        background-color: #e6f4ea;
        color: #137333;
    }

    .status-pending {
        background-color: #fef7e0;
        color: #b06000;
    }

    .status-error {
        background-color: #fce8e6;
        color: #c5221f;
    }

    /* Google Material Buttons */
    .stButton > button {
        font-family: 'Google Sans', 'Roboto', sans-serif;
        font-size: 14px;
        font-weight: 500;
        letter-spacing: 0.25px;
        text-transform: none;
        padding: 0 24px;
        height: 36px;
        border-radius: 4px;
        border: none;
        background-color: var(--primary);
        color: white;
        box-shadow: var(--elevation-1);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        cursor: pointer;
        position: relative;
        overflow: hidden;
    }

    .stButton > button::before {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        width: 0;
        height: 0;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.3);
        transform: translate(-50%, -50%);
        transition: width 0.6s, height 0.6s;
    }

    .stButton > button:hover::before {
        width: 300px;
        height: 300px;
    }

    .stButton > button:hover {
        background-color: var(--primary-hover);
        box-shadow: var(--elevation-3);
        transform: translateY(-1px);
    }

    .stButton > button:active {
        transform: translateY(0);
        box-shadow: var(--elevation-1);
    }

    .stButton > button:active {
        box-shadow: var(--elevation-1);
    }

    /* Text inputs - Material Design */
    .stTextInput input,
    .stNumberInput input,
    .stTextArea textarea {
        font-family: 'Roboto', sans-serif;
        font-size: 14px;
        padding: 12px 16px;
        border: 1px solid var(--border);
        border-radius: 4px;
        background-color: var(--surface);
        color: var(--on-surface);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        animation: fadeIn 0.5s ease-out;
    }

    .stTextInput input:hover,
    .stNumberInput input:hover,
    .stTextArea textarea:hover {
        border-color: var(--on-surface);
        transform: translateY(-1px);
        box-shadow: 0 2px 4px rgba(0,0,0,0.08);
    }

    .stTextInput input:focus,
    .stNumberInput input:focus,
    .stTextArea textarea:focus {
        border-color: var(--primary);
        border-width: 2px;
        outline: none;
        box-shadow: 0 0 0 3px rgba(26, 115, 232, 0.1);
        transform: translateY(-1px);
    }

    /* Select boxes */
    .stSelectbox select {
        font-family: 'Roboto', sans-serif;
        font-size: 14px;
        padding: 12px 16px;
        border: 1px solid var(--border);
        border-radius: 4px;
        background-color: var(--surface);
        color: var(--on-surface);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        animation: fadeIn 0.5s ease-out;
    }

    .stSelectbox select:hover {
        border-color: var(--on-surface);
        transform: translateY(-1px);
        box-shadow: 0 2px 4px rgba(0,0,0,0.08);
    }

    .stSelectbox select:focus {
        border-color: var(--primary);
        border-width: 2px;
        outline: none;
        box-shadow: 0 0 0 3px rgba(26, 115, 232, 0.1);
    }

    /* Checkboxes - Material style */
    .stCheckbox {
        font-family: 'Roboto', sans-serif;
        font-size: 14px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }

    /* File uploader */
    .stFileUploader {
        background-color: var(--surface);
        border: 2px dashed var(--border);
        border-radius: 8px;
        padding: 24px;
        text-align: center;
        transition: all 0.2s;
    }

    .stFileUploader:hover {
        border-color: var(--primary);
        background-color: #f8f9fa;
    }

    /* Progress bar - Material */
    .stProgress > div > div {
        background-color: #e8eaed;
        border-radius: 4px;
        height: 4px;
    }

    .stProgress > div > div > div {
        background-color: var(--primary);
        border-radius: 4px;
    }

    /* Tabs - Material Design */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0;
        border-bottom: 1px solid var(--border);
        background-color: transparent;
    }

    .stTabs [data-baseweb="tab"] {
        font-family: 'Google Sans', sans-serif;
        font-size: 14px;
        font-weight: 500;
        color: var(--on-surface-variant);
        background-color: transparent;
        border: none;
        padding: 12px 24px;
        height: auto;
        border-bottom: 2px solid transparent;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
    }

    .stTabs [data-baseweb="tab"]::after {
        content: '';
        position: absolute;
        bottom: 0;
        left: 50%;
        width: 0;
        height: 2px;
        background-color: var(--primary);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        transform: translateX(-50%);
    }

    .stTabs [data-baseweb="tab"]:hover {
        color: var(--on-surface);
        background-color: rgba(26, 115, 232, 0.04);
    }

    .stTabs [data-baseweb="tab"]:hover::after {
        width: 100%;
    }

    .stTabs [aria-selected="true"] {
        color: var(--primary);
        border-bottom-color: var(--primary);
        font-weight: 500;
    }

    .stTabs [aria-selected="true"]::after {
        width: 100%;
    }

    /* Sidebar - Material style */
    [data-testid="stSidebar"] {
        background: linear-gradient(135deg, rgba(255,255,255,0.95) 0%, rgba(248,249,250,0.95) 100%);
        backdrop-filter: blur(10px);
        border-right: 1px solid var(--border);
        box-shadow: var(--elevation-2);
        animation: slideIn 0.4s ease-out;
    }

    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        font-family: 'Google Sans', sans-serif;
        color: var(--on-surface);
        animation: fadeIn 0.6s ease-out;
    }

    /* Metric containers */
    .stMetric {
        background: linear-gradient(135deg, rgba(255,255,255,0.9) 0%, rgba(248,249,250,0.9) 100%);
        backdrop-filter: blur(10px);
        padding: 16px;
        border-radius: 8px;
        box-shadow: var(--elevation-1);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        animation: fadeIn 0.5s ease-out;
        border: 1px solid rgba(218, 220, 224, 0.5);
    }

    .stMetric:hover {
        box-shadow: var(--elevation-2);
        transform: translateY(-2px);
    }

    .stMetric label {
        font-family: 'Roboto', sans-serif;
        font-size: 12px;
        color: var(--on-surface-variant);
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .stMetric [data-testid="stMetricValue"] {
        font-family: 'Google Sans', sans-serif;
        font-size: 32px;
        font-weight: 400;
        color: var(--on-surface);
    }

    /* Alerts - Material Design */
    .stSuccess,
    .stInfo,
    .stWarning,
    .stError {
        font-family: 'Roboto', sans-serif;
        font-size: 14px;
        padding: 16px;
        border-radius: 8px;
        border-left: none;
        box-shadow: var(--elevation-1);
        animation: slideIn 0.4s ease-out;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }

    .stSuccess:hover,
    .stInfo:hover,
    .stWarning:hover,
    .stError:hover {
        box-shadow: var(--elevation-2);
        transform: translateX(4px);
    }

    .stSuccess {
        background-color: #e6f4ea;
        color: #137333;
    }

    .stInfo {
        background-color: #e8f0fe;
        color: #1967d2;
    }

    .stWarning {
        background-color: #fef7e0;
        color: #b06000;
    }

    .stError {
        background-color: #fce8e6;
        color: #c5221f;
    }

    /* Dividers - Material style */
    hr {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent 0%, var(--border) 50%, transparent 100%);
        margin: 24px 0;
        animation: fadeIn 0.5s ease-out;
    }

    /* Expander - Material Design */
    .streamlit-expanderHeader {
        font-family: 'Roboto', sans-serif;
        font-size: 14px;
        font-weight: 500;
        background-color: transparent;
        border: 1px solid var(--border);
        border-radius: 4px;
        padding: 12px 16px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }

    .streamlit-expanderHeader:hover {
        background-color: rgba(26, 115, 232, 0.04);
        box-shadow: var(--elevation-1);
        transform: translateX(2px);
    }

    /* Column titles */
    .column-title {
        font-family: 'Google Sans', sans-serif;
        font-size: 14px;
        font-weight: 500;
        color: var(--on-surface);
        margin-bottom: 8px;
        letter-spacing: 0.1px;
    }

    /* Google-style section headers */
    .section-header {
        font-family: 'Google Sans', sans-serif;
        font-size: 20px;
        font-weight: 400;
        color: var(--on-surface);
        margin: 24px 0 16px 0;
        letter-spacing: 0;
        animation: slideIn 0.5s ease-out;
        position: relative;
        padding-left: 12px;
    }

    .section-header::before {
        content: '';
        position: absolute;
        left: 0;
        top: 50%;
        transform: translateY(-50%);
        width: 4px;
        height: 24px;
        background: linear-gradient(135deg, var(--google-blue) 0%, var(--primary) 100%);
        border-radius: 2px;
        animation: fadeIn 0.6s ease-out;
    }

    /* Floating Action Button style */
    .fab {
        background: linear-gradient(135deg, var(--primary) 0%, var(--google-blue) 100%);
        color: white;
        border-radius: 50%;
        width: 56px;
        height: 56px;
        box-shadow: var(--elevation-3);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        animation: fadeIn 0.8s ease-out;
    }

    .fab:hover {
        box-shadow: 0 8px 10px 1px rgba(60,64,67,0.15), 0 3px 14px 2px rgba(60,64,67,0.12);
        transform: translateY(-4px) rotate(90deg);
    }

    /* Status items for sidebar */
    .status-item {
        background: linear-gradient(135deg, rgba(255,255,255,0.9) 0%, rgba(248,249,250,0.9) 100%);
        backdrop-filter: blur(10px);
        border-radius: 8px;
        padding: 12px;
        margin: 8px 0;
        border: 1px solid var(--border);
        font-family: 'Roboto', sans-serif;
        font-size: 13px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        animation: slideIn 0.4s ease-out;
    }

    .status-item:hover {
        box-shadow: var(--elevation-2);
        border-color: var(--primary);
        transform: translateX(4px);
    }

    /* Google-style data table */
    .dataframe {
        font-family: 'Roboto', sans-serif;
        font-size: 13px;
        border: 1px solid var(--border);
        border-radius: 8px;
        overflow: hidden;
        animation: fadeIn 0.6s ease-out;
        box-shadow: var(--elevation-1);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }

    .dataframe:hover {
        box-shadow: var(--elevation-2);
    }

    .dataframe th {
        background: linear-gradient(135deg, #f8f9fa 0%, #e8eaed 100%);
        color: var(--on-surface);
        font-weight: 500;
        padding: 12px 16px;
        text-align: left;
        transition: background-color 0.3s ease;
    }

    .dataframe tr {
        transition: all 0.2s ease;
    }

    .dataframe tr:hover {
        background-color: rgba(26, 115, 232, 0.04);
    }

    .dataframe td {
        padding: 12px 16px;
        border-top: 1px solid var(--border);
    }

    /* Scrollbar styling - Material */
    ::-webkit-scrollbar {
        width: 12px;
        height: 12px;
    }

    ::-webkit-scrollbar-track {
        background: #f1f3f4;
    }

    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #dadce0 0%, #bdc1c6 100%);
        border-radius: 6px;
        border: 2px solid #f1f3f4;
        transition: all 0.3s ease;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #bdc1c6 0%, #9aa0a6 100%);
    }

    /* Remove default Streamlit padding */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
        animation: fadeIn 0.6s ease-out;
    }

    /* Progress bar animation */
    .stProgress > div > div {
        background: linear-gradient(90deg, var(--primary) 0%, var(--google-blue) 50%, var(--primary) 100%);
        background-size: 200% 100%;
        animation: shimmer 2s linear infinite;
        transition: all 0.3s ease;
    }

    /* Loading spinner */
    .stSpinner > div {
        border-color: var(--primary) transparent transparent transparent;
        animation: spin 1s linear infinite;
    }

    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }

    /* Tab content transitions */
    .tab-content {
        animation: tabFadeIn 0.4s ease-out;
        transform-origin: top;
    }

    @keyframes tabFadeIn {
        from {
            opacity: 0;
            transform: translateY(20px) scale(0.98);
        }
        to {
            opacity: 1;
            transform: translateY(0) scale(1);
        }
    }

    /* Stagger animation for cards */
    .stMarkdown > div:nth-child(1) {
        animation-delay: 0.05s;
    }

    .stMarkdown > div:nth-child(2) {
        animation-delay: 0.1s;
    }

    .stMarkdown > div:nth-child(3) {
        animation-delay: 0.15s;
    }

    /* Column animations */
    .stColumn {
        animation: slideUpFade 0.5s ease-out;
    }

    @keyframes slideUpFade {
        from {
            opacity: 0;
            transform: translateY(15px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    /* Menu transition enhancement */
    [data-testid="stHorizontalBlock"] {
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }

    /* Smooth content swap */
    [data-testid="stVerticalBlock"] > div {
        animation: contentFadeIn 0.35s ease-out;
    }

    @keyframes contentFadeIn {
        from {
            opacity: 0;
            transform: translateX(-10px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }

    /* Status grid styling */
    .status-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 0.5rem;
        margin: 1rem 0;
    }
    .status-item {
        padding: 0.8rem;
        border-radius: 8px;
        text-align: center;
        font-size: 0.9rem;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    .status-item-done {
        background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%);
        color: white;
    }
    .status-item-pending {
        background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
        color: white;
    }
    </style>
    """
