import streamlit as st
from modules.data_loader import load_operations_data
from tabs.master_data import render_master_data
from tabs.ops_table import render_ops_table
from tabs.ops_levels import render_ops_levels
from tabs.ops_calc import render_ops_calc
from tabs.ops_trend import render_ops_trend

st.set_page_config(page_title="Asset Management for Gharb El Burullus", layout="wide")
st.title("Asset Management for Gharb El Burullus")
st.markdown("---")

st.sidebar.header("Navigation")
data_category = st.sidebar.radio("Select Data Category", ["Master Data", "Operations Data"])

if data_category == "Master Data":
    render_master_data()

elif data_category == "Operations Data":
    st.header("Operations Dashboard")
    operations_data = load_operations_data()
    
    if operations_data:
        target_station = st.selectbox("Select Station", ["Station 11", "Gharb El Burullus"])
        df_target = operations_data[target_station]
        
        if 'Date_Index' not in df_target.columns or df_target['Date_Index'].dropna().empty:
            st.warning("No valid date format found in the dataset.")
            st.dataframe(df_target)
        else:
            # Render the 4 sub-tabs
            tab_data, tab_levels, tab_calc, tab_trend = st.tabs([
                "📊 Data Table & Filters", 
                "🌊 Water Levels Analysis", 
                "🧮 Summary Calculator", 
                "📈 Operating Hours Trend"
            ])
            
            with tab_data:
                render_ops_table(df_target)
            with tab_levels:
                render_ops_levels(df_target)
            with tab_calc:
                render_ops_calc(df_target)
            with tab_trend:
                render_ops_trend(df_target)
