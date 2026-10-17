import os
import pandas as pd
import streamlit as st

@st.cache_data
def load_operations_data():
    """
    Loads consolidated operational transactions data from data/ folder.
    Handles dates, station filtering, and temporal features.
    """
    possible_paths = [
        os.path.join("data", "transactions_data.xlsx"),
        os.path.join("data", "transactions_data.xls"),
        os.path.join("data", "transactions_data_clean.csv"),
        os.path.join("data", "transactions_data.csv"),
        "transactions_data.xlsx",
        "transactions_data.xls"
    ]
    
    file_path = None
    for p in possible_paths:
        if os.path.exists(p):
            file_path = p
            break
            
    if not file_path:
        st.error("Operations dataset not found in data/ folder.")
        return None
        
    try:
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)
            
        # Clean column headers
        df.columns = df.columns.astype(str).str.strip().str.lower()
        
        # Parse datetime
        df['Date_Index'] = pd.to_datetime(df['date'], errors='coerce')
        df = df.dropna(subset=['Date_Index']).copy()
        
        # Extract temporal features for filtering and grouping
        df['Day_of_Month'] = df['Date_Index'].dt.day
        df['Month_Name'] = df['Date_Index'].dt.strftime('%b')
        df['Year_Month'] = df['Date_Index'].dt.strftime('%Y-%m')
        df['Year'] = df['Date_Index'].dt.year
        
        # Ensure numerical casting for unit operating hours, levels, and energy
        numeric_cols = [c for c in df.columns if c.startswith('unit_') or c in [
            'total_hr', 'suction_8am', 'avg_suction', 'avg_delivery', 'avg_head', 'energy_consumed', 'energy'
        ]]
        
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
                
        return df
        
    except Exception as e:
        st.error(f"Error loading operational data: {e}")
        return None

def get_station_unit_columns(df_station):
    """
    Returns only valid unit columns (e.g. unit_1..unit_6) that contain data for the selected station.
    """
    unit_cols = [f'unit_{i}' for i in range(1, 7) if f'unit_{i}' in df_station.columns]
    # Keep columns that are not entirely NaN for this specific station
    valid_units = [col for col in unit_cols if df_station[col].notna().any() and (df_station[col] > 0).any()]
    return valid_units
