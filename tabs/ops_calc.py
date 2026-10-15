import streamlit as st
import pandas as pd

def render_ops_calc(df_target):
    unit_cols = [col for col in df_target.columns if 'unit' in col.lower() or 'total' in col.lower()]
    
    if unit_cols:
        st.markdown("### 🧮 Summary Calculator")
        st.markdown("Calculate Total or Average operating hours for specific units over any period.")
        
        calc_col1, calc_col2, calc_col3 = st.columns(3)
        with calc_col1:
            calc_units = st.multiselect("Select Unit(s) for Calculation", unit_cols, default=[unit_cols[-1]])
            calc_type = st.radio("Calculation Type", ["Total (Sum)", "Average (Mean)"])
            
        with calc_col2:
            period_type = st.radio("Select Period Type", ["All Time", "Specific Year(s)", "Specific Month/Year", "Custom Date Range"])
            
        with calc_col3:
            calc_df = df_target.copy()
            min_dt = calc_df['Date_Index'].min().date()
            max_dt = calc_df['Date_Index'].max().date()
            
            if period_type == "Specific Year(s)":
                avail_years = calc_df['Date_Index'].dt.year.dropna().unique()
                sel_yrs = st.multiselect("Select Year(s)", sorted(avail_years), default=[max(avail_years)])
                calc_df = calc_df[calc_df['Date_Index'].dt.year.isin(sel_yrs)]
            elif period_type == "Specific Month/Year":
                avail_years = calc_df['Date_Index'].dt.year.dropna().unique()
                sel_yr = st.selectbox("Select Year", sorted(avail_years), key='calc_yr')
                sel_mo = st.selectbox("Select Month", range(1, 13), key='calc_mo')
                calc_df = calc_df[(calc_df['Date_Index'].dt.year == sel_yr) & (calc_df['Date_Index'].dt.month == sel_mo)]
            elif period_type == "Custom Date Range":
                d_range = st.date_input("Select Date Range", value=(min_dt, max_dt), min_value=min_dt, max_value=max_dt)
                if isinstance(d_range, tuple) and len(d_range) == 2:
                    calc_df = calc_df[(calc_df['Date_Index'].dt.date >= d_range[0]) & (calc_df['Date_Index'].dt.date <= d_range[1])]
        
        if not calc_df.empty and calc_units:
            if calc_type == "Total (Sum)":
                result_df = calc_df[calc_units].sum().to_frame(name="Total Operating Hours").T
            else:
                result_df = calc_df[calc_units].mean().round(2).to_frame(name="Average Daily Hours").T
            
            st.success(f"Calculation Result ({period_type}):")
            st.dataframe(result_df, use_container_width=True)
        else:
            st.info("Please select at least one unit and a valid date range to see the summary.")
    else:
        st.warning("No unit operating hours columns found in this dataset.")
