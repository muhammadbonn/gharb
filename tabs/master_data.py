import streamlit as st
import pandas as pd
from modules.data_loader import load_master_data
from modules.filters import get_available_stations, filter_master_data

def render_master_data():
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
            
            display_mode = st.radio("Display Mode", ["Table View", "Card View"], horizontal=True)
            
            if display_mode == "Table View":
                st.dataframe(filtered_df, use_container_width=True)
            else:
                for idx, row in filtered_df.iterrows():
                    with st.container(border=True):
                        st.markdown(f"#### ⚙️ {selected_component} Details")
                        cols = st.columns(4)
                        col_idx = 0
                        
                        for col_name, value in row.items():
                            if pd.isna(value) or str(value).strip() == "":
                                continue
                            
                            clean_name = str(col_name).replace('_', ' ').title()
                            
                            # Custom HTML/CSS to prevent text truncation and style the labels
                            custom_card_html = f"""
                            <div style="margin-bottom: 16px;">
                                <div style="color: #64B5F6; font-size: 0.9em; font-weight: bold; margin-bottom: 4px;">
                                    {clean_name}
                                </div>
                                <div style="font-size: 1.1em; word-wrap: break-word; white-space: normal; line-height: 1.4;">
                                    {str(value)}
                                </div>
                            </div>
                            """
                            
                            # Render the custom HTML inside the column
                            cols[col_idx % 4].markdown(custom_card_html, unsafe_allow_html=True)
                            col_idx += 1
        else:
            st.info(f"No {selected_component} records found for {selected_station}.")
