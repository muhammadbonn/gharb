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
            # Create 4 sub-tabs instead of 3
            tab_data, tab_levels, tab_calc, tab_trend = st.tabs([
                "📊 Data Table & Filters", 
                "🌊 Water Levels Analysis", 
                "🧮 Summary Calculator", 
                "📈 Operating Hours Trend"
            ])
            
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
                
                level_cols = ['suction', 'discharge', 'head']
                available_levels = [col for col in level_cols if col in df_target.columns]
                
                if available_levels:
                    l_col1, l_col2 = st.columns([1, 3])
                    
                    with l_col1:
                        selected_level = st.selectbox("Select Metric", available_levels)
                        chart_mode = st.radio("Chart Mode", ["Year-over-Year (Monthly Averages)", "Continuous Time Trend", "Daily Overlay (Specific Month)"])
                        
                        years = df_target['Date_Index'].dt.year.dropna().unique()
                        
                        if chart_mode == "Year-over-Year (Monthly Averages)":
                            selected_years = st.multiselect("Select Year(s) to Compare", sorted(years), default=sorted(years), key='yoy_lvl_yr')
                            plot_df = df_target[df_target['Date_Index'].dt.year.isin(selected_years)].copy()
                        
                        elif chart_mode == "Continuous Time Trend":
                            selected_years = st.multiselect("Select Year(s)", sorted(years), default=sorted(years), key='cont_lvl_yr')
                            plot_df = df_target[df_target['Date_Index'].dt.year.isin(selected_years)]
                        
                        elif chart_mode == "Daily Overlay (Specific Month)":
                            sel_year = st.selectbox("Select Year for Overlay", sorted(years))
                            months = df_target[df_target['Date_Index'].dt.year == sel_year]['Month_Name'].unique()
                            selected_months = st.multiselect("Select Months to Overlay", months, default=months[:2] if len(months)>1 else months)
                            plot_df = df_target[(df_target['Date_Index'].dt.year == sel_year) & (df_target['Month_Name'].isin(selected_months))]

                    with l_col2:
                        if plot_df.empty:
                            st.warning("No data available for the selected filters.")
                        else:
                            if chart_mode == "Year-over-Year (Monthly Averages)":
                                plot_df['Month_Num'] = plot_df['Date_Index'].dt.month
                                plot_df['Month'] = plot_df['Date_Index'].dt.strftime('%b')
                                plot_df['Year'] = plot_df['Date_Index'].dt.year.astype(str)
                                
                                avg_df = plot_df.groupby(['Year', 'Month_Num', 'Month'])[selected_level].mean().reset_index()
                                avg_df = avg_df.sort_values(['Year', 'Month_Num'])
                                
                                fig = px.line(avg_df, x='Month', y=selected_level, color='Year', markers=True,
                                              title=f"Monthly Average {selected_level.capitalize()} (Year-over-Year)",
                                              labels={'Month': 'Month', selected_level: f'Avg {selected_level.capitalize()}'})
                                st.plotly_chart(fig, use_container_width=True)
                                
                            elif chart_mode == "Continuous Time Trend":
                                fig = px.line(plot_df, x='Date_Index', y=selected_level, title=f"{selected_level.capitalize()} Over Time")
                                plot_df = plot_df.sort_values('Date_Index')
                                plot_df['Monthly Avg'] = plot_df[selected_level].rolling(window=30, min_periods=1).mean()
                                fig.add_trace(go.Scatter(x=plot_df['Date_Index'], y=plot_df['Monthly Avg'], mode='lines', name='30-Day Avg', line=dict(dash='dot', color='red')))
                                st.plotly_chart(fig, use_container_width=True)
                                
                            elif chart_mode == "Daily Overlay (Specific Month)":
                                fig = px.line(plot_df, x='Day_of_Month', y=selected_level, color='Month_Name', markers=True,
                                              title=f"{selected_level.capitalize()} Comparison by Day of Month",
                                              labels={'Day_of_Month': 'Day of the Month'})
                                st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("Level columns (suction, discharge, head) not found in this dataset.")

            # --- TAB 3: SUMMARY CALCULATOR ---
            with tab_calc:
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
                            sel_yrs = st.multiselect("Select Year(s)", sorted(avail_years), default=sorted(avail_years))
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
                    
            # --- TAB 4: OPERATING HOURS TREND ---
            with tab_trend:
                unit_cols = [col for col in df_target.columns if 'unit' in col.lower() or 'total' in col.lower()]
                
                if unit_cols:
                    st.markdown("### 📈 Year-over-Year Trend")
                    h_col1, h_col2 = st.columns([1, 3])
                    
                    with h_col1:
                        selected_unit = st.selectbox("Select Equipment/Unit to Visualize", unit_cols, index=len(unit_cols)-1)
                        years = df_target['Date_Index'].dt.year.dropna().unique()
                        selected_years_hrs = st.multiselect("Select Year(s) to Compare", sorted(years), default=sorted(years), key='yoy_hrs_yr')
                        
                    with h_col2:
                        plot_df_hrs = df_target[df_target['Date_Index'].dt.year.isin(selected_years_hrs)].copy()
                        
                        if plot_df_hrs.empty:
                            st.warning("No data available for the selected years.")
                        else:
                            plot_df_hrs['Month_Num'] = plot_df_hrs['Date_Index'].dt.month
                            plot_df_hrs['Month'] = plot_df_hrs['Date_Index'].dt.strftime('%b')
                            plot_df_hrs['Year'] = plot_df_hrs['Date_Index'].dt.year.astype(str)
                            
                            sum_df = plot_df_hrs.groupby(['Year', 'Month_Num', 'Month'])[selected_unit].sum().reset_index()
                            sum_df = sum_df.sort_values(['Year', 'Month_Num'])
                            
                            fig2 = px.line(sum_df, x='Month', y=selected_unit, color='Year', markers=True,
                                          title=f"Total Monthly Operating Hours for '{selected_unit}' (Year-over-Year)",
                                          labels={'Month': 'Month', selected_unit: 'Total Operating Hours'})
                            
                            fig2.update_traces(line=dict(width=3), marker=dict(size=8))
                            st.plotly_chart(fig2, use_container_width=True)
                else:
                    st.warning("No unit operating hours columns found in this dataset.")
