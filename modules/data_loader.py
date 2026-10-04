import pandas as pd
import streamlit as st

@st.cache_data
def load_master_data():
    """Load Master Data from the data folder."""
    file_path = "data/database.xlsx"
    try:
        xls = pd.ExcelFile(file_path)
        db_data = {}
        # Loop through all sheets and skip the translation sheet
        for sheet in xls.sheet_names:
            if sheet.lower() != "translate":
                df = pd.read_excel(xls, sheet_name=sheet)
                db_data[sheet.capitalize()] = df
        return db_data
    except Exception as e:
        st.error(f"Error loading Master Data: {e}")
        return {}

@st.cache_data
def load_operations_data():
    """Load Operations Data for specific stations."""
    file_path = "data/data.xls"
    try:
        xls = pd.ExcelFile(file_path)
        df_11 = pd.read_excel(xls, sheet_name="drainag_11")
        df_gharb = pd.read_excel(xls, sheet_name="gharb_elburullus_new")
        
        # Convert Arabic date column to a standard datetime format for filtering
        if 'التاريخ' in df_11.columns:
            df_11['Date'] = pd.to_datetime(df_11['التاريخ'], errors='coerce')
        if 'التاريخ' in df_gharb.columns:
            df_gharb['Date'] = pd.to_datetime(df_gharb['التاريخ'], errors='coerce')
            
        return {"Station 11": df_11, "Gharb El Burullus": df_gharb}
    except Exception as e:
        st.error(f"Error loading Operations Data: {e}")
        return {}
