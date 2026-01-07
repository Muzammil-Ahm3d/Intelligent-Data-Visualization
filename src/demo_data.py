import pandas as pd
import os
import streamlit as st

def load_demo_data():
    """
    Loads the pre-existing demo dataset from data/Global_Weather_Analytics_500.xlsx
    """
    # Define path relative to the app root
    # Assuming app.py is in root, data is in root/data
    file_path = os.path.join(os.getcwd(), 'data', 'Global_Weather_Analytics_500.xlsx')
    
    if not os.path.exists(file_path):
        st.error(f"Demo data file not found at: {file_path}")
        return None
        
    try:
        # Load Excel file
        df = pd.read_excel(file_path)
        return df
    except Exception as e:
        st.error(f"Error loading demo data: {str(e)}")
        return None
