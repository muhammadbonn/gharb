import streamlit as st
import pandas as pd

def render_ops_table(df_target):
    st.subheader("Filter Raw Data")
    filter_type = st.radio("Time Filter:", ["All", "Daily", "Monthly", "Yearly", "Custom Period"], horizontal=True)
    
    min_date = df_target['Date_Index'].min().date()
    max_date = df_target['Date_Index'].max().date()
    filtered_df = df_target.copy()
    
    col1, col2 = st.columns(2)
    if filter_type == "Daily":
        sel_date = col1.date_input("Select Date", value=min_date, min_value=min_date, max_value=max_date)
        filtered_df = df_target[df_target['Date_Index'].dt.date == sel_date]
    elif filter_type == "Monthly":
        yr = col1.selectbox("Year", sorted(df_target['Date_Index'].dt.year.dropna().unique()))
        mo = col2.selectbox("Month", range(1, 13))
        filtered_df = df_target[(df_target['Date_Index'].dt.year == yr) & (df_target['Date_Index'].dt.month == mo)]
    elif filter_type == "Yearly":
        yr = col1.selectbox("Year", sorted(df_target['Date_Index'].dt.year.dropna().unique()))
        filtered_df = df_target[df_target['Date_Index'].dt.year == yr]
    elif filter_type == "Custom Period":
        date_range = col1.date_input("Date Range", value=(min_date, max_date), min_value=min_date, max_value=max_date)
        if isinstance(date_range, tuple) and len(date_range) == 2:
            filtered_df = df_target[(df_target['Date_Index'].dt.date >= date_range[0]) & (df_target['Date_Index'].dt.date <= date_range[1])]
    
    st.dataframe(filtered_df.drop(columns=['Date_Index', 'Day_of_Month', 'Month_Name', 'Year_Month'], errors='ignore'), use_container_width=True)
