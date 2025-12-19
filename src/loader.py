import pandas as pd
import streamlit as st

@st.cache_data
def load_data(file) -> pd.DataFrame:
    """
    Loads data from a CSV or Excel file into a Pandas DataFrame.
    """
    try:
        if file.name.endswith('.csv'):
            df = pd.read_csv(file)
        elif file.name.endswith('.xlsx'):
            df = pd.read_excel(file)
        else:
            return None
        
        # Simple preprocessing: drop empty rows
        df = df.dropna(how='all')
        return df
    except Exception as e:
        st.error(f"Error loading file: {e}")
        return None
