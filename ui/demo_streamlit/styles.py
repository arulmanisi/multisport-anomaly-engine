"""
Custom CSS styles for the PLAIX Intelligence Platform UI.
"""

CUSTOM_CSS = """
<style>
    /* Global Imports */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');

    /* Root Variables */
    :root {
        --bg-color: #0E1117;
        --card-bg: #1A1C24;
        --accent-color: #4CAF50; /* Green accent */
        --accent-gradient: linear-gradient(90deg, #4CAF50 0%, #00C853 100%);
        --text-primary: #E0E0E0;
        --text-secondary: #B0B0B0;
        --border-color: rgba(255, 255, 255, 0.1);
    }

    /* General Typography */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        color: var(--text-primary);
        background-color: var(--bg-color);
    }

    h1, h2, h3 {
        font-weight: 700 !important;
        letter-spacing: -0.02em !important;
    }

    h1 {
        background: -webkit-linear-gradient(eee, #4CAF50);
        -webkit-background-clip: text;
        margin-bottom: 0.5rem !important;
    }

    /* Hide Streamlit Stuff */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Cards / Containers */
    div[data-testid="stExpander"] {
        border: 1px solid var(--border-color);
        border-radius: 8px;
        background-color: var(--card-bg);
    }

    div[data-testid="stMetricValue"] {
        font-size: 1.8rem !important;
        font-weight: 600 !important;
        color: var(--text-primary) !important;
    }
    
    div[data-testid="stMetricLabel"] {
        font-size: 0.9rem !important;
        color: var(--text-secondary) !important;
    }

    /* Modern Buttons */
    div.stButton > button {
        background: var(--accent-gradient);
        color: white;
        border: none;
        border-radius: 6px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        transition: all 0.2s ease;
        width: 100%;
    }

    div.stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(76, 175, 80, 0.3);
    }

    div.stButton > button:active {
        transform: translateY(0);
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #12141A;
        border-right: 1px solid var(--border-color);
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
        background-color: transparent;
    }

    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: transparent;
        border-radius: 4px;
        color: var(--text-secondary);
        font-weight: 600;
    }

    .stTabs [aria-selected="true"] {
        background-color: rgba(76, 175, 80, 0.1) !important;
        color: var(--accent-color) !important;
        border-bottom: 2px solid var(--accent-color);
    }

    /* Key Value Tables (Dataframes) */
    div[data-testid="stDataFrame"] {
        border: 1px solid var(--border-color);
        border-radius: 8px;
        overflow: hidden;
    }
    
    /* Dividers */
    hr {
        margin: 1.5em 0 !important;
        border-color: var(--border-color) !important;
    }

</style>
"""
