import streamlit as st
import pandas as pd
import plotly.express as px
from modules.data_loader import get_station_unit_columns

def render_ops_trend(df_station):
    """
    Renders Year-over-Year operating hours trend analysis.
    """
    st.markdown("### 📈 Operating Hours Trend")
    
    valid_units = get_station_unit_columns(df_station)
    total_col = 'total_hr' if 'total_hr' in df_station.columns else ('total' if 'total' in df_station.columns else None)
    
    selectable_cols = valid_units + ([total_col] if total_col else [])
    
    if selectable_cols:
        h_col1, h_col2 = st.columns([1, 3])
        
        with h_col1:
            selected_metric = st.selectbox("Select Unit / Total to Visualize", selectable_cols)
            years = sorted(df_station['Date_Index'].dt.year.dropna().unique())
            max_year = int(max(years)) if years else 2026
            selected_years = st.multiselect("Select Year(s) to Compare", years, default=[max_year], key='yoy_hrs_yr')
            
        with h_col2:
            plot_df = df_station[df_station['Date_Index'].dt.year.isin(selected_years)].copy()
            
            if plot_df.empty or plot_df[selected_metric].dropna().empty:
                st.warning("No data recorded for the selected year(s).")
            else:
                plot_df['Month_Num'] = plot_df['Date_Index'].dt.month
                plot_df['Month'] = plot_df['Date_Index'].dt.strftime('%b')
                plot_df['Year'] = plot_df['Date_Index'].dt.year.astype(str)
                
                sum_df = plot_df.groupby(['Year', 'Month_Num', 'Month'])[selected_metric].sum().reset_index()
                sum_df = sum_df.sort_values(['Year', 'Month_Num'])
                
                clean_name = selected_metric.replace('_', ' ').title()
                fig = px.line(sum_df, x='Month', y=selected_metric, color='Year', markers=True,
                              title=f"Total Monthly Operating Hours for '{clean_name}'",
                              labels={'Month': 'Month', selected_metric: 'Operating Hours'})
                
                fig.update_traces(line=dict(width=3), marker=dict(size=8))
                st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No unit operating hours data found for this station.")
