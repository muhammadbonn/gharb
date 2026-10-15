import streamlit as st
import pandas as pd
import plotly.express as px

def render_ops_trend(df_target):
    unit_cols = [col for col in df_target.columns if 'unit' in col.lower() or 'total' in col.lower()]
    
    if unit_cols:
        st.markdown("### 📈 Year-over-Year Trend")
        h_col1, h_col2 = st.columns([1, 3])
        
        with h_col1:
            selected_unit = st.selectbox("Select Equipment/Unit to Visualize", unit_cols, index=len(unit_cols)-1)
            years = df_target['Date_Index'].dt.year.dropna().unique()
            selected_years_hrs = st.multiselect("Select Year(s) to Compare", sorted(years), default=[int(max(years))], key='yoy_hrs_yr')
            
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
