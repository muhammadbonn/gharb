import pandas as pd
import streamlit as st

@st.cache_data
def load_master_data():
    """Load Master Data from the data folder."""
    file_path = "data/database.xlsx"
    try:
        xls = pd.ExcelFile(file_path)
        db_data = {}
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
        
        # Check for English 'date' or Arabic 'التاريخ' dynamically
        for df in [df_11, df_gharb]:
            if 'date' in df.columns:
                df['Date_Index'] = pd.to_datetime(df['date'], errors='coerce')
            elif 'التاريخ' in df.columns:
                df['Date_Index'] = pd.to_datetime(df['التاريخ'], errors='coerce')
            
            # Extract day and month for easy overlapping in graphs
            if 'Date_Index' in df.columns:
                df['Day_of_Month'] = df['Date_Index'].dt.day
                df['Month_Name'] = df['Date_Index'].dt.strftime('%B')
                df['Year_Month'] = df['Date_Index'].dt.to_period('M').astype(str)

        return {"Station 11": df_11, "Gharb El Burullus": df_gharb}
    except Exception as e:
        st.error(f"Error loading Operations Data: {e}")
        return {}
