def get_main_styles():
    """
    Returns the main CSS styles for the application.
    Modern Glassmorphism & Soft UI Theme.
    """
    return """
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

    /* Root variables - Modern Palette */
    :root {
        --primary: #6366f1;
        --primary-hover: #4f46e5;
        --secondary: #ec4899;
        --success: #10b981;
        --warning: #f59e0b;
        --error: #ef4444;
        --info: #3b82f6;

        --background: #f8fafc;
        --surface: rgba(255, 255, 255, 0.7);
        --surface-hover: rgba(255, 255, 255, 0.9);

        --text-primary: #1e293b;
        --text-secondary: #64748b;

        --border: rgba(226, 232, 240, 0.8);

        /* Modern Shadows */
        --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
        --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        --shadow-color: rgba(99, 102, 241, 0.2);

        --radius-sm: 8px;
        --radius-md: 12px;
        --radius-lg: 16px;
        --radius-xl: 24px;
    }

    /* Animations */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }

    @keyframes slideIn {
        from { opacity: 0; transform: translateX(-20px); }
        to { opacity: 1; transform: translateX(0); }
    }

    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.05); }
    }

    @keyframes gradient-xy {
        0%, 100% {
            background-size: 400% 400%;
            background-position: left center;
        }
        50% {
            background-size: 200% 200%;
            background-position: right center;
        }
    }

    /* Global styles */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
    }

    body {
        background-color: var(--background);
        background-image:
            radial-gradient(at 0% 0%, rgba(99, 102, 241, 0.15) 0px, transparent 50%),
            radial-gradient(at 100% 0%, rgba(236, 72, 153, 0.15) 0px, transparent 50%),
            radial-gradient(at 100% 100%, rgba(16, 185, 129, 0.15) 0px, transparent 50%),
            radial-gradient(at 0% 100%, rgba(59, 130, 246, 0.15) 0px, transparent 50%);
        background-attachment: fixed;
    }

    h1, h2, h3, h4, h5, h6 {
        font-weight: 700;
        color: var(--text-primary);
        letter-spacing: -0.025em;
    }

    /* Modern Headers */
    .main-title {
        font-size: 3.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.5rem;
        padding-bottom: 0.5rem;
    }

    .subtitle {
        font-size: 1.1rem;
        color: var(--text-secondary);
        text-align: center;
        margin-bottom: 3rem;
        font-weight: 400;
    }

    /* Glassmorphism Cards */
    .material-card {
        background: var(--surface);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.5);
        border-radius: var(--radius-lg);
        padding: 24px;
        box-shadow: var(--shadow-sm);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        margin: 16px 0;
    }

    .material-card:hover {
        transform: translateY(-4px);
        box-shadow: var(--shadow-lg);
        background: var(--surface-hover);
        border-color: var(--primary);
    }

    /* Modern Buttons */
    .stButton > button {
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-hover) 100%);
        color: white;
        border: none;
        padding: 0.5rem 1.5rem;
        border-radius: var(--radius-md);
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px -1px var(--shadow-color);
        height: auto;
        min-height: 44px;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px var(--shadow-color);
        background: linear-gradient(135deg, var(--primary-hover) 0%, var(--primary) 100%);
    }

    .stButton > button:active {
        transform: translateY(0);
    }

    /* Inputs & Selects */
    .stTextInput input, .stNumberInput input, .stSelectbox select, .stTextArea textarea {
        background: rgba(255, 255, 255, 0.8);
        border: 1px solid var(--border);
        border-radius: var(--radius-md);
        padding: 0.75rem 1rem;
        transition: all 0.2s ease;
        color: var(--text-primary);
    }

    .stTextInput input:focus, .stNumberInput input:focus, .stSelectbox select:focus, .stTextArea textarea:focus {
        border-color: var(--primary);
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.2);
        background: white;
    }

    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background: rgba(255, 255, 255, 0.8);
        backdrop-filter: blur(20px);
        border-right: 1px solid var(--border);
    }

    /* Status Grid */
    .status-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 0.75rem;
        margin: 1.5rem 0;
    }

    .status-item {
        padding: 1rem;
        border-radius: var(--radius-md);
        text-align: center;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        border: 1px solid transparent;
        background: white;
        box-shadow: var(--shadow-sm);
    }

    .status-item:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-md);
    }

    .status-item-done {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(16, 185, 129, 0.2) 100%);
        border-color: rgba(16, 185, 129, 0.3);
        color: #065f46;
    }

    .status-item-pending {
        background: linear-gradient(135deg, rgba(245, 158, 11, 0.1) 0%, rgba(245, 158, 11, 0.2) 100%);
        border-color: rgba(245, 158, 11, 0.3);
        color: #92400e;
    }

    /* Metric Cards */
    .stMetric {
        background: white;
        padding: 1.5rem;
        border-radius: var(--radius-lg);
        box-shadow: var(--shadow-sm);
        border: 1px solid var(--border);
    }

    .stMetric [data-testid="stMetricValue"] {
        font-weight: 700;
        color: var(--primary);
    }

    /* Progress Bar */
    .stProgress > div > div {
        background: linear-gradient(90deg, var(--primary) 0%, var(--secondary) 100%);
        border-radius: 10px;
        height: 8px;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(255, 255, 255, 0.5);
        padding: 0.5rem;
        border-radius: var(--radius-lg);
        border: 1px solid var(--border);
        gap: 0.5rem;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: var(--radius-md);
        padding: 0.5rem 1rem;
        color: var(--text-secondary);
        font-weight: 500;
        border: none;
    }

    .stTabs [aria-selected="true"] {
        background: white;
        color: var(--primary);
        box-shadow: var(--shadow-sm);
        font-weight: 600;
    }

    /* File Uploader */
    .stFileUploader {
        border: 2px dashed var(--border);
        border-radius: var(--radius-lg);
        padding: 2rem;
        background: rgba(255, 255, 255, 0.5);
        transition: all 0.3s ease;
    }

    .stFileUploader:hover {
        border-color: var(--primary);
        background: rgba(99, 102, 241, 0.05);
    }

    /* DataFrame Styling */
    .dataframe {
        border-radius: var(--radius-lg);
        overflow: hidden;
        border: 1px solid var(--border);
        box-shadow: var(--shadow-sm);
    }

    .dataframe th {
        background: #f1f5f9;
        color: var(--text-primary);
        font-weight: 600;
        padding: 1rem;
    }

    .dataframe td {
        padding: 0.75rem 1rem;
        border-bottom: 1px solid var(--border);
    }

    /* Custom Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }

    ::-webkit-scrollbar-track {
        background: transparent;
    }

    ::-webkit-scrollbar-thumb {
        background: #cbd5e1;
        border-radius: 4px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: #94a3b8;
    }

    /* Header Enhancements */
    .section-header {
        position: relative;
        padding-left: 1.5rem;
        margin: 2rem 0 1.5rem 0;
        font-size: 1.5rem;
    }

    .section-header::before {
        content: '';
        position: absolute;
        left: 0;
        top: 50%;
        transform: translateY(-50%);
        width: 6px;
        height: 32px;
        background: linear-gradient(to bottom, var(--primary), var(--secondary));
        border-radius: 4px;
    }

    /* Alerts/Callouts */
    .stSuccess, .stInfo, .stWarning, .stError {
        border-radius: var(--radius-md);
        border: none;
        padding: 1rem;
        box-shadow: var(--shadow-sm);
    }

    .stSuccess { background: #ecfdf5; color: #065f46; border-left: 4px solid var(--success); }
    .stInfo { background: #eff6ff; color: #1e40af; border-left: 4px solid var(--info); }
    .stWarning { background: #fffbeb; color: #92400e; border-left: 4px solid var(--warning); }
    .stError { background: #fef2f2; color: #991b1b; border-left: 4px solid var(--error); }

    </style>
    """
