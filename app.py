import streamlit as st
from modules.data_loader import load_operations_data
from tabs.master_data import render_master_data
from tabs.ops_table import render_ops_table
from tabs.ops_levels import render_ops_levels
from tabs.ops_calc import render_ops_calc
from tabs.ops_trend import render_ops_trend

# Page configuration
st.set_page_config(page_title="Asset Management for Gharb El Burullus Stations", layout="wide")
st.title("Asset Management for Gharb El Burullus Stations")
st.markdown("---")

st.sidebar.header("Navigation")
data_category = st.sidebar.radio("Select Data Category", ["Master Data", "Operations Data"], index=1)

# --- MASTER DATA TAB ---
if data_category == "Master Data":
    render_master_data()

# --- OPERATIONS DATA TAB ---
elif data_category == "Operations Data":
    st.header("Operations Dashboard")
    df_ops = load_operations_data()
    
    if df_ops is not None and not df_ops.empty:
        # Dynamically list all available stations from dataset
        available_stations = sorted(df_ops['station'].unique().tolist())
        selected_station = st.selectbox("Select Station", available_stations)
        
        # Filter dataframe for the selected station
        df_station = df_ops[df_ops['station'] == selected_station].copy()
        
        if df_station.empty:
            st.warning(f"No records found for station: {selected_station}")
        else:
            # Render sub-tabs
            tab_data, tab_levels, tab_calc, tab_trend = st.tabs([
                "📊 Data Table & Filters", 
                "🌊 Water Levels Analysis", 
                "🧮 Summary Calculator", 
                "📈 Operating Hours Trend"
            ])
            
            with tab_data:
                render_ops_table(df_station)
            with tab_levels:
                render_ops_levels(df_station)
            with tab_calc:
                render_ops_calc(df_station)
            with tab_trend:
                render_ops_trend(df_station)
    else:
        st.error("Operations dataset could not be loaded or is empty.")
