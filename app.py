import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from modules.data_loader import load_master_data, load_operations_data
from modules.filters import get_available_stations, filter_master_data

st.set_page_config(page_title="Pumping Stations Dashboard", layout="wide")
st.title("Pumping Stations Management Dashboard")
st.markdown("---")

st.sidebar.header("Navigation")
data_category = st.sidebar.radio("Select Data Category", ["Master Data", "Operations Data"])

# ----------------- MASTER DATA MODULE ----------------- #
if data_category == "Master Data":
    st.header("Master Data Viewer")
    master_data = load_master_data()
    
    if master_data:
        all_stations = get_available_stations(master_data)
        selected_station = st.selectbox("Select Station", all_stations)
        components = list(master_data.keys())
        selected_component = st.selectbox("Select Equipment Component", components)
        
        df_selected = master_data[selected_component]
        filtered_df = filter_master_data(df_selected, selected_station)
        
        if not filtered_df.empty:
            st.success(f"Showing {selected_component} records for {selected_station}")
        else:
            st.info(f"No {selected_component} records found for {selected_station}.")
            
        st.dataframe(filtered_df, use_container_width=True)

# ----------------- OPERATIONS DATA MODULE ----------------- #
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
            # Create sub-tabs for organizing the dashboard
            tab_data, tab_levels, tab_hours = st.tabs(["📊 Data Table & Filters", "🌊 Water Levels Analysis", "⚙️ Operating Hours Analysis"])
            
            # --- TAB 1: DATA TABLE & DATE FILTRATION ---
            with tab_data:
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

            # --- TAB 2: WATER LEVELS ANALYSIS ---
            with tab_levels:
                st.subheader("Water Levels Visualization (Suction, Discharge, Head)")
                
                # Dynamic layout for level charts
                level_cols = ['suction', 'discharge', 'head']
                available_levels = [col for col in level_cols if col in df_target.columns]
                
                if available_levels:
                    l_col1, l_col2 = st.columns([1, 3])
                    
                    with l_col1:
                        selected_level = st.selectbox("Select Metric", available_levels)
                        chart_mode = st.radio("Chart Mode", ["Continuous Time Trend", "Month-over-Month Overlay"])
                        
                        if chart_mode == "Continuous Time Trend":
                            years = df_target['Date_Index'].dt.year.dropna().unique()
                            selected_years = st.multiselect("Select Year(s)", sorted(years), default=sorted(years))
                            plot_df = df_target[df_target['Date_Index'].dt.year.isin(selected_years)]
                        
                        elif chart_mode == "Month-over-Month Overlay":
                            years = df_target['Date_Index'].dt.year.dropna().unique()
                            sel_year = st.selectbox("Select Year for Overlay", sorted(years))
                            months = df_target[df_target['Date_Index'].dt.year == sel_year]['Month_Name'].unique()
                            selected_months = st.multiselect("Select Months to Overlay", months, default=months[:2] if len(months)>1 else months)
                            plot_df = df_target[(df_target['Date_Index'].dt.year == sel_year) & (df_target['Month_Name'].isin(selected_months))]

                    with l_col2:
                        if plot_df.empty:
                            st.warning("No data available for the selected filters.")
                        else:
                            if chart_mode == "Continuous Time Trend":
                                fig = px.line(plot_df, x='Date_Index', y=selected_level, title=f"{selected_level.capitalize()} Over Time")
                                # Add rolling average line
                                plot_df = plot_df.sort_values('Date_Index')
                                plot_df['Monthly Avg'] = plot_df[selected_level].rolling(window=30, min_periods=1).mean()
                                fig.add_trace(go.Scatter(x=plot_df['Date_Index'], y=plot_df['Monthly Avg'], mode='lines', name='30-Day Avg', line=dict(dash='dot', color='red')))
                                st.plotly_chart(fig, use_container_width=True)
                                
                            elif chart_mode == "Month-over-Month Overlay":
                                fig = px.line(plot_df, x='Day_of_Month', y=selected_level, color='Month_Name', markers=True,
                                              title=f"{selected_level.capitalize()} Comparison by Day of Month",
                                              labels={'Day_of_Month': 'Day of the Month', selected_level: selected_level.capitalize()})
                                st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("Level columns (suction, discharge, head) not found in this dataset.")

            # --- TAB 3: OPERATING HOURS ANALYSIS ---
            with tab_hours:
                st.subheader("Pump Units Operating Hours")
                
                unit_cols = [col for col in df_target.columns if 'unit' in col.lower() or 'total' in col.lower()]
                
                if unit_cols:
                    h_col1, h_col2 = st.columns([1, 3])
                    
                    with h_col1:
                        selected_units = st.multiselect("Select Units to Compare", unit_cols, default=[unit_cols[-1]] if unit_cols else [])
                        agg_type = st.radio("Aggregation Level", ["Daily (Specific Month)", "Monthly (Yearly Summary)"])
                        
                        if agg_type == "Daily (Specific Month)":
                            y_sel = st.selectbox("Select Year", sorted(df_target['Date_Index'].dt.year.dropna().unique()), key='h_yr')
                            m_sel = st.selectbox("Select Month", range(1, 13), key='h_mo')
                            hours_df = df_target[(df_target['Date_Index'].dt.year == y_sel) & (df_target['Date_Index'].dt.month == m_sel)]
                            x_axis = 'Date_Index'
                        else:
                            y_sel = st.selectbox("Select Year", sorted(df_target['Date_Index'].dt.year.dropna().unique()), key='h_yr_all')
                            base_df = df_target[df_target['Date_Index'].dt.year == y_sel]
                            hours_df = base_df.groupby('Year_Month')[selected_units].sum().reset_index()
                            x_axis = 'Year_Month'

                    with h_col2:
                        if hours_df.empty or not selected_units:
                            st.warning("Select units and valid dates to view operating hours.")
                        else:
                            # Melt dataframe for multi-unit comparison grouped bar chart
                            melted_df = hours_df.melt(id_vars=[x_axis], value_vars=selected_units, var_name='Unit', value_name='Hours')
                            fig2 = px.bar(melted_df, x=x_axis, y='Hours', color='Unit', barmode='group',
                                          title=f"Operating Hours Comparison - {agg_type}")
                            st.plotly_chart(fig2, use_container_width=True)
                else:
                    st.warning("No unit operating hours columns found in this dataset.")
