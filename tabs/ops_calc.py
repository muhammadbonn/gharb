import streamlit as st
import pandas as pd
from modules.data_loader import get_station_unit_columns

def render_ops_calc(df_station):
    """
    Renders Summary Calculator for unit operating hours and energy consumption.
    """
    st.markdown("### 🧮 Summary Calculator")
    
    # Get station-specific unit columns
    valid_units = get_station_unit_columns(df_station)
    
    # Check for total hours and energy columns
    extra_cols = []
    if 'total_hr' in df_station.columns:
        extra_cols.append('total_hr')
    elif 'total' in df_station.columns:
        extra_cols.append('total')
        
    energy_col = next((c for c in ['energy_consumed', 'energy'] if c in df_station.columns), None)
    if energy_col:
        extra_cols.append(energy_col)
        
    selectable_cols = valid_units + extra_cols
    
    if selectable_cols:
        calc_col1, calc_col2, calc_col3 = st.columns(3)
        
        with calc_col1:
            calc_metrics = st.multiselect("Select Metric(s) for Calculation", selectable_cols, default=valid_units[:2] if len(valid_units)>=2 else selectable_cols)
            calc_type = st.radio("Calculation Type", ["Total (Sum)", "Average (Mean)"])
            
        with calc_col2:
            period_type = st.radio("Select Period Type", ["All Time", "Specific Year(s)", "Specific Month/Year", "Custom Date Range"])
            
        with calc_col3:
            calc_df = df_station.copy()
            min_dt = calc_df['Date_Index'].min().date()
            max_dt = calc_df['Date_Index'].max().date()
            avail_years = sorted(calc_df['Date_Index'].dt.year.dropna().unique())
            
            if period_type == "Specific Year(s)" and avail_years:
                sel_yrs = st.multiselect("Select Year(s)", avail_years, default=[max(avail_years)])
                calc_df = calc_df[calc_df['Date_Index'].dt.year.isin(sel_yrs)]
            elif period_type == "Specific Month/Year" and avail_years:
                sel_yr = st.selectbox("Select Year", avail_years, key='calc_yr')
                sel_mo = st.selectbox("Select Month", range(1, 13), key='calc_mo')
                calc_df = calc_df[(calc_df['Date_Index'].dt.year == sel_yr) & (calc_df['Date_Index'].dt.month == sel_mo)]
            elif period_type == "Custom Date Range":
                d_range = st.date_input("Select Date Range", value=(min_dt, max_dt), min_value=min_dt, max_value=max_dt)
                if isinstance(d_range, tuple) and len(d_range) == 2:
                    calc_df = calc_df[(calc_df['Date_Index'].dt.date >= d_range[0]) & (calc_df['Date_Index'].dt.date <= d_range[1])]
        
        if not calc_df.empty and calc_metrics:
            if calc_type == "Total (Sum)":
                result = calc_df[calc_metrics].sum(numeric_only=True).to_frame(name="Total Sum").T
            else:
                result = calc_df[calc_metrics].mean(numeric_only=True).round(2).to_frame(name="Daily Average").T
            
            st.success(f"Calculation Results ({period_type}):")
            st.dataframe(result, use_container_width=True)
        else:
            st.info("Please select at least one valid metric and period.")
    else:
        st.warning("No operational metrics available for calculation.")
