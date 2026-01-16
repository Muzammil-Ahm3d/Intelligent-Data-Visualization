# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
from src.loader import load_data
from src.analysis import get_column_types, identify_key_metrics
from src.visualizer import generate_dashboard_charts, format_number
from src.copilot import ask_copilot 
from src.demo_data import load_demo_data # Added import
from dotenv import load_dotenv

load_dotenv()
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import streamlit.components.v1 as components

# --- HELPER: CHECK DATA LOADED ---
def check_data_loaded():
    if st.session_state.df is None:
        st.markdown("""
        <div style="background: linear-gradient(135deg, rgba(30, 41, 59, 0.8) 0%, rgba(15, 23, 42, 0.9) 100%); border: 1px solid rgba(99, 102, 241, 0.3); border-radius: 16px; padding: 2.5rem; text-align: center; margin-top: 2rem; margin-bottom: 2rem; box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);">
            <div style="background: linear-gradient(135deg, rgba(99, 102, 241, 0.2) 0%, rgba(139, 92, 246, 0.2) 100%); width: 60px; height: 60px; border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; margin-bottom: 1rem; border: 1px solid rgba(99, 102, 241, 0.3);">
                <span style="font-size: 2rem;">🚀</span>
            </div>
            <h3 style="color: #f1f5f9; margin-bottom: 0.5rem; font-weight: 700;">Exploration Ready</h3>
            <p style="color: #94a3b8; margin-bottom: 0rem; max-width: 500px; margin-left: auto; margin-right: auto;">
                This tool requires a dataset to generate insights. You can upload your own file or instantly launch our pre-loaded Global Weather demo.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Centered Layout for Buttons
        # [1, 2, 1] creates a center column that is 50% of width (2/4)
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
             # Equal width columns for buttons
             col_demo, col_upload = st.columns(2, gap="large")
             with col_demo:
                 if st.button("🚀 Launch Weather Demo", type="primary", width="stretch"):
                     with st.spinner("Loading demo data..."):
                         df = load_demo_data()
                         if df is not None:
                             st.session_state.df = df
                             st.session_state.col_types = get_column_types(df)
                             st.session_state.uploaded_file_name = "Global_Weather_Demo.xlsx"
                             st.session_state.dashboard_generated = False
                             st.rerun()
             with col_upload:
                 if st.button("📂 Go to Data Source", width="stretch"):
                     st.session_state.page = "Data Source"
                     st.rerun()
        
        return False
    return True

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
if 'copilot_usage_count' not in st.session_state:
    st.session_state.copilot_usage_count = 0 


# --- CUSTOM CSS ---
st.markdown("""
<style>
    /* Main Background */
    .stApp {
        background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 50%, #16213e 100%);
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
    
    /* Chart Cards - Dark Theme */
    .stPlotlyChart {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.8) 0%, rgba(15, 23, 42, 0.9) 100%);
        border-radius: 16px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        padding: 15px;
        border: 1px solid rgba(99, 102, 241, 0.2);
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .stPlotlyChart:hover {
        border-color: rgba(99, 102, 241, 0.4);
        box-shadow: 0 12px 40px rgba(99, 102, 241, 0.15);
    }

    /* Metrics - Dark Theme */
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.8) 0%, rgba(15, 23, 42, 0.9) 100%);
        padding: 18px;
        border-radius: 16px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        text-align: center;
        border: 1px solid rgba(99, 102, 241, 0.2);
    }
    div[data-testid="stMetric"] label {
        color: #94a3b8 !important;
    }
    div[data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: #f1f5f9 !important;
    }
    
    /* Global Primary Button Style - Gradient */
    div.stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%) !important;
        border: 1px solid rgba(99, 102, 241, 0.5) !important;
        color: white !important;
        font-weight: 600;
        border-radius: 12px;
        padding: 0.6rem 1.2rem;
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3);
        transition: all 0.3s ease;
    }
    div.stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%) !important;
        border-color: rgba(99, 102, 241, 0.8) !important;
        box-shadow: 0 8px 25px rgba(99, 102, 241, 0.4);
        transform: translateY(-2px);
    }
    
    /* Secondary Buttons - Dark Theme */
    div.stButton > button:not([kind="primary"]) {
        background: rgba(30, 41, 59, 0.6) !important;
        border: 1px solid rgba(99, 102, 241, 0.3) !important;
        color: #c7d2fe !important;
        border-radius: 12px;
        transition: all 0.3s ease;
    }
    div.stButton > button:not([kind="primary"]):hover {
        background: rgba(99, 102, 241, 0.2) !important;
        border-color: rgba(99, 102, 241, 0.5) !important;
        color: #fff !important;
    }
    
    /* File Uploader - Dark Theme */
    div[data-testid='stFileUploader'] {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.8) 0%, rgba(15, 23, 42, 0.9) 100%) !important;
        border: 2px dashed rgba(99, 102, 241, 0.4) !important;
        border-radius: 16px;
    }
    div[data-testid='stFileUploader']:hover {
        border-color: rgba(99, 102, 241, 0.7) !important;
    }
    div[data-testid='stFileUploader'] section {
        color: #94a3b8;
    }
    
    /* Text Input - Dark Theme */
    .stTextInput input, .stSelectbox select, .stMultiSelect div[data-baseweb="select"] {
        background: rgba(30, 41, 59, 0.8) !important;
        border-color: rgba(99, 102, 241, 0.3) !important;
        color: #f1f5f9 !important;
        border-radius: 12px;
    }
    
    /* Expander - Dark Theme */
    .streamlit-expanderHeader {
        background: rgba(30, 41, 59, 0.8) !important;
        border-radius: 12px;
        color: #f1f5f9 !important;
    }
    
    /* Info/Warning boxes - Dark Theme */
    .stAlert {
        background: rgba(30, 41, 59, 0.8) !important;
        border-radius: 12px;
        border-left: 4px solid rgba(99, 102, 241, 0.6) !important;
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

# --- CURSOR TRAIL EFFECT (Antigravity Style) ---
import streamlit.components.v1 as components
cursor_effect_html = """
<style>
    .cursor-glow {
        position: fixed;
        pointer-events: none;
        z-index: 9999;
        border-radius: 50%;
        mix-blend-mode: screen;
        filter: blur(1px);
        opacity: 0;
        transition: opacity 0.3s ease;
    }
    .cursor-glow.active {
        opacity: 1;
    }
    .cursor-glow-1 {
        width: 400px;
        height: 400px;
        background: radial-gradient(circle, rgba(99, 102, 241, 0.15) 0%, rgba(139, 92, 246, 0.08) 40%, transparent 70%);
    }
    .cursor-glow-2 {
        width: 250px;
        height: 250px;
        background: radial-gradient(circle, rgba(168, 85, 247, 0.2) 0%, rgba(236, 72, 153, 0.1) 40%, transparent 70%);
    }
    .cursor-glow-3 {
        width: 120px;
        height: 120px;
        background: radial-gradient(circle, rgba(59, 130, 246, 0.25) 0%, rgba(34, 211, 238, 0.15) 40%, transparent 70%);
    }
    
    /* Floating particles */
    .cursor-particle {
        position: fixed;
        pointer-events: none;
        z-index: 9998;
        border-radius: 50%;
        opacity: 0;
        transition: opacity 0.2s ease;
    }
    .cursor-particle.active {
        opacity: 1;
    }
</style>

<div class="cursor-glow cursor-glow-1" id="glow1"></div>
<div class="cursor-glow cursor-glow-2" id="glow2"></div>
<div class="cursor-glow cursor-glow-3" id="glow3"></div>

<script>
(function() {
    const parentDoc = window.parent.document;
    
    // Check if already injected
    if (parentDoc.getElementById('cursor-effect-container')) return;
    
    // Create container
    const container = parentDoc.createElement('div');
    container.id = 'cursor-effect-container';
    container.innerHTML = `
        <style>
            .cursor-glow {
                position: fixed;
                pointer-events: none;
                z-index: 9999;
                border-radius: 50%;
                mix-blend-mode: screen;
                filter: blur(2px);
                opacity: 0;
                transition: opacity 0.5s ease;
                will-change: transform;
            }
            .cursor-glow.active {
                opacity: 1;
            }
            .cursor-glow-1 {
                width: 500px;
                height: 500px;
                background: radial-gradient(circle, 
                    rgba(99, 102, 241, 0.12) 0%, 
                    rgba(139, 92, 246, 0.06) 30%, 
                    rgba(168, 85, 247, 0.03) 50%,
                    transparent 70%);
            }
            .cursor-glow-2 {
                width: 300px;
                height: 300px;
                background: radial-gradient(circle, 
                    rgba(168, 85, 247, 0.18) 0%, 
                    rgba(236, 72, 153, 0.08) 40%, 
                    transparent 70%);
            }
            .cursor-glow-3 {
                width: 150px;
                height: 150px;
                background: radial-gradient(circle, 
                    rgba(59, 130, 246, 0.22) 0%, 
                    rgba(34, 211, 238, 0.12) 40%, 
                    transparent 70%);
            }
            
            /* Small trailing particles */
            .trail-dot {
                position: fixed;
                pointer-events: none;
                z-index: 9997;
                border-radius: 50%;
                opacity: 0;
                transition: opacity 0.15s ease, transform 0.15s ease;
            }
        </style>
        <div class="cursor-glow cursor-glow-1" id="parentGlow1"></div>
        <div class="cursor-glow cursor-glow-2" id="parentGlow2"></div>
        <div class="cursor-glow cursor-glow-3" id="parentGlow3"></div>
    `;
    parentDoc.body.appendChild(container);
    
    const glow1 = parentDoc.getElementById('parentGlow1');
    const glow2 = parentDoc.getElementById('parentGlow2');
    const glow3 = parentDoc.getElementById('parentGlow3');
    
    // Trail particles
    const particles = [];
    const particleCount = 8;
    const colors = [
        'rgba(99, 102, 241, 0.6)',
        'rgba(139, 92, 246, 0.6)',
        'rgba(168, 85, 247, 0.6)',
        'rgba(236, 72, 153, 0.5)',
        'rgba(59, 130, 246, 0.6)',
        'rgba(34, 211, 238, 0.5)',
        'rgba(129, 140, 248, 0.6)',
        'rgba(192, 132, 252, 0.5)'
    ];
    
    for (let i = 0; i < particleCount; i++) {
        const dot = parentDoc.createElement('div');
        dot.className = 'trail-dot';
        dot.style.width = (4 + Math.random() * 4) + 'px';
        dot.style.height = dot.style.width;
        dot.style.background = colors[i % colors.length];
        dot.style.boxShadow = '0 0 ' + (5 + i * 2) + 'px ' + colors[i % colors.length];
        parentDoc.body.appendChild(dot);
        particles.push({
            el: dot,
            x: 0,
            y: 0,
            delay: (i + 1) * 0.08
        });
    }
    
    // Mouse tracking
    let mouseX = 0, mouseY = 0;
    let glow1X = 0, glow1Y = 0;
    let glow2X = 0, glow2Y = 0;
    let glow3X = 0, glow3Y = 0;
    let isActive = false;
    
    parentDoc.addEventListener('mousemove', (e) => {
        mouseX = e.clientX;
        mouseY = e.clientY;
        
        if (!isActive) {
            isActive = true;
            glow1.classList.add('active');
            glow2.classList.add('active');
            glow3.classList.add('active');
            particles.forEach(p => p.el.style.opacity = '1');
        }
    });
    
    parentDoc.addEventListener('mouseleave', () => {
        isActive = false;
        glow1.classList.remove('active');
        glow2.classList.remove('active');
        glow3.classList.remove('active');
        particles.forEach(p => p.el.style.opacity = '0');
    });
    
    // Animation loop with easing
    function animate() {
        // Main glows with different follow speeds
        const ease1 = 0.06;
        const ease2 = 0.08;
        const ease3 = 0.12;
        
        glow1X += (mouseX - glow1X) * ease1;
        glow1Y += (mouseY - glow1Y) * ease1;
        glow2X += (mouseX - glow2X) * ease2;
        glow2Y += (mouseY - glow2Y) * ease2;
        glow3X += (mouseX - glow3X) * ease3;
        glow3Y += (mouseY - glow3Y) * ease3;
        
        glow1.style.transform = `translate(${glow1X - 250}px, ${glow1Y - 250}px)`;
        glow2.style.transform = `translate(${glow2X - 150}px, ${glow2Y - 150}px)`;
        glow3.style.transform = `translate(${glow3X - 75}px, ${glow3Y - 75}px)`;
        
        // Trail particles
        particles.forEach((p, i) => {
            const prevP = i === 0 ? {x: mouseX, y: mouseY} : particles[i - 1];
            p.x += (prevP.x - p.x) * (0.3 - i * 0.02);
            p.y += (prevP.y - p.y) * (0.3 - i * 0.02);
            p.el.style.transform = `translate(${p.x - 3}px, ${p.y - 3}px) scale(${1 - i * 0.08})`;
        });
        
        requestAnimationFrame(animate);
    }
    
    animate();
})();
</script>
"""
components.html(cursor_effect_html, height=0, scrolling=False)

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
                background: linear-gradient(135deg, 
                    rgba(99, 102, 241, 0.08) 0%, 
                    rgba(168, 85, 247, 0.06) 25%,
                    rgba(236, 72, 153, 0.04) 50%,
                    rgba(34, 211, 238, 0.06) 75%,
                    rgba(255, 255, 255, 0) 100%);
                border-radius: 24px;
                margin-bottom: 2rem;
                position: relative;
                overflow: hidden;
            }
            .hero-container::before {
                content: '';
                position: absolute;
                top: -50%;
                left: -50%;
                width: 200%;
                height: 200%;
                background: radial-gradient(circle at 30% 20%, rgba(99, 102, 241, 0.15) 0%, transparent 50%),
                            radial-gradient(circle at 70% 80%, rgba(236, 72, 153, 0.1) 0%, transparent 50%),
                            radial-gradient(circle at 80% 30%, rgba(34, 211, 238, 0.1) 0%, transparent 40%);
                animation: shimmer 15s ease-in-out infinite alternate;
                pointer-events: none;
            }
            @keyframes shimmer {
                0% { transform: translate(0, 0) rotate(0deg); }
                100% { transform: translate(5%, 5%) rotate(3deg); }
            }
            .hero-title {
                font-size: 3.5rem;
                font-weight: 800;
                margin-bottom: 1rem;
                color: #f1f5f9;
                position: relative;
                z-index: 1;
            }
            .hero-title span {
                background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 40%, #d946ef 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }
            .hero-subtitle {
                font-size: 1.25rem;
                color: #94a3b8;
                max-width: 600px;
                margin: 0 auto 2rem auto;
                line-height: 1.6;
                position: relative;
                z-index: 1;
            }
            .cta-button {
                display: inline-block;
                background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #a855f7 100%);
                color: white;
                font-weight: 600;
                padding: 0.8rem 2rem;
                border-radius: 12px;
                text-decoration: none;
                transition: all 0.3s ease;
                box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3);
            }
            .cta-button:hover {
                transform: translateY(-2px);
                box-shadow: 0 8px 25px rgba(99, 102, 241, 0.4);
            }
            
            /* 3D Feature Cards - Dark Theme */
            .card-wrapper {
                perspective: 1000px;
                height: 100%;
            }
            .feature-card {
                background: linear-gradient(135deg, rgba(30, 41, 59, 0.8) 0%, rgba(15, 23, 42, 0.9) 100%);
                backdrop-filter: blur(20px);
                border-radius: 20px;
                padding: 1.75rem;
                border: 1px solid rgba(99, 102, 241, 0.2);
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3),
                            0 2px 8px rgba(0, 0, 0, 0.2),
                            inset 0 1px 0 rgba(255, 255, 255, 0.05);
                height: 100%;
                transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
                transform-style: preserve-3d;
                position: relative;
                overflow: visible;
            }
            .feature-card::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: linear-gradient(135deg, 
                    rgba(99, 102, 241, 0.1) 0%, 
                    rgba(168, 85, 247, 0.08) 50%,
                    rgba(236, 72, 153, 0.05) 100%);
                opacity: 0;
                transition: opacity 0.3s ease;
                pointer-events: none;
                border-radius: 20px;
            }
            .feature-card:hover::before {
                opacity: 1;
            }
            .feature-card:hover {
                transform: translateY(-8px);
                box-shadow: 0 20px 40px rgba(99, 102, 241, 0.2),
                            0 8px 16px rgba(0, 0, 0, 0.25),
                            inset 0 1px 0 rgba(255, 255, 255, 0.1);
                border-color: rgba(99, 102, 241, 0.5);
            }
            
            
            /* Card Header with Icon and Info Button */
            .card-header {
                display: flex;
                justify-content: space-between;
                align-items: flex-start;
                margin-bottom: 1rem;
            }
            .feature-icon-box {
                width: 56px;
                height: 56px;
                border-radius: 16px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 1.6rem;
                color: white;
                box-shadow: 0 8px 20px rgba(0, 0, 0, 0.3);
                transform: translateZ(20px);
                transition: transform 0.3s ease, box-shadow 0.3s ease;
            }
            .feature-card:hover .feature-icon-box {
                transform: translateZ(40px) scale(1.1);
                box-shadow: 0 12px 30px rgba(0, 0, 0, 0.4);
            }
            .info-btn {
                width: 32px;
                height: 32px;
                border-radius: 50%;
                background: rgba(99, 102, 241, 0.2);
                border: 1px solid rgba(99, 102, 241, 0.3);
                color: #a5b4fc;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 0.9rem;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
                text-decoration: none;
                position: relative;
                z-index: 100;
            }
            .info-btn:hover {
                background: rgba(99, 102, 241, 0.4);
                border-color: rgba(99, 102, 241, 0.6);
                color: #fff;
                transform: scale(1.1);
                z-index: 1000;
            }
            /* Tooltip popup - positioned below-left */
            .info-btn::after {
                content: attr(data-tooltip);
                position: absolute;
                top: calc(100% + 12px);
                right: 0;
                width: 280px;
                padding: 16px;
                background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
                border: 1px solid rgba(99, 102, 241, 0.5);
                border-radius: 14px;
                color: #e2e8f0;
                font-size: 0.85rem;
                font-weight: 400;
                line-height: 1.7;
                text-align: left;
                box-shadow: 0 20px 50px rgba(0, 0, 0, 0.6),
                            0 0 30px rgba(99, 102, 241, 0.15);
                opacity: 0;
                visibility: hidden;
                transition: all 0.25s ease;
                z-index: 10000;
                pointer-events: none;
                white-space: pre-wrap;
                transform: translateY(-10px);
            }
            /* Arrow pointing up */
            .info-btn::before {
                content: '';
                position: absolute;
                top: calc(100% + 4px);
                right: 8px;
                border: 8px solid transparent;
                border-bottom-color: rgba(99, 102, 241, 0.5);
                opacity: 0;
                visibility: hidden;
                transition: all 0.25s ease;
                z-index: 10001;
            }
            .info-btn:hover::after {
                opacity: 1;
                visibility: visible;
                transform: translateY(0);
            }
            .info-btn:hover::before {
                opacity: 1;
                visibility: visible;
            }
            .icon-purple { 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%); 
            }
            .icon-blue { 
                background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); 
            }
            .icon-green { 
                background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); 
            }
            
            .card-title {
                font-size: 1.25rem;
                font-weight: 700;
                color: #f1f5f9;
                margin-bottom: 0.5rem;
                transform: translateZ(15px);
            }
            .card-desc {
                color: #94a3b8;
                font-size: 0.95rem;
                line-height: 1.6;
                transform: translateZ(10px);
                margin-bottom: 1.25rem;
            }
            .card-action-btn {
                display: block;
                width: 100%;
                padding: 0.75rem 1rem;
                background: linear-gradient(135deg, rgba(99, 102, 241, 0.3) 0%, rgba(139, 92, 246, 0.3) 100%);
                border: 1px solid rgba(99, 102, 241, 0.4);
                border-radius: 12px;
                color: #c7d2fe;
                font-weight: 600;
                font-size: 0.9rem;
                text-align: center;
                text-decoration: none;
                cursor: pointer;
                transition: all 0.3s ease;
            }
            .card-action-btn:hover {
                background: linear-gradient(135deg, rgba(99, 102, 241, 0.5) 0%, rgba(139, 92, 246, 0.5) 100%);
                border-color: rgba(99, 102, 241, 0.6);
                color: #fff;
                transform: translateY(-2px);
                box-shadow: 0 8px 20px rgba(99, 102, 241, 0.3);
            }
            
            .key-feature-banner {
                background: linear-gradient(135deg, 
                    #667eea 0%, 
                    #764ba2 30%, 
                    #f093fb 70%, 
                    #4facfe 100%);
                background-size: 200% 200%;
                animation: gradient-shift 8s ease infinite;
                border-radius: 20px;
                padding: 3rem;
                color: white;
                margin-top: 3rem;
                box-shadow: 0 20px 40px rgba(102, 126, 234, 0.3);
                position: relative;
                overflow: hidden;
            }
            .key-feature-banner::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: linear-gradient(45deg, 
                    rgba(255,255,255,0.1) 0%, 
                    transparent 50%, 
                    rgba(255,255,255,0.1) 100%);
                pointer-events: none;
            }
            @keyframes gradient-shift {
                0% { background-position: 0% 50%; }
                50% { background-position: 100% 50%; }
                100% { background-position: 0% 50%; }
            }
        </style>
        
        <div class="hero-container">
            <div class="hero-title">Welcome to <span>IDV</span></div>
            <div class="hero-subtitle">
                AI-powered data analytics and visualization platform. Explore, analyze, and discover insights automatically.
            </div>
            <!-- Hacky inline click to switch session state? No, standard button below -->
        </div>
    """, unsafe_allow_html=True)
    
    # CTA Button using Streamlit
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("Get Started →", type="primary", width="stretch"):
            st.session_state.page = "Data Source"
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # Feature Cards as Clickable Buttons
    # We use newlines to separate Title and Description visually, combined with CSS 'white-space: pre-wrap'
    
    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.markdown("""
            <div class="feature-card">
                <div class="card-header">
                    <div class="feature-icon-box icon-purple">✨</div>
                    <div class="info-btn" data-tooltip="📊 Data Profiling: Scans columns to detect types (Numerical, Categorical, Time-series). 📈 Statistical Analysis: Calculates mean, median, std dev. 🔍 Outlier Detection: Uses IQR method to flag anomalies.">i</div>
                </div>
                <div class="card-title">Auto Exploration</div>
                <div class="card-desc">Let AI automatically discover patterns and insights in your data with one click.</div>
            </div>
        """, unsafe_allow_html=True)
        if st.button("🚀 Launch", key="btn_nav_ae", type="primary", use_container_width=True):
            st.session_state.page = "Auto Exploration"
            st.rerun()
        
    with c2:
        st.markdown("""
            <div class="feature-card">
                <div class="card-header">
                    <div class="feature-icon-box icon-blue">🤖</div>
                    <div class="info-btn" data-tooltip="🧠 Intent Recognition: Uses Gemini AI for natural language queries. 💻 Code Generation: Writes Python/Plotly code dynamically. 📋 Context Aware: Fed with dataframe schema for accuracy.">i</div>
                </div>
                <div class="card-title">Data Copilot</div>
                <div class="card-desc">Get AI-powered chart recommendations based on your selected variables.</div>
            </div>
        """, unsafe_allow_html=True)
        if st.button("🚀 Launch", key="btn_nav_dc", type="primary", use_container_width=True):
            st.session_state.page = "Data Copilot"
            st.rerun()
        
    with c3:
        st.markdown("""
            <div class="feature-card">
                <div class="card-header">
                    <div class="feature-icon-box icon-green">📈</div>
                    <div class="info-btn" data-tooltip="🎯 Heuristic Selection: Auto-picks best chart types. ⚙️ Rule Engine: Time series→Line, Low cardinality→Pie/Bar. 📊 KPI Extraction: Sums key metrics automatically.">i</div>
                </div>
                <div class="card-title">Smart Dashboard</div>
                <div class="card-desc">Interactive dashboard with AI-curated charts and key performance indicators.</div>
            </div>
        """, unsafe_allow_html=True)
        if st.button("🚀 Launch", key="btn_nav_dashboard", type="primary", use_container_width=True):
            st.session_state.page = "Dashboard"
            st.rerun()
        
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
        <div style="background: linear-gradient(135deg, rgba(30, 41, 59, 0.8) 0%, rgba(15, 23, 42, 0.9) 100%); border: 1px solid rgba(34, 197, 94, 0.3); border-radius: 16px; padding: 1.5rem; margin-bottom: 2rem; display: flex; align-items: center; justify-content: space-between; box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);">
            <div style="display: flex; align-items: center; gap: 1rem;">
                <div style="background: linear-gradient(135deg, rgba(34, 197, 94, 0.2) 0%, rgba(22, 163, 74, 0.3) 100%); color: #4ade80; padding: 12px; border-radius: 50%; border: 1px solid rgba(34, 197, 94, 0.3);">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M20 6L9 17L4 12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                </div>
                <div>
                    <h4 style="margin: 0; color: #f1f5f9; font-weight: 600;">Data Ready: {st.session_state.get('uploaded_file_name', 'Dataset')}</h4>
                    <p style="margin: 0; color: #94a3b8; font-size: 0.9rem;">{len(st.session_state.df)} rows loaded successfully</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
             if st.button("Proceed to Dashboard →", type="primary", width="stretch"):
                    st.session_state.page = "Dashboard"
                    st.rerun()
        
        st.markdown("<div style='text-align: center; color: #94a3b8; margin: 2rem 0;'>— OR UPLOAD NEW FILE —</div>", unsafe_allow_html=True)
    
    # 2. UPLOAD AREA (Split into Upload and Quick Start)
    
    # Using 2 columns layout for Desktop
    col_upload_area, col_quick_start = st.columns([1.5, 1])
    
    with col_upload_area:
        st.markdown("""
            <div style="background: linear-gradient(135deg, rgba(30, 41, 59, 0.8) 0%, rgba(15, 23, 42, 0.9) 100%); border: 2px dashed rgba(99, 102, 241, 0.4); border-radius: 16px; padding: 2rem; text-align: center; height: 100%;">
                <div style="background: linear-gradient(135deg, rgba(99, 102, 241, 0.2) 0%, rgba(139, 92, 246, 0.2) 100%); width:60px; height:60px; border-radius:50%; display:inline-flex; align-items:center; justify-content:center; margin-bottom:10px; border: 1px solid rgba(99, 102, 241, 0.3);">
                    <svg width="30" height="30" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" stroke="#818cf8" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                </div>
                <h3 style="margin:0; color:#f1f5f9; font-size:1.2rem;">Upload Your Data</h3>
                <p style="color: #94a3b8; font-size: 0.9rem; margin-top: 0.5rem; margin-bottom: 1.5rem;">Supported: CSV, Excel (Max 200MB)</p>
        """, unsafe_allow_html=True)
        
        # Determine unique key based on state to force reset if needed, though simple key works
        uploaded_file = st.file_uploader("Upload CSV or Excel", type=["csv", "xlsx"], key="main_uploader", label_visibility="collapsed")
        
        st.markdown("</div>", unsafe_allow_html=True)

    with col_quick_start:
         st.markdown("""
            <div style="background: linear-gradient(135deg, rgba(30, 41, 59, 0.8) 0%, rgba(15, 23, 42, 0.9) 100%); border: 1px solid rgba(99, 102, 241, 0.3); border-radius: 16px; padding: 2rem; box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3); position: relative; overflow: hidden;">
                <div style="position: absolute; top: 0; right: 0; background: linear-gradient(135deg, rgba(34, 211, 238, 0.2) 0%, rgba(6, 182, 212, 0.3) 100%); color: #22d3ee; font-size: 0.7rem; font-weight: 700; padding: 4px 12px; border-bottom-left-radius: 12px; border: 1px solid rgba(34, 211, 238, 0.3);">NEW</div>
                <h3 style="margin-top:0; color:#f1f5f9; font-size:1.2rem; display: flex; align-items: center; gap: 8px;">
                    🚀 Quick Start
                </h3>
                <p style="color: #94a3b8; font-size: 0.95rem; line-height: 1.5; margin-bottom: 0;">
                    Don't have a dataset? Try our pre-loaded <span style="color: #818cf8; font-weight: 600;">Global Weather Analytics</span> demo to see the platform's power.
                </p>
            </div>
            <div style="height: 15px;"></div>
        """, unsafe_allow_html=True)
         
         if st.button("Load Demo Data", type="primary", width="stretch"):
             with st.spinner("Loading global weather data..."):
                 df = load_demo_data()
                 if df is not None:
                     st.session_state.df = df
                     st.session_state.col_types = get_column_types(df)
                     st.session_state.uploaded_file_name = "Global_Weather_Demo.xlsx"
                     st.session_state.dashboard_generated = False
                     
                     # AUTO GENERATE ANALYTICS - REMOVED as per user request
                     # st.session_state.page = "Auto Exploration"
                     # st.session_state.auto_analysis_run = True 
                     
                     st.toast("Demo data loaded successfully!", icon="🚀")
                     st.rerun()
         
         st.markdown("<div style='text-align: center; margin-top: 10px;'><a href='#' style='color: #94a3b8; font-size: 0.85rem; text-decoration: none;'>Download Sample Excel</a></div>", unsafe_allow_html=True)

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
    
    # --- PAGE SPECIFIC CSS (Chart Overflow Fix + Button Styling) ---
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
        
        /* FIX: Chart Overflow - Ensure charts stay within container */
        [data-testid="stVerticalBlock"] .stPlotlyChart {
            max-width: 100% !important;
            overflow: hidden !important;
        }
        
        [data-testid="stVerticalBlock"] .stPlotlyChart > div {
            max-width: 100% !important;
            overflow: hidden !important;
        }
        
        /* Ensure iframe/plot containers respect parent width */
        .stPlotlyChart iframe,
        .stPlotlyChart .plotly-graph-div {
            max-width: 100% !important;
        }
        
        /* Container constraints for bordered containers */
        div[data-testid="stVerticalBlockBorderWrapper"] {
            overflow: hidden !important;
        }
        
        div[data-testid="stVerticalBlockBorderWrapper"] > div {
            overflow: hidden !important;
        }
        
        /* Smart Charts section specific fix */
        .element-container {
            max-width: 100% !important;
        }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="margin-top: -1rem; margin-bottom: 2rem;">
        <h1 style="color: #f1f5f9; font-size: 2rem; font-weight: 800;">Auto Exploration</h1>
        <p style="color: #94a3b8; font-size: 1rem;">Let AI automatically discover insights in your data</p>
    </div>
    """, unsafe_allow_html=True)

    if not check_data_loaded():
        pass # The helper renders the UI
    
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
                    fig.update_layout(height=800, autosize=True)
                    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': True})
                    
            elif chart_type == "Distribution Analysis":
                 if not num_df.empty:
                    target_col = num_df.std().idxmax()
                    fig = px.box(df_ae, y=target_col, points="outliers", title=f"Distribution of {target_col}")
                    fig.update_layout(height=800, autosize=True)
                    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': True})
                    
            elif chart_type == "Trend Analysis":
                if len(date_cols) > 0 and not num_df.empty:
                    date_col = date_cols[0]
                    val_col = num_df.columns[0]
                    df_trend = df_ae.sort_values(by=date_col)
                    fig = px.line(df_trend, x=date_col, y=val_col, title=f"{val_col} over {date_col}")
                    fig.update_layout(height=800, autosize=True)
                    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': True})
        
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

                # RENDER SUMMARY - Dark Theme
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, rgba(30, 41, 59, 0.9) 0%, rgba(15, 23, 42, 0.95) 100%); border: 1px solid rgba(99, 102, 241, 0.3); border-radius: 12px; padding: 1.5rem; margin-bottom: 2rem; border-left: 5px solid #6366f1; box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);">
                    <h3 style="margin-top: 0; color: #f1f5f9; font-size: 1.2rem; display: flex; align-items: center; gap: 8px;">
                        ⚡ Executive Summary
                    </h3>
                    <p style="color: #cbd5e1; line-height: 1.6; margin-bottom: 0;">
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
                                        <strong style="color: #f1f5f9;">{col}</strong>: Found <span style="color:#ef4444; font-weight: 600;">{len(outliers)} outliers</span> 
                                        <span style="color: #94a3b8;">(Range: {num_df[col].min():.1f} - {num_df[col].max():.1f})</span>
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
                                        <span style="color: #e2e8f0;">{col1}</span> & <span style="color: #e2e8f0;">{col2}</span>
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
                            fig_corr.update_layout(height=300, margin=dict(l=0, r=0, t=0, b=0), autosize=True)
                            st.plotly_chart(fig_corr, use_container_width=True, config={'displayModeBar': False})

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
                            fig_dist.update_layout(height=300, margin=dict(l=0, r=0, t=0, b=0), autosize=True)
                            st.plotly_chart(fig_dist, use_container_width=True, config={'displayModeBar': False})
                        
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
                            fig_trend.update_layout(height=250, margin=dict(l=0, r=0, t=0, b=0), autosize=True)
                            st.plotly_chart(fig_trend, use_container_width=True, config={'displayModeBar': False})

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

    # Fallback Check - MUST BE BEFORE COLUMNS to render full width
    if not check_data_loaded():
        st.stop()

    c1, c2 = st.columns([1, 1.5])
    
    with c1:
        @st.fragment
        def render_chat_interface():
            # Init pending query state if needed
            if "pending_query" not in st.session_state:
                st.session_state.pending_query = None

            # 1. PROCESS PENDING INPUT (Main Body - Safe for st.spinner)
            if st.session_state.pending_query:
                user_input = st.session_state.pending_query
                st.session_state.pending_query = None # Consume it
                
                # Add user message
                st.session_state.copilot_history.append({"role": "user", "content": user_input})
                
                # Call Gemini API if within limits
                if "copilot_usage_count" not in st.session_state:
                     st.session_state.copilot_usage_count = 0
                     
                MAX_SESSION_QUERY_LIMIT = 10
                
                if st.session_state.copilot_usage_count >= MAX_SESSION_QUERY_LIMIT:
                    answer = f"🔒 **Session Limit Reached ({MAX_SESSION_QUERY_LIMIT}/{MAX_SESSION_QUERY_LIMIT})**\\n\\nTo ensure availability for all testers, the AI feature is limited per session. Please refresh the page to start a new session."
                else:
                    st.session_state.copilot_usage_count += 1
                    with st.spinner(f"Thinking... (Query {st.session_state.copilot_usage_count}/{MAX_SESSION_QUERY_LIMIT})"):
                        answer = ask_copilot(st.session_state.df, user_input)
                
                # Add assistant message
                st.session_state.copilot_history.append({"role": "assistant", "content": answer})

            # 2. INPUT CALLBACK (Only updates state, no rendering)
            def handle_submit():
                st.session_state.pending_query = st.session_state.copilot_input
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
            st.text_input("Ask about your data...", placeholder="Ask about your data...", key="copilot_input", label_visibility="collapsed", on_change=handle_submit)
            st.markdown("<div style='margin-bottom: 2rem;'></div>", unsafe_allow_html=True)

        # Call the fragment
        render_chat_interface()

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
    if not check_data_loaded():
        pass
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
                        fig.update_xaxes(rangeslider_visible=True)
                        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': True})
                        
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
    if not check_data_loaded():
        pass
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
                     st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': True})
            
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
                            st.plotly_chart(chart_data['fig'], use_container_width=True, config={'displayModeBar': False})
                            if st.button(f"🔍 Enlarge", key=f"btn_{chart_index}"): #Enlarge Button for viewing the chart in Full-View.
                                st.session_state.focused_chart_index = chart_index
                                st.rerun()

# --- FOOTER SPACER ---
st.markdown("<div style='height: 100px;'></div>", unsafe_allow_html=True)
