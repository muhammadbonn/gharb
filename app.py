import streamlit as st
import pandas as pd
from modules.data_loader import load_master_data, load_operations_data
from modules.filters import get_available_stations, filter_master_data

# Page configuration
st.set_page_config(page_title="Pumping Stations Dashboard", layout="wide")
st.title("Pumping Stations Management Dashboard")
st.markdown("---")

# Sidebar navigation
st.sidebar.header("Navigation")
data_category = st.sidebar.radio("Select Data Category", ["Master Data", "Operations Data"])

# ----------------- MASTER DATA MODULE ----------------- #
if data_category == "Master Data":
    st.header("Master Data Viewer")
    st.markdown("View technical specifications for equipment across different stations.")
    
    master_data = load_master_data()
    
    if master_data:
        # Get dynamic stations and let user select
        all_stations = get_available_stations(master_data)
        selected_station = st.selectbox("Select Station", all_stations)
        
        # Component Selection (Pumps, Motors, etc.)
        components = list(master_data.keys())
        selected_component = st.selectbox("Select Equipment Component", components)
        
        # Display data
        df_selected = master_data[selected_component]
        filtered_df = filter_master_data(df_selected, selected_station)
        
        if not filtered_df.empty:
            st.success(f"Showing {selected_component} records for {selected_station}")
        else:
            st.info(f"No {selected_component} records found for {selected_station}.")
            
        st.dataframe(filtered_df, use_container_width=True)

# ----------------- OPERATIONS DATA MODULE ----------------- #
elif data_category == "Operations Data":
    st.header("Operations Data Viewer")
    st.markdown("View historical transactional data for operational stations.")
    
    operations_data = load_operations_data()
    
    if operations_data:
        target_station = st.selectbox("Select Station", ["Station 11", "Gharb El Burullus"])
        df_target = operations_data[target_station]
        
        if 'Date' in df_target.columns and not df_target['Date'].dropna().empty:
            st.subheader(f"Data Filter for {target_station}")
            
            filter_type = st.radio("Select Time Filter", ["Daily", "Monthly", "Yearly", "Custom Period"], horizontal=True)
            
            min_date = df_target['Date'].min().date()
            max_date = df_target['Date'].max().date()
            filtered_df = pd.DataFrame()
            
            # Apply Filter Logic
            if filter_type == "Daily":
                selected_date = st.date_input("Select Date", min_value=min_date, max_value=max_date, value=min_date)
                filtered_df = df_target[df_target['Date'].dt.date == selected_date]
                
            elif filter_type == "Monthly":
                col1, col2 = st.columns(2)
                with col1:
                    yr = st.selectbox("Select Year", sorted(df_target['Date'].dt.year.dropna().unique()))
                with col2:
                    mo = st.selectbox("Select Month", range(1, 13))
                filtered_df = df_target[(df_target['Date'].dt.year == yr) & (df_target['Date'].dt.month == mo)]
                
            elif filter_type == "Yearly":
                yr = st.selectbox("Select Year", sorted(df_target['Date'].dt.year.dropna().unique()))
                filtered_df = df_target[df_target['Date'].dt.year == yr]
                
            elif filter_type == "Custom Period":
                date_range = st.date_input("Select Date Range", value=(min_date, max_date), min_value=min_date, max_value=max_date)
                if isinstance(date_range, tuple) and len(date_range) == 2:
                    start, end = date_range
                    filtered_df = df_target[(df_target['Date'].dt.date >= start) & (df_target['Date'].dt.date <= end)]
                else:
                    filtered_df = df_target
                    
            # Drop the datetime helper column before displaying
            st.dataframe(filtered_df.drop(columns=['Date']), use_container_width=True)
        else:
            st.warning("No valid date format found to apply time filters.")
            st.dataframe(df_target, use_container_width=True)
