import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def render_ops_levels(df_target):
    st.subheader("Water Levels Visualization (Suction, Discharge, Head)")
    level_cols = ['suction', 'discharge', 'head']
    available_levels = [col for col in level_cols if col in df_target.columns]
    
    if available_levels:
        l_col1, l_col2 = st.columns([1, 3])
        with l_col1:
            selected_level = st.selectbox("Select Metric", available_levels)
            chart_mode = st.radio("Chart Mode", ["Year-over-Year (Monthly Averages)", "Continuous Time Trend", "Daily Overlay (Specific Month)"])
            
            years = df_target['Date_Index'].dt.year.dropna().unique()
            max_year = int(max(years))
            
            if chart_mode == "Year-over-Year (Monthly Averages)":
                selected_years = st.multiselect("Select Year(s) to Compare", sorted(years), default=[max_year], key='yoy_lvl_yr')
                plot_df = df_target[df_target['Date_Index'].dt.year.isin(selected_years)].copy()
            
            elif chart_mode == "Continuous Time Trend":
                min_year = int(min(years))
                if min_year == max_year:
                    sel_range = (min_year, max_year)
                    st.info(f"Data available only for year {min_year}")
                else:
                    sel_range = st.slider("Select Year Range", min_value=min_year, max_value=max_year, value=(min_year, max_year), key='cont_lvl_yr')
                plot_df = df_target[(df_target['Date_Index'].dt.year >= sel_range[0]) & (df_target['Date_Index'].dt.year <= sel_range[1])]
            
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
