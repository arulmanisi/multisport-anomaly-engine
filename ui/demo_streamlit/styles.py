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

    /* Reduce default Streamlit padding */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
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
    
    /* Navigation Menu Styling (Radio Buttons) */
    div[role="radiogroup"] {
        gap: 8px;
    }
    
    div[role="radiogroup"] label {
        background-color: rgba(255, 255, 255, 0.03);
        padding: 12px 16px;
        border-radius: 8px;
        border: 1px solid transparent;
        transition: all 0.2s;
        width: 100%;
    }
    
    div[role="radiogroup"] label:hover {
        background-color: rgba(255, 255, 255, 0.08);
        border-color: rgba(255, 255, 255, 0.1);
    }
    
    /* Selected Item */
    div[role="radiogroup"] label[data-baseweb="radio"] > div:first-child {
        /* Hide the actual radio circle if possible, or style it */
    }

    /* Highlight selected text */
    div[role="radiogroup"] label[aria-checked="true"] {
        background: linear-gradient(90deg, rgba(76, 175, 80, 0.2) 0%, transparent 100%);
        border-left: 4px solid var(--accent-color);
        color: var(--accent-color);
    }
    
    section[data-testid="stSidebar"] div[data-testid="stExpander"] {
        background-color: transparent; /* Cleaner nested look */
        border: none;
    }

    button[kind="primary"] {
        background: var(--accent-gradient) !important;
        font-weight: 700;
        border: none;
        transition: transform 0.1s;
    }
    
    button[kind="primary"]:hover {
        transform: scale(1.02);
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

    /* Featured Anomaly Card */
    .featured-card {
        background: linear-gradient(135deg, rgba(76, 175, 80, 0.1), rgba(33, 150, 243, 0.05));
        border: 1px solid rgba(76, 175, 80, 0.3);
        border-radius: 12px;
        padding: 24px;
        margin-top: 1rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
    }
    
    .driver-tag {
        display: inline-block;
        background: rgba(255, 255, 255, 0.05);
        color: var(--text-secondary);
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 0.85rem;
        margin-right: 8px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Sports Ticker */
    .ticker-wrap {
        width: 100%;
        background-color: rgba(255, 193, 7, 0.1);
        border-bottom: 1px solid rgba(255, 193, 7, 0.3);
        padding: 8px 0;
        margin-bottom: 16px;
        overflow: hidden;
        white-space: nowrap;
    }
    
    .ticker-item {
        display: inline-block;
        padding: 0 2rem;
        color: #FFC107; /* Amber for breaking news */
        font-weight: 600;
        font-size: 0.9rem;
    }
    
    /* Dashboard Stat Card */
    .stat-card {
        background-color: var(--card-bg);
        border: 1px solid var(--border-color);
        border-radius: 8px;
        padding: 16px;
        text-align: center;
        transition: transform 0.2s;
    }
    
    .stat-card:hover {
        transform: translateY(-2px);
        border-color: var(--accent-color);
    }
    
    .stat-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: var(--text-primary);
        margin: 4px 0;
    }
    
    .stat-label {
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: var(--text-secondary);
    }

</style>
"""
