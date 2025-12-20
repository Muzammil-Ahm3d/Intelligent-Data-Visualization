# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
from src.loader import load_data
from src.analysis import get_column_types, identify_key_metrics
from src.visualizer import generate_dashboard_charts, format_number
from src.copilot import ask_copilot 
from dotenv import load_dotenv

load_dotenv()
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import streamlit.components.v1 as components

# Page Config
st.set_page_config(page_title="IDV Analytics Platform", page_icon="zb", layout="wide")

# --- NAVIGATION HANDLER ---
# Check for query params to handle navigation from HTML cards
if "nav" in st.query_params:
    nav_page = st.query_params["nav"]
    valid_pages = ["Auto Exploration", "Data Copilot", "Manual Exploration"]
    if nav_page in valid_pages:
        st.session_state.page = nav_page
        # Clear the query param to prevent sticky navigation on rerun
        st.query_params.clear()

# --- SESSION STATE INITIALIZATION ---
if 'page' not in st.session_state:
    st.session_state.page = "Home"
if 'df' not in st.session_state:
    st.session_state.df = None
if 'col_types' not in st.session_state:
    st.session_state.col_types = None
if 'focused_chart_index' not in st.session_state:
    st.session_state.focused_chart_index = None
if 'dashboard_generated' not in st.session_state:
    st.session_state.dashboard_generated = False
if 'uploaded_file_name' not in st.session_state:
    st.session_state.uploaded_file_name = None
# --- MANUAL EXPLORATION STATE ---
if 'me_x' not in st.session_state:
    st.session_state.me_x = "None"
if 'me_y' not in st.session_state:
    st.session_state.me_y = "None"
if 'me_color' not in st.session_state:
    st.session_state.me_color = "None"
if 'me_type' not in st.session_state:
    st.session_state.me_type = "Scatter"
if 'copilot_history' not in st.session_state:
    st.session_state.copilot_history = [{"role": "assistant", "content": "Hello! I'm your Data Copilot. Ask me anything about your data."}]

# --- CUSTOM CSS ---
st.markdown("""
<style>
    /* Main Background */
    .stApp {
        background: linear-gradient(to bottom right, #e0f2fe, #eef2ff, #f3e8ff);
        background-attachment: fixed;
    }
    
    /* Navigation Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #0b1120;
    }
    section[data-testid="stSidebar"] .stMarkdown h3 {
        color: #94a3b8 !important;
        text-transform: uppercase;
        font-size: 0.75rem;
        letter-spacing: 0.05em;
        margin-top: 1rem;
    }
    section[data-testid="stSidebar"] label {
        color: #cbd5e1 !important;
    }
    
    /* Nav Buttons */
    div[role="radiogroup"] label p {
        color: #3b82f6 !important; /* Bright Blue for Page Names */
        font-size: 1.1rem;
        font-weight: 700;
    }
    
    /* Sidebar Captions (Row count) */
    section[data-testid="stSidebar"] div[data-testid="stCaptionContainer"] {
        color: #cbd5e1 !important; /* Light text for caption */
    }
    
    /* General Sidebar Text */
    section[data-testid="stSidebar"] p {
        color: #e2e8f0;
    }

    /* HIDE STREAMLIT ELEMENTS */
    [data-testid="stToolbar"] {
        display: none;
    }
    [data-testid="stDecoration"] {
        display: none;
    }
    footer {
        display: none;
    }
    
    /* Hide native sidebar toggle visually but keep in DOM for JS triggering */
    [data-testid="collapsedControl"] {
        opacity: 0; /* Invisible */
        pointer-events: auto; /* Clickable */
    }
    
    /* Make header transparent and pass-through */
    [data-testid="stHeader"] {
        background: transparent;
        pointer-events: none; 
        z-index: 100; /* Keep roughly where it is */
    }
    
    /* Upload Box Styling - Target the Streamlit Uploader */
    div[data-testid='stFileUploader'] {
        background-color: white;
        border: 2px dashed #cbd5e1;
        border-radius: 16px;
        padding: 2rem;
        text-align: center;
        transition: border-color 0.3s;
    }
    div[data-testid='stFileUploader']:hover {
        border-color: #6366f1;
    }
    div[data-testid='stFileUploader'] section {
        padding: 0;
    }
    
    /* Smart Builder Card (Dashboard Page) */
    .smart-builder-card {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #d946ef 100%);
        border-radius: 16px;
        padding: 3rem;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 10px 25px rgba(99, 102, 241, 0.2);
    }
    
    /* Chart Cards */
    .stPlotlyChart {
        background-color: white;
        border-radius: 12px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        padding: 10px;
        border: 1px solid #f1f5f9;
        transition: transform 0.2s, box-shadow 0.2s;
    }

    /* Metrics */
    div[data-testid="stMetric"] {
        background-color: white;
        padding: 15px;
        border-radius: 12px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        text-align: center;
        border: 1px solid #e2e8f0;
    }
    
    /* Global Primary Button Style (Blue) */
    /* Global Primary Button Style (Blue) */
    div.stButton > button[kind="primary"] {
        background-color: #3b82f6 !important;
        border-color: #3b82f6 !important;
        color: white !important;
        font-weight: 600;
        border-radius: 8px;
        padding: 0.5rem 1rem;
    }
    div.stButton > button[kind="primary"]:hover {
        background-color: #2563eb !important;
        border-color: #2563eb !important;
    }
    
    /* Feature Cards CSS (Restored) */
    .feature-card {
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        transition: transform 0.2s, box-shadow 0.2s;
        height: 100%;
        cursor: pointer;
    }
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        border-color: #cbd5e1;
    }
    .feature-icon-box {
        width: 48px;
        height: 48px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 1.5rem;
        margin-bottom: 1rem;
    }
    .icon-purple { background: linear-gradient(135deg, #a855f7 0%, #d946ef 100%); }
    .icon-blue { background: linear-gradient(135deg, #0ea5e9 0%, #3b82f6 100%); }
    .icon-green { background: linear-gradient(135deg, #22c55e 0%, #10b981 100%); }
    
    .card-title {
        font-size: 1.25rem;
        font-weight: 700;
        color: #0f172a;
        margin-bottom: 0.5rem;
    }
    .card-desc {
        color: #64748b;
        font-size: 0.95rem;
        line-height: 1.5;
    }
    
    /* Link styling for cards */
    a.card-link {
        text-decoration: none !important;
        color: inherit !important;
        display: block;
        height: 100%;
    }
    a.card-link:hover {
        text-decoration: none !important;
    }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR NAV & FILTERS ---
from streamlit_option_menu import option_menu

# --- SIDEBAR NAV & FILTERS ---
with st.sidebar:
    # Navigation Logic - Sync with Session State
    pages = ["Home", "Data Source", "Auto Exploration", "Data Copilot", "Manual Exploration", "Dashboard"]
    
    # Determine default index
    try:
        current_index = pages.index(st.session_state.page)
    except ValueError:
        current_index = 0
        
    st.markdown('<p style="color: #94a3b8; font-size: 0.75rem; letter-spacing: 0.05em; text-transform: uppercase; margin-bottom: 0.5rem; padding-left: 10px;">Analytics Tools</p>', unsafe_allow_html=True)

    selection = option_menu(
        menu_title=None,
        options=pages,
        icons=['house', 'database', 'rocket-takeoff', 'robot', 'grip-vertical', 'microsoft'],
        default_index=current_index,
        styles={
            "container": {"padding": "0!important", "background-color": "#0b1120", "border": "none", "border-radius": "0", "box-shadow": "none"},
            "icon": {"color": "#3b82f6", "font-size": "1.1rem"}, 
            "nav-link": {
                "font-size": "1rem", 
                "text-align": "left", 
                "margin": "0px", 
                "--hover-color": "#1e293b",
                "color": "#cbd5e1",
                "background-color": "#0b1120"
            },
            "nav-link-selected": {
                "background-color": "transparent", 
                "color": "#3b82f6", 
                "font-weight": "700",
                "border": "none"
            },
        }
    )
    
    # Update state if changed
    if selection != st.session_state.page:
        st.session_state.page = selection
        st.rerun()

    st.markdown("---")
    
    # --- FILTERS (Restored) ---
    # Apply filters globally to the DF if we are on Dashboard view
    df_display = None
    if st.session_state.df is not None:
        df_display = st.session_state.df.copy() # Start with full data
        col_types = st.session_state.col_types
        
        if st.session_state.page == "Dashboard":
            st.markdown("### FILTERS")
            
            # 1. Date Filter
            if col_types['date']:
                date_col = col_types['date'][0]
                df_display[date_col] = pd.to_datetime(df_display[date_col], errors='coerce')
                min_date = df_display[date_col].min()
                max_date = df_display[date_col].max()
                
                if pd.notnull(min_date) and pd.notnull(max_date):
                    start_date, end_date = st.date_input(
                        f"Date Range", 
                        [min_date, max_date],
                        min_value=min_date, max_value=max_date,
                        key="date_filter"
                    )
                    if start_date and end_date:
                        df_display = df_display[(df_display[date_col].dt.date >= start_date) & 
                                                (df_display[date_col].dt.date <= end_date)]

            # 2. Categorical Filters
            filter_cols = [c for c in col_types['categorical'] if df_display[c].nunique() < 50]
            filter_cols.sort(key=lambda x: df_display[x].nunique())
            
            for f_col in filter_cols[:3]: 
                options = sorted(df_display[f_col].astype(str).unique())
                selected = st.multiselect(f"{f_col}", options, key=f"filter_{f_col}")
                if selected:
                    df_display = df_display[df_display[f_col].astype(str).isin(selected)]
            
            st.markdown("---")
            st.caption(f"Showing {len(df_display)} rows")


import streamlit.components.v1 as components

# --- PAGE ROUTING ---

# Global CSS for Layout & Hiding Streamlit Elements
st.markdown("""
    <style>
        /* Reduce Top Padding for Main Content & Add Left Margin for Mini-Sidebar */
        .block-container {
            padding-top: 0rem;
            padding-bottom: 0rem;
            padding-left: 5rem; /* Make space for mini-sidebar */
        }
        
        /* Adjust Sidebar Padding to align with Main Header */
        [data-testid="stSidebarUserContent"] {
            padding-top: 0rem !important; 
        }
        
        /* General Sidebar Text */
        section[data-testid="stSidebar"] p {
            color: #e2e8f0;
        }
    
        /* HIDE STREAMLIT ELEMENTS */
        [data-testid="stToolbar"] {
            display: none;
        }
        [data-testid="stDecoration"] {
            display: none;
        }
        footer {
            display: none;
        }
        
        /* Hide native sidebar toggle visually but keep in DOM for JS triggering */
        [data-testid="collapsedControl"] {
            opacity: 0; /* Invisible */
            pointer-events: auto; /* Clickable */
        }
        
        /* Make header transparent and pass-through */
        [data-testid="stHeader"] {
            background: transparent;
            pointer-events: none; 
            z-index: 100; /* Keep roughly where it is */
        }
        
        /* Upload Box Styling */
        div[data-testid='stFileUploader'] {
            background-color: white;
            border: 2px dashed #cbd5e1;
            border-radius: 16px;
            padding: 2rem;
            text-align: center;
            transition: border-color 0.3s;
        }
        div[data-testid='stFileUploader']:hover {
            border-color: #6366f1;
        }
        div[data-testid='stFileUploader'] section {
            padding: 0;
        }
        
        .smart-builder-card {
            background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #d946ef 100%);
            border-radius: 16px;
            padding: 3rem;
            color: white;
            margin-bottom: 2rem;
            box-shadow: 0 10px 25px rgba(99, 102, 241, 0.2);
        }
        .stPlotlyChart {
            background-color: white;
            border-radius: 12px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            padding: 10px;
            border: 1px solid #f1f5f9;
        }
        div[data-testid="stMetric"] {
            background-color: white;
            padding: 15px;
            border-radius: 12px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            text-align: center;
            border: 1px solid #e2e8f0;
        }
    </style>
""", unsafe_allow_html=True)

# Custom Header Component (Iframe for reliable JS)
header_html = """
    <head>
        <!-- Load Bootstrap Icons to match standard Streamlit option_menu styling -->
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/font/bootstrap-icons.css">
    </head>
    <style>
        body { margin: 0; padding: 0; background: transparent; font-family: sans-serif; }
        .custom-header { display: flex; align-items: center; padding: 0.5rem 0; }
        .header-icon { cursor: pointer; margin-right: 15px; color: #1e293b; transition: 0.2s; display: flex; }
        .header-icon:hover { transform: scale(1.1); color: #3b82f6; }
        .brand-text { font-size: 1.25rem; font-weight: 600; color: #64748b; letter-spacing: 0.05em; }
        .brand-highlight { color: #6366f1; font-weight: 800; font-size: 1.5rem; margin-right: 0.5rem; }
    </style>
    
    <script>
        function toggleSidebar() {
            try {
                const doc = window.parent.document;
                const selectors = ['[data-testid="collapsedControl"]', '[data-testid="stSidebar"] button', 'button[kind="header"]'];
                for (let s of selectors) {
                    const els = doc.querySelectorAll(s);
                    for (let el of els) {
                        if (el.offsetParent !== null || selectors.indexOf(s) === 0) { el.click(); return; }
                    }
                }
            } catch(e) { console.error(e); }
        }
        
        function injectMiniSidebar() {
            const doc = window.parent.document; // Parent document
            if (doc.getElementById('mini-sidebar')) return;
            
            // Create container
            const sidebar = doc.createElement('div');
            sidebar.id = 'mini-sidebar';
            sidebar.style.cssText = `
                position: fixed; top: 0; left: 0; bottom: 0; width: 60px;
                background-color: #0b1120; z-index: 99; display: flex;
                flex-direction: column; align-items: center; padding-top: 60px;
                box-shadow: 2px 0 5px rgba(0,0,0,0.2);
                transition: transform 0.3s;
            `;
            
            // Since we are injecting into PARENT, we need the styles there too!
            // BUT: We can't easily inject CSS link into parent head from here without CORS potentially, 
            // OR we can just inject a <style> block with @import or create a <link> element in parent head.
            if (!doc.getElementById('bi-css')) {
                const link = doc.createElement('link');
                link.id = 'bi-css';
                link.rel = 'stylesheet';
                link.href = 'https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/font/bootstrap-icons.css';
                doc.head.appendChild(link);
            }
            
            // Icon Classes
            const icons = [
                'bi-house',
                'bi-database',
                'bi-rocket-takeoff',
                'bi-robot',
                'bi-grip-vertical',
                'bi-microsoft'
            ];
            
            icons.forEach((iconClass, index) => {
                const btn = doc.createElement('div');
                // Use <i> tag for font icon
                btn.innerHTML = `<i class="bi ${iconClass}"></i>`;
                
                // Styling: Match the main sidebar "icon" style ({color: #3b82f6, font-size: 1.1rem}) from app.py
                btn.style.cssText = `
                    padding: 15px 0; 
                    cursor: pointer; 
                    display: flex; 
                    justify-content: center; 
                    width: 100%;
                    color: #3b82f6;
                    font-size: 1.25rem; /* ~20px */
                `;
                btn.className = 'mini-sidebar-icon'; 
                
                // Hover
                btn.addEventListener('mouseenter', () => { btn.style.backgroundColor = '#1e293b'; });
                btn.addEventListener('mouseleave', () => { btn.style.backgroundColor = 'transparent'; });
                
                btn.onclick = () => {
                    // Click logic
                    const iframes = doc.querySelectorAll('.stSidebar iframe');
                    let clicked = false;
                    for (let frame of iframes) {
                        try {
                            const frameDoc = frame.contentDocument || frame.contentWindow.document;
                            const items = frameDoc.querySelectorAll('.nav-link');
                            if (items && items[index]) {
                                items[index].click();
                                clicked = true;
                                break;
                            }
                        } catch (e) { console.log(e); }
                    }
                    if (!clicked) console.warn("Nav item not found");
                };
                sidebar.appendChild(btn);
            });
            
            doc.body.appendChild(sidebar);
        }
        
        // Init
        setTimeout(injectMiniSidebar, 1000); 
    </script>
    
    <div class="custom-header">
        <div onclick="toggleSidebar()" class="header-icon">
             <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
                <line x1="9" y1="3" x2="9" y2="21"></line>
            </svg>
        </div>
        <span class="brand-highlight">IDV</span>
        <span class="brand-text">ANALYTICS PLATFORM</span>
    </div>
"""

components.html(header_html, height=60, scrolling=False)

if st.session_state.page == "Home":
    # Home Page UI
    st.markdown("""
        <style>
            .hero-container {
                text-align: center;
                padding: 4rem 0;
                background: linear-gradient(180deg, rgba(99,102,241,0.05) 0%, rgba(255,255,255,0) 100%);
                border-radius: 20px;
                margin-bottom: 2rem;
            }
            .hero-title {
                font-size: 3.5rem;
                font-weight: 800;
                margin-bottom: 1rem;
                color: #0f172a;
            }
            .hero-subtitle {
                font-size: 1.25rem;
                color: #64748b;
                max-width: 600px;
                margin: 0 auto 2rem auto;
                line-height: 1.6;
            }
            .cta-button {
                display: inline-block;
                background-color: #3b82f6;
                color: white;
                font-weight: 600;
                padding: 0.8rem 2rem;
                border-radius: 8px;
                text-decoration: none;
                transition: background-color 0.2s;
            }
            .cta-button:hover {
                background-color: #2563eb;
            }
            
            .feature-card {
                background: white;
                border-radius: 16px;
                padding: 2rem;
                border: 1px solid #f1f5f9;
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
                height: 100%;
                transition: transform 0.2s, box-shadow 0.2s;
            }
            .feature-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
                border-color: #cbd5e1;
            }
            .feature-icon-box {
                width: 50px;
                height: 50px;
                border-radius: 12px;
                display: flex;
                align-items: center;
                justify-content: center;
                margin-bottom: 1.5rem;
                font-size: 1.5rem;
                color: white;
            }
            .icon-purple { background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%); }
            .icon-blue { background: linear-gradient(135deg, #3b82f6 0%, #06b6d4 100%); }
            .icon-green { background: linear-gradient(135deg, #10b981 0%, #3b82f6 100%); }
            
            .card-title {
                font-size: 1.25rem;
                font-weight: 700;
                color: #0f172a;
                margin-bottom: 0.5rem;
            }
            .card-desc {
                color: #64748b;
                font-size: 0.95rem;
                line-height: 1.5;
            }
            
            .key-feature-banner {
                background: linear-gradient(90deg, #4f46e5 0%, #7c3aed 100%);
                border-radius: 16px;
                padding: 3rem;
                color: white;
                margin-top: 3rem;
            }
        </style>
        
        <div class="hero-container">
            <div class="hero-title">Welcome to <span style="color: #6366f1;">IDV</span></div>
            <div class="hero-subtitle">
                AI-powered data analytics and visualization platform. Explore, analyze, and discover insights automatically.
            </div>
            <!-- Hacky inline click to switch session state? No, standard button below -->
        </div>
    """, unsafe_allow_html=True)
    
    # CTA Button using Streamlit
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("Get Started →", type="primary", use_container_width=True):
            st.session_state.page = "Data Source"
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # Feature Cards as Clickable Buttons
    # We use newlines to separate Title and Description visually, combined with CSS 'white-space: pre-wrap'
    
    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.markdown("""
            <a href="?nav=Auto Exploration" target="_self" class="card-link">
                <div class="feature-card">
                    <div class="feature-icon-box icon-purple">\U00002728</div>
                    <div class="card-title">Auto Exploration</div>
                    <div class="card-desc">Let AI automatically discover patterns and insights in your data with one click.</div>
                </div>
            </a>
        """, unsafe_allow_html=True)
        
    with c2:
        st.markdown("""
            <a href="?nav=Data Copilot" target="_self" class="card-link">
                <div class="feature-card">
                    <div class="feature-icon-box icon-blue">\U0001F916</div>
                    <div class="card-title">Data Copilot</div>
                    <div class="card-desc">Get AI-powered chart recommendations based on your selected variables.</div>
                </div>
            </a>
        """, unsafe_allow_html=True)
        
    with c3:
        st.markdown("""
            <a href="?nav=Manual Exploration" target="_self" class="card-link">
                <div class="feature-card">
                    <div class="feature-icon-box icon-green">\U0001F3A8</div>
                    <div class="card-title">Manual Exploration</div>
                    <div class="card-desc">Drag and drop variables to create custom visualizations exactly how you want.</div>
                </div>
            </a>
        """, unsafe_allow_html=True)
        
    # Key Features Banner
    st.markdown("""
        <div class="key-feature-banner">
            <h2 style="font-weight: 700; font-size: 2rem; margin-bottom: 1.5rem; color: white;">Key Features</h2>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                <div style="display: flex; align-items: center; gap: 10px;">
                    <div style="background: rgba(255,255,255,0.2); padding: 5px; border-radius: 50%;">●</div>
                    <span>Automated Insights & Outlier Detection</span>
                </div>
                <div style="display: flex; align-items: center; gap: 10px;">
                    <div style="background: rgba(255,255,255,0.2); padding: 5px; border-radius: 50%;">●</div>
                    <span>Smart Chart Recommendations</span>
                </div>
                <div style="display: flex; align-items: center; gap: 10px;">
                    <div style="background: rgba(255,255,255,0.2); padding: 5px; border-radius: 50%;">●</div>
                    <span>Interactive Dashboards</span>
                </div>
                <div style="display: flex; align-items: center; gap: 10px;">
                    <div style="background: rgba(255,255,255,0.2); padding: 5px; border-radius: 50%;">●</div>
                    <span>Interactive Chatbot</span>
                </div>
            </div>
        </div>
        
        <!-- Footer Space -->
        <div style="height: 100px;"></div>
    """, unsafe_allow_html=True)


if st.session_state.page == "Data Source":
    st.title("Data Source")
    st.markdown("<p style='color: #64748b; margin-top: -10px;'>Connect your data to start exploring insights</p>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 1. SHOW CURRENTLY LOADED DATA (If Exists)
    if st.session_state.df is not None:
        st.markdown(f"""
        <div style="background-color: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 1.5rem; margin-bottom: 2rem; display: flex; align-items: center; justify-content: space-between; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);">
            <div style="display: flex; align-items: center; gap: 1rem;">
                <div style="background-color: #dcfce7; color: #166534; padding: 10px; border-radius: 50%;">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M20 6L9 17L4 12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                </div>
                <div>
                    <h4 style="margin: 0; color: #0f172a; font-weight: 600;">Data Ready: {st.session_state.get('uploaded_file_name', 'Dataset')}</h4>
                    <p style="margin: 0; color: #64748b; font-size: 0.9rem;">{len(st.session_state.df)} rows loaded successfully</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
             if st.button("Proceed to Dashboard →", type="primary", use_container_width=True):
                    st.session_state.page = "Dashboard"
                    st.rerun()
        
        st.markdown("<div style='text-align: center; color: #94a3b8; margin: 2rem 0;'>— OR UPLOAD NEW FILE —</div>", unsafe_allow_html=True)
    
    # 2. UPLOAD AREA
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
            <div style="text-align: center; margin-bottom: 20px;">
                <div style="background:#eff6ff; width:60px; height:60px; border-radius:50%; display:inline-flex; align-items:center; justify-content:center; margin-bottom:10px;">
                    <svg width="30" height="30" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" stroke="#3b82f6" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                </div>
                <h3 style="margin:0; color:#1e293b; font-size:1.2rem;">Upload Your Data</h3>
            </div>
        """, unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader("Upload CSV or Excel", type=["csv", "xlsx"], key="main_uploader", label_visibility="collapsed")
        
        st.markdown("""
            <div style="text-align: center; margin-top: 10px; color: #94a3b8; font-size: 0.9rem;">
                Supported formats: CSV, Excel (Max 200MB)
            </div>
        """, unsafe_allow_html=True)

    if uploaded_file:
        try:
            # Handle File Loading
            # If a file is uploaded, it ALWAYS takes precedence and overwrites
            if st.session_state.uploaded_file_name != uploaded_file.name:
                df = load_data(uploaded_file)
                if df is not None:
                    st.session_state.df = df
                    st.session_state.col_types = get_column_types(df)
                    st.session_state.uploaded_file_name = uploaded_file.name
                    st.session_state.dashboard_generated = False 
                    
                    st.toast(f"File loaded! {len(df)} rows.", icon="✅")
                    # Force rerun to show the "Data Ready" state we just built
                    st.rerun()
            
        except Exception as e:
            st.error(f"Error loading file: {str(e)}")


elif st.session_state.page == "Auto Exploration":
    # --- AUTO EXPLORATION LOGIC (Integrated) ---
    df_ae = st.session_state.df
    
    # --- PAGE SPECIFIC CSS (Green Button) ---
    st.markdown("""
    <style>
        /* Force Primary Button to Blue on this page (Global now handles it, but just in case of conflict) */
        div.stButton > button[kind="primary"] {
            background-color: #3b82f6 !important;
            border-color: #3b82f6 !important;
            color: white !important;
        }
        div.stButton > button[kind="primary"]:hover {
            background-color: #2563eb !important;
            border-color: #2563eb !important;
        }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="margin-top: -1rem; margin-bottom: 2rem;">
        <h1 style="color: #0f172a; font-size: 2rem; font-weight: 800;">Auto Exploration</h1>
        <p style="color: #64748b; font-size: 1rem;">Let AI automatically discover insights in your data</p>
    </div>
    """, unsafe_allow_html=True)

    if df_ae is None:
        st.warning("Please upload data in the 'Data Source' page first.")
        if st.button("Go to Data Source", key="ae_go_back"):
            st.session_state.page = "Data Source"
            st.rerun()
    
    else:
        # --- STATE MANAGEMENT ---
        if 'auto_analysis_run' not in st.session_state:
            st.session_state.auto_analysis_run = False
        
        if 'ae_focused_chart' not in st.session_state:
            st.session_state.ae_focused_chart = None

        # --- FOCUS MODE VIEW ---
        if st.session_state.ae_focused_chart is not None:
            chart_type = st.session_state.ae_focused_chart
            
            if st.button("← Back to Insights"):
                st.session_state.ae_focused_chart = None
                st.rerun()
                
            st.subheader(f"🔍 Focused View: {chart_type}")
            
            num_df = df_ae.select_dtypes(include=[np.number])
            date_cols = df_ae.select_dtypes(include=['datetime', 'datetimetz']).columns
            if len(date_cols) == 0:
                for col in df_ae.select_dtypes(include='object').columns:
                    try:
                        df_ae[col] = pd.to_datetime(df_ae[col])
                        date_cols = df_ae.select_dtypes(include=['datetime', 'datetimetz']).columns
                    except: pass

            if chart_type == "Correlation Matrix":
                if not num_df.empty and len(num_df.columns) > 1:
                    fig = px.imshow(num_df.corr(), text_auto=True, color_continuous_scale='RdBu_r', aspect="auto")
                    fig.update_layout(height=800)
                    st.plotly_chart(fig, use_container_width=True)
                    
            elif chart_type == "Distribution Analysis":
                 if not num_df.empty:
                    target_col = num_df.std().idxmax()
                    fig = px.box(df_ae, y=target_col, points="outliers", title=f"Distribution of {target_col}")
                    fig.update_layout(height=800)
                    st.plotly_chart(fig, use_container_width=True)
                    
            elif chart_type == "Trend Analysis":
                if len(date_cols) > 0 and not num_df.empty:
                    date_col = date_cols[0]
                    val_col = num_df.columns[0]
                    df_trend = df_ae.sort_values(by=date_col)
                    fig = px.line(df_trend, x=date_col, y=val_col, title=f"{val_col} over {date_col}")
                    fig.update_layout(height=800)
                    st.plotly_chart(fig, use_container_width=True)
        
        else:
            # --- NORMAL VIEW (Hero + Grid) ---
            
            # HERO CARD
            st.markdown("""
            <style>
            .auto-hero-card {
                background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #d946ef 100%);
                border-radius: 16px;
                padding: 3rem;
                color: white;
                margin-bottom: 2rem;
                box-shadow: 0 10px 25px rgba(99, 102, 241, 0.2);
            }
            .insight-badge {
                background-color: #eff6ff; 
                color: #1e40af; 
                padding: 4px 12px; 
                border-radius: 12px; 
                font-size: 0.8rem; 
                font-weight: 600;
                border: 1px solid #bfdbfe;
                display: inline-block;
                margin-bottom: 4px;
            }
            </style>
            <div class="auto-hero-card">
                <div style="background: rgba(255,255,255,0.2); width: 60px; height: 60px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-bottom: 1.5rem;">
                     <svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2">
                        <path d="M12 2V6M12 18V22M4.93 4.93L7.76 7.76M16.24 16.24L19.07 19.07M2 12H6M18 12H22M4.93 19.07L7.76 16.24M16.24 7.76L19.07 4.93" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                </div>
                <h2 style="font-weight: 800; font-size: 1.8rem; margin-bottom: 0.5rem;">AI Advanced Analysis</h2>
                <p style="font-size: 1.1rem; opacity: 0.9;">Run deep correlation checks, outlier detection, and pattern recognition.</p>
            </div>
            """, unsafe_allow_html=True)
            
            col_btn, _ = st.columns([1, 4])
            with col_btn:
                if st.button("⚡ Run Advanced Scan", type="primary"):
                    st.session_state.auto_analysis_run = True
                    st.rerun()

            st.markdown("<br>", unsafe_allow_html=True)

            # --- ANALYSIS LOGIC & UI ---
            if st.session_state.auto_analysis_run:
                
                # 1. PREPARE DATA
                num_df = df_ae.select_dtypes(include=[np.number])
                date_cols = df_ae.select_dtypes(include=['datetime', 'datetimetz']).columns
                if len(date_cols) == 0:
                    for col in df_ae.select_dtypes(include='object').columns:
                        try:
                            df_ae[col] = pd.to_datetime(df_ae[col])
                            date_cols = df_ae.select_dtypes(include=['datetime', 'datetimetz']).columns
                        except:
                            pass

                # --- QUICK SUMMARY GENERATION ---
                summary_points = []
                
                # A. Dimensions
                summary_points.append(f"The dataset consists of **{len(df_ae)} rows** and **{len(df_ae.columns)} columns**.")
                
                # B. Time Context
                if len(date_cols) > 0:
                    d_col = date_cols[0]
                    start_date = df_ae[d_col].min().strftime('%Y-%m-%d')
                    end_date = df_ae[d_col].max().strftime('%Y-%m-%d')
                    summary_points.append(f"It covers a time range from **{start_date}** to **{end_date}**.")
                    
                # C. Outliers
                outlier_cols = []
                if not num_df.empty:
                    for col in num_df.columns[:5]: # Check top 5
                        Q1 = num_df[col].quantile(0.25)
                        Q3 = num_df[col].quantile(0.75)
                        IQR = Q3 - Q1
                        outliers = num_df[(num_df[col] < (Q1 - 1.5 * IQR)) | (num_df[col] > (Q3 + 1.5 * IQR))]
                        if len(outliers) > 0:
                            outlier_cols.append(col)
                
                if outlier_cols:
                    summary_points.append(f"Potential outliers were detected in **{', '.join(outlier_cols[:3])}**.")
                    
                # D. Correlation
                if not num_df.empty and len(num_df.columns) > 1:
                    corr_matrix = num_df.corr().abs()
                    upper = corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(bool))
                    max_corr = upper.max().max()
                    if max_corr > 0.7:
                         # Find pair
                         stack = upper.stack()
                         top_pair = stack.idxmax()
                         summary_points.append(f"A strong relationship exists between **{top_pair[0]}** and **{top_pair[1]}**.")

                # RENDER SUMMARY
                st.markdown(f"""
                <div style="background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 1.5rem; margin-bottom: 2rem; border-left: 5px solid #6366f1;">
                    <h3 style="margin-top: 0; color: #1e293b; font-size: 1.2rem; display: flex; align-items: center; gap: 8px;">
                        ⚡ Executive Summary
                    </h3>
                    <p style="color: #475569; line-height: 1.6; margin-bottom: 0;">
                        {' '.join(summary_points)}
                    </p>
                </div>
                """, unsafe_allow_html=True)

                # 2. LAYOUT
                c1, c2 = st.columns([1, 1])

                # --- LEFT COL: INSIGHTS ---
                with c1:
                    with st.container(border=True):
                        st.subheader("🔍 Key Insights")
                        
                        # A. OUTLIERS (IQR)
                        st.markdown("##### Outlier Detection")
                        if not num_df.empty:
                            for col in num_df.columns[:3]: 
                                Q1 = num_df[col].quantile(0.25)
                                Q3 = num_df[col].quantile(0.75)
                                IQR = Q3 - Q1
                                lower_bound = Q1 - 1.5 * IQR
                                upper_bound = Q3 + 1.5 * IQR
                                outliers = num_df[(num_df[col] < lower_bound) | (num_df[col] > upper_bound)]
                                
                                if len(outliers) > 0:
                                    st.markdown(f"""
                                    <div style="margin-bottom: 10px; padding-left: 10px; border-left: 3px solid #ef4444;">
                                        <strong>{col}</strong>: Found <span style="color:#ef4444;">{len(outliers)} outliers</span> 
                                        (Range: {num_df[col].min():.1f} - {num_df[col].max():.1f})
                                    </div>
                                    """, unsafe_allow_html=True)
                        else:
                            st.info("No numeric data for outlier analysis.")

                        st.divider()

                        # B. CORRELATIONS
                        st.markdown("##### Strong Correlations")
                        if not num_df.empty and len(num_df.columns) > 1:
                            corr_matrix = num_df.corr().abs()
                            upper = corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(bool))
                            strong_pairs = [(column, index, upper.loc[index, column]) 
                                            for index, row in upper.iterrows() 
                                            for column, val in row.items() if val > 0.7] 
                            
                            if strong_pairs:
                                for (col1, col2, score) in strong_pairs[:5]:
                                    st.markdown(f"""
                                    <div style="margin-bottom: 8px;">
                                        <span class="insight-badge">Correlation {score:.2f}</span>
                                        <span style="color: #334155;">{col1}</span> & <span style="color: #334155;">{col2}</span>
                                    </div>
                                    """, unsafe_allow_html=True)
                            else:
                                st.info("No strong linear correlations found (>0.7).")
                        else:
                             st.info("Not enough numeric interactions.")
                        
                        st.divider()
                        
                        # C. TRENDS
                        st.markdown("##### Temporal Patterns")
                        if len(date_cols) > 0:
                            date_col = date_cols[0]
                            st.success(f"Detected time series data: **{date_col}**")
                            time_span = df_ae[date_col].max() - df_ae[date_col].min()
                            st.write(f"Data spans **{time_span.days} days**.")
                        else:
                            st.warning("No date column detected for trend analysis.")

                # --- RIGHT COL: VISUALIZATIONS ---
                with c2:
                    with st.container(border=True):
                        st.subheader("📈 Smart Charts")
                        
                        # A. HEATMAP
                        if not num_df.empty and len(num_df.columns) > 1:
                            c_head, c_btn = st.columns([4, 1])
                            c_head.caption("Correlation Matrix")
                            if c_btn.button("⤢", key="btn_exp_corr", help="Expand Correlation Matrix"):
                                st.session_state.ae_focused_chart = "Correlation Matrix"
                                st.rerun()
                                
                            fig_corr = px.imshow(num_df.corr(), text_auto=True, color_continuous_scale='RdBu_r', aspect="auto")
                            fig_corr.update_layout(height=300, margin=dict(l=0, r=0, t=0, b=0))
                            st.plotly_chart(fig_corr, use_container_width=True)

                        # B. DISTRIBUTION
                        st.divider()
                        if not num_df.empty:
                            target_col = num_df.std().idxmax()
                            c_head, c_btn = st.columns([4, 1])
                            c_head.caption(f"Distribution of {target_col}")
                            if c_btn.button("⤢", key="btn_exp_dist", help="Expand Distribution Plot"):
                                 st.session_state.ae_focused_chart = "Distribution Analysis"
                                 st.rerun()
                                 
                            fig_dist = px.box(df_ae, y=target_col, points="outliers")
                            fig_dist.update_layout(height=300, margin=dict(l=0, r=0, t=0, b=0))
                            st.plotly_chart(fig_dist, use_container_width=True)
                        
                        # C. TREND
                        if len(date_cols) > 0 and not num_df.empty:
                            st.divider()
                            date_col = date_cols[0]
                            val_col = num_df.columns[0]
                            
                            c_head, c_btn = st.columns([4, 1])
                            c_head.caption(f"Trend of {val_col}")
                            if c_btn.button("⤢", key="btn_exp_trend", help="Expand Trend Graph"):
                                st.session_state.ae_focused_chart = "Trend Analysis"
                                st.rerun()

                            df_trend = df_ae.sort_values(by=date_col)
                            fig_trend = px.line(df_trend, x=date_col, y=val_col)
                            fig_trend.update_layout(height=250, margin=dict(l=0, r=0, t=0, b=0))
                            st.plotly_chart(fig_trend, use_container_width=True)

            else:
                # Placeholder State
                c1, c2 = st.columns(2)
                with c1:
                    with st.container(border=True):
                        st.markdown("### 🔒 Key Insights")
                        st.info("Run analysis to unlock.")
                with c2:
                    with st.container(border=True):
                        st.markdown("### 🔒 Recommended Charts")
                        st.info("Run analysis to unlock.")

elif st.session_state.page == "Data Copilot":
    st.markdown("""
        <style>
            .copilot-header {
                margin-bottom: 2rem;
            }
            .copilot-title {
                font-size: 2.5rem;
                font-weight: 700;
                color: #0f172a;
                margin-bottom: 0.5rem;
            }
            .copilot-subtitle {
                font-size: 1.1rem;
                color: #64748b;
            }
            
            .copilot-card {
                background: white;
                border-radius: 16px;
                padding: 1.5rem;
                border: 1px solid #e2e8f0;
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
                height: 600px;
                display: flex;
                flex-direction: column;
            }
            .card-header-row {
                display: flex;
                align-items: center;
                margin-bottom: 1.5rem;
                padding-bottom: 1rem;
                border-bottom: 1px solid #f1f5f9;
            }
            .header-icon-box {
                width: 40px;
                height: 40px;
                border-radius: 10px;
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                font-size: 1.25rem;
                margin-right: 1rem;
            }
            .bg-purple { background: #a855f7; }
            .bg-teal { background: #0ea5e9; }
            
            .card-title-text {
                font-size: 1.25rem;
                font-weight: 700;
                color: #1e293b;
            }
            .card-subtitle-caption {
                font-size: 0.85rem;
                color: #94a3b8;
                font-weight: 400;
            }
            
            .chat-bubble {
                background-color: #f1f5f9;
                padding: 1rem;
                border-radius: 12px;
                border-top-left-radius: 2px;
                color: #334155;
                margin-bottom: 1rem;
                line-height: 1.5;
            }
            
            /* Hide Streamlit default label for text input if needed */
            .stTextInput label {
                display: none;
            }
            
            /* Table Styling for Data Preview */
            .copilot-table {
                width: 100%;
                min-width: 1200px; /* Ensure wide enough for scrolling */
                border-collapse: collapse;
                margin-top: 1rem;
            }
            .copilot-table th {
                background-color: #f8fafc;
                color: #1e293b;
                font-weight: 600;
                padding: 0.75rem;
                text-align: left;
                border-bottom: 1px solid #e2e8f0;
                font-size: 0.9rem;
                white-space: nowrap; /* Prevent wrapping */
            }
            .copilot-table td {
                padding: 0.75rem;
                border-bottom: 1px solid #f1f5f9;
                color: #64748b;
                font-size: 0.9rem;
                white-space: nowrap; /* Prevent wrapping */
            }
            .copilot-table tr:last-child td {
                border-bottom: none;
            }
        </style>
        
        <div class="copilot-header">
            <div class="copilot-title">Data Copilot</div>
            <div class="copilot-subtitle">AI-powered assistant to explore and analyze your data</div>
        </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns([1, 1.5])
    
    with c1:
        # Chat Logic
        def handle_input():
            user_input = st.session_state.copilot_input
            if user_input:
                # Add user message
                st.session_state.copilot_history.append({"role": "user", "content": user_input})
                # Call Gemini API
                with st.spinner("Thinking..."):
                    answer = ask_copilot(st.session_state.df, user_input)
                # Add assistant message
                st.session_state.copilot_history.append({"role": "assistant", "content": answer})
                # Clear input (Streamlit hack: input is separate from key state in callback sometimes, but clearing session state key works for next render)
                st.session_state.copilot_input = ""

        # Build Chat HTML
        chat_html = ""
        for msg in st.session_state.copilot_history:
            content = msg["content"]
            display_html = ""
            
            # Handle structured response (dict) vs legacy string
            if isinstance(content, dict):
                main_text = content.get("content", "")
                code_text = content.get("code", "")
                
                # Convert newlines to br for main text if needed, or rely on markdown parsing? 
                # The chat bubble is just a div, so standard text formatting. 
                # Let's keep main text as is, maybe simple replacement for line breaks if raw string.
                main_text = main_text.replace("\n", "<br>") 
                
                if content.get("type") == "code" and code_text:
                    # Styled Code Block using HTML <details>
                    code_html = f"""
                    <div style="margin-top: 8px;">
                        <details style="border: 1px solid #e2e8f0; border-radius: 8px; overflow: hidden; background-color: white;">
                            <summary style="padding: 6px 12px; cursor: pointer; background-color: #f8fafc; font-size: 0.8rem; color: #64748b; font-weight: 500; outline: none; user-select: none;">
                                \U00002728 Thinking Process
                            </summary>
                            <div style="background-color: #0f172a; color: #f8fafc; padding: 12px; font-family: 'Consolas', 'Monaco', monospace; font-size: 0.8rem; overflow-x: auto; border-top: 1px solid #e2e8f0;">
                                <pre style="margin: 0; white-space: pre-wrap;">{code_text}</pre>
                            </div>
                        </details>
                    </div>
                    """
                    display_html = f"<div>{main_text}</div>{code_html}"
                else:
                    display_html = main_text
            else:
                # Legacy string
                display_html = str(content).replace("\n", "<br>")

            if msg["role"] == "user":
                chat_html += f'<div class="chat-bubble" style="background-color: #e0f2fe; color: #0369a1; align-self: flex-end; margin-left: auto; width: fit-content; max-width: 80%; text-align: right;">{display_html}</div>'
            else:
                chat_html += f'<div class="chat-bubble" style="background-color: #f1f5f9; color: #334155; align-self: flex-start; max-width: 90%;">{display_html}</div>'

        st.markdown(f"""
            <div class="copilot-card">
                <div class="card-header-row">
                    <div class="header-icon-box bg-purple">\U0001F916</div>
                    <div class="card-title-text">Chat Assistant</div>
                </div>
                <div id="chat-container" style="flex-grow: 1; overflow-y: auto; display: flex; flex-direction: column; gap: 10px; padding-right: 5px;">
                    {chat_html}
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # Auto-scroll Logic
        components.html("""
        <script>
            var container = window.parent.document.getElementById("chat-container");
            if (container) {
                container.scrollTop = container.scrollHeight;
            }
        </script>
        """, height=0, width=0)
        
        # Input - simulating positioning at bottom of card
        st.text_input("Ask about your data...", placeholder="Ask about your data...", key="copilot_input", label_visibility="collapsed", on_change=handle_input)
        st.markdown("<div style='margin-bottom: 2rem;'></div>", unsafe_allow_html=True)

    with c2:
        # Prepare content for the card
        if st.session_state.df is not None:
            # Convert head to HTML with custom class
            table_html = st.session_state.df.head().to_html(classes="copilot-table", border=0)
        else:
            table_html = "<div style='color: #94a3b8; padding: 1rem; text-align: center;'>Please upload a dataset in 'Data Source' to preview.</div>"
            
        st.markdown(f"""
            <div class="copilot-card" style="display: block; overflow: hidden;">
                <div class="card-header-row">
                    <div class="header-icon-box bg-teal">📊</div>
                    <div>
                        <div class="card-title-text">Data Preview</div>
                        <div class="card-subtitle-caption">head() - First 5 rows</div>
                    </div>
                </div>
                <div style="overflow-x: auto;">
                    {table_html}
                </div>
            </div>
        """, unsafe_allow_html=True)


if st.session_state.page == "Manual Exploration":
    # --- MANUAL EXPLORATION LOGIC (Integrated) ---
    st.markdown("""
    <div style="margin-top: -1rem; margin-bottom: 2rem;">
        <h1 style="color: #0f172a; font-size: 2rem; font-weight: 800;">Manual Exploration</h1>
        <p style="color: #64748b; font-size: 1rem;">Drag and drop variables to create custom visualizations</p>
    </div>
    """, unsafe_allow_html=True)

    df_me = st.session_state.df
    if df_me is None:
        st.warning("Please upload data in the 'Data Source' page first.")
        if st.button("Go to Data Source", key="me_go_back"):
            st.session_state.page = "Data Source"
            st.rerun()
    else:
        # Layout: variables on left, canvas on right
        me_col1, me_col2 = st.columns([1, 3])

        with me_col1:
            st.markdown("### Variables")
            st.caption("Available columns")
            
            # Display columns as 'cards'
            for col in df_me.columns:
                st.markdown(f"""
                <div style="
                    background-color: white;
                    padding: 10px;
                    margin-bottom: 8px;
                    border-radius: 8px;
                    border: 1px solid #e2e8f0;
                    color: #334155;
                    font-weight: 500;
                    display: flex;
                    align-items: center;
                    gap: 8px;
                    box-shadow: 0 1px 2px rgba(0,0,0,0.05);
                ">
                    <span style="color: #94a3b8; font-family: monospace;">::</span> {col}
                </div>
                """, unsafe_allow_html=True)

        with me_col2:
            st.markdown("### Canvas")
            st.caption("Configure axes and filters")

            # MAIN CANVAS CONTAINER
            with st.container(border=True):
                
                # 1. Controls
                cols_opts = ["None"] + list(df_me.columns)
                chart_types = ["Scatter", "Line", "Bar", "Area"]
                
                # Callbacks to sync Shadow Key -> Persistent Key
                def sync_x(): st.session_state.me_x = st.session_state._me_x
                def sync_y(): st.session_state.me_y = st.session_state._me_y
                def sync_color(): st.session_state.me_color = st.session_state._me_color
                def sync_type(): st.session_state.me_type = st.session_state._me_type
                
                # Get Indexes for Default Values
                try: idx_x = cols_opts.index(st.session_state.me_x)
                except: idx_x = 0
                
                try: idx_y = cols_opts.index(st.session_state.me_y)
                except: idx_y = 0
                
                try: idx_color = cols_opts.index(st.session_state.me_color)
                except: idx_color = 0

                try: idx_type = chart_types.index(st.session_state.me_type)
                except: idx_type = 0

                c1, c2 = st.columns(2)
                with c1:
                    x_axis = st.selectbox(
                        "X-Axis", 
                        options=cols_opts, 
                        index=idx_x, 
                        key="_me_x", 
                        on_change=sync_x
                    )
                    color_col = st.selectbox(
                        "Color", 
                        options=cols_opts, 
                        index=idx_color, 
                        key="_me_color", 
                        on_change=sync_color
                    )
                
                with c2:
                    y_axis = st.selectbox(
                        "Y-Axis", 
                        options=cols_opts, 
                        index=idx_y, 
                        key="_me_y", 
                        on_change=sync_y
                    )
                    chart_type = st.selectbox(
                        "Chart Type", 
                        chart_types, 
                        index=idx_type, 
                        key="_me_type", 
                        on_change=sync_type
                    )

                st.markdown("<hr style='margin: 1.5rem 0;'>", unsafe_allow_html=True)
                
                # 2. Visualization Logic
                # Use current widget values (which are synced to session state anyway)
                if x_axis != "None" and y_axis != "None":
                    try:
                        if chart_type == "Scatter":
                            fig = px.scatter(df_me, x=x_axis, y=y_axis, color=color_col if color_col != "None" else None)
                        elif chart_type == "Line":
                            fig = px.line(df_me, x=x_axis, y=y_axis, color=color_col if color_col != "None" else None)
                        elif chart_type == "Bar":
                            fig = px.bar(df_me, x=x_axis, y=y_axis, color=color_col if color_col != "None" else None)
                        elif chart_type == "Area":
                            fig = px.area(df_me, x=x_axis, y=y_axis, color=color_col if color_col != "None" else None)
                        
                        fig.update_layout(
                            paper_bgcolor='rgba(0,0,0,0)',
                            plot_bgcolor='rgba(0,0,0,0)',
                            height=500,
                            margin=dict(t=20, l=20, r=20, b=20)
                        )
                        st.plotly_chart(fig, use_container_width=True)
                        
                    except Exception as e:
                        st.error(f"Could not generate chart: {e}")
                else:
                     st.markdown("""
                    <div style="text-align: center; color: #94a3b8; padding: 4rem;">
                        <div style="margin-bottom: 1rem; font-size: 2rem; opacity: 0.5;">📊</div>
                        <p>Select multiple variables above to generate visualization</p>
                    </div>
                    """, unsafe_allow_html=True)


elif st.session_state.page == "Dashboard":
    # --- HEADER ---
    if st.session_state.focused_chart_index is None:
        st.markdown("""
        <div style="margin-top: -1rem; margin-bottom: 2rem;">
            <h1 style="color: #0f172a; font-size: 2rem; font-weight: 800;">Dashboard</h1>
            <p style="color: #64748b; font-size: 1rem;">Create and customize interactive dashboards</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        if st.button("← Back to Dashboard"):
            st.session_state.focused_chart_index = None
            st.rerun()

    # --- CONTENT ---
    if st.session_state.df is None:
        st.warning("No data loaded. Please go to the 'Data Source' page to upload a file.")
        if st.button("Go to Data Source"):
            st.session_state.page = "Data Source"
            st.rerun()
    else:
        # USE FILTERED DATA
        df = df_display # This comes from sidebar logic
        col_types = st.session_state.col_types
        
        if not st.session_state.dashboard_generated:
            # RENDER THE SMART BUILDER CARD
            st.markdown("""
            <div class="smart-builder-card">
                <div style="background: rgba(255,255,255,0.2); width: 60px; height: 60px; border-radius: 12px; display: flex; align-items: center; justify-content: center; margin-bottom: 1.5rem;">
                    <svg width="30" height="30" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M4 4H10V10H4V4ZM14 4H20V10H14V4ZM4 14H10V20H4V14ZM14 14H20V20H14V14Z" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                </div>
                <h2>Smart Dashboard Builder</h2>
                <p>AI can design a dashboard based on your data automatically</p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("Generate Dashboard", type="primary"):
                st.session_state.dashboard_generated = True
                st.rerun()
        else:
            # DASHBOARD IS GENERATED
            kpi_cols = identify_key_metrics(df, col_types)
            charts = generate_dashboard_charts(df, col_types, kpi_cols)
            
            # Focused View
            if st.session_state.focused_chart_index is not None:
                 idx = st.session_state.focused_chart_index
                 if 0 <= idx < len(charts):
                     chart_data = charts[idx]
                     st.markdown(f"## 🔍 View: {chart_data.get('title', 'Chart')}")
                     fig = chart_data['fig']
                     fig.update_layout(height=700, margin=dict(t=50, l=50, r=50, b=50))
                     st.plotly_chart(fig, use_container_width=True)
            
            # Grid View
            else:
                # KPIs
                if kpi_cols:
                    cols = st.columns(min(len(kpi_cols), 4))
                    for i, col in enumerate(kpi_cols[:4]):
                        val = df[col].sum()
                        cols[i].metric(col, format_number(val))
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                # Charts
                cols_per_row = 3
                for i in range(0, len(charts), cols_per_row):
                    row_charts = charts[i:i+cols_per_row]
                    cols = st.columns(cols_per_row)
                    for j, chart_data in enumerate(row_charts):
                        chart_index = i + j
                        with cols[j]:
                            st.plotly_chart(chart_data['fig'], use_container_width=True)
                            if st.button(f"🔍 Enlarge", key=f"btn_{chart_index}"): #Enlarge Button for viewing the chart in Full-View.
                                st.session_state.focused_chart_index = chart_index
                                st.rerun()
