import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def render_ops_levels(df_station):
    """
    Renders interactive charts for suction, delivery, and head water levels.
    """
    st.subheader("Water Levels Analysis")
    
    # Map possible level column names in dataset
    level_mapping = {
        'avg_suction': 'Average Suction Level',
        'avg_delivery': 'Average Delivery Level',
        'avg_head': 'Average Head Level',
        'suction_8am': 'Suction Level (8 AM)',
        'suction': 'Suction Level',
        'discharge': 'Discharge Level',
        'head': 'Head Level'
    }
    
    available_levels = [col for col in level_mapping.keys() if col in df_station.columns and df_station[col].notna().any()]
    
    if available_levels:
        l_col1, l_col2 = st.columns([1, 3])
        with l_col1:
            selected_col = st.selectbox("Select Level Metric", available_levels, format_func=lambda c: level_mapping.get(c, c))
            chart_mode = st.radio("Chart Mode", ["Year-over-Year (Monthly Averages)", "Continuous Time Trend", "Daily Overlay (Specific Month)"])
            
            years = sorted(df_station['Date_Index'].dt.year.dropna().unique())
            max_year = int(max(years)) if years else 2026
            
            if chart_mode == "Year-over-Year (Monthly Averages)":
                selected_years = st.multiselect("Select Year(s) to Compare", years, default=[max_year], key='yoy_lvl_yr')
                plot_df = df_station[df_station['Date_Index'].dt.year.isin(selected_years)].copy()
            
            elif chart_mode == "Continuous Time Trend":
                min_year = int(min(years)) if years else 2009
                if min_year == max_year:
                    sel_range = (min_year, max_year)
                    st.info(f"Data available for year {min_year}")
                else:
                    sel_range = st.slider("Select Year Range", min_value=min_year, max_value=max_year, value=(min_year, max_year), key='cont_lvl_yr')
                plot_df = df_station[(df_station['Date_Index'].dt.year >= sel_range[0]) & (df_station['Date_Index'].dt.year <= sel_range[1])]
            
            elif chart_mode == "Daily Overlay (Specific Month)":
                sel_year = st.selectbox("Select Year for Overlay", years)
                months = df_station[df_station['Date_Index'].dt.year == sel_year]['Month_Name'].unique()
                selected_months = st.multiselect("Select Months to Overlay", months, default=months[:2] if len(months)>1 else months)
                plot_df = df_station[(df_station['Date_Index'].dt.year == sel_year) & (df_station['Month_Name'].isin(selected_months))]

        with l_col2:
            if plot_df.empty or plot_df[selected_col].dropna().empty:
                st.warning("No water level data recorded for the selected parameters.")
            else:
                metric_label = level_mapping.get(selected_col, selected_col)
                
                if chart_mode == "Year-over-Year (Monthly Averages)":
                    plot_df['Month_Num'] = plot_df['Date_Index'].dt.month
                    plot_df['Month'] = plot_df['Date_Index'].dt.strftime('%b')
                    plot_df['Year'] = plot_df['Date_Index'].dt.year.astype(str)
                    
                    avg_df = plot_df.groupby(['Year', 'Month_Num', 'Month'])[selected_col].mean().reset_index()
                    avg_df = avg_df.sort_values(['Year', 'Month_Num'])
                    
                    fig = px.line(avg_df, x='Month', y=selected_col, color='Year', markers=True,
                                  title=f"Monthly {metric_label} (Year-over-Year Comparison)",
                                  labels={'Month': 'Month', selected_col: f'Avg {metric_label}'})
                    st.plotly_chart(fig, use_container_width=True)
                    
                elif chart_mode == "Continuous Time Trend":
                    fig = px.line(plot_df, x='Date_Index', y=selected_col, title=f"{metric_label} Over Time")
                    plot_df = plot_df.sort_values('Date_Index')
                    plot_df['Monthly Avg'] = plot_df[selected_col].rolling(window=30, min_periods=1).mean()
                    fig.add_trace(go.Scatter(x=plot_df['Date_Index'], y=plot_df['Monthly Avg'], mode='lines', name='30-Day Moving Avg', line=dict(dash='dot', color='red')))
                    st.plotly_chart(fig, use_container_width=True)
                    
                elif chart_mode == "Daily Overlay (Specific Month)":
                    fig = px.line(plot_df, x='Day_of_Month', y=selected_col, color='Month_Name', markers=True,
                                  title=f"{metric_label} Comparison by Day of Month",
                                  labels={'Day_of_Month': 'Day of the Month', selected_col: metric_label})
                    st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No water level columns found in the dataset for this station.")
