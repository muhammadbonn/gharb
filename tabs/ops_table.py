import streamlit as st
import pandas as pd


def render_ops_table(df_station):
  """Renders raw operational data table with dynamic time filtration options.

  Displays filtered data by day, month, year, or custom date range.
  """
  st.subheader("Filter Raw Data")

  # Time filtration mode selection
  filter_type = st.radio(
      "Time Filter:",
      ["All", "Daily", "Monthly", "Yearly", "Custom Period"],
      horizontal=True,
  )

  # Determine dataset date boundaries
  min_date = df_station["Date_Index"].min().date()
  max_date = df_station["Date_Index"].max().date()
  filtered_df = df_station.copy()

  col1, col2 = st.columns(2)

  # Apply filtration based on user selection
  if filter_type == "Daily":
    sel_date = col1.date_input(
        "Select Date", value=min_date, min_value=min_date, max_value=max_date
    )
    filtered_df = df_station[df_station["Date_Index"].dt.date == sel_date]

  elif filter_type == "Monthly":
    available_years = sorted(df_station["Date_Index"].dt.year.dropna().unique())
    sel_yr = col1.selectbox("Year", available_years)
    sel_mo = col2.selectbox("Month", range(1, 13))
    filtered_df = df_station[
        (df_station["Date_Index"].dt.year == sel_yr)
        & (df_station["Date_Index"].dt.month == sel_mo)
    ]

  elif filter_type == "Yearly":
    available_years = sorted(df_station["Date_Index"].dt.year.dropna().unique())
    sel_yr = col1.selectbox("Year", available_years)
    filtered_df = df_station[df_station["Date_Index"].dt.year == sel_yr]

  elif filter_type == "Custom Period":
    date_range = col1.date_input(
        "Select Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )
    if isinstance(date_range, tuple) and len(date_range) == 2:
      filtered_df = df_station[
          (df_station["Date_Index"].dt.date >= date_range[0])
          & (df_station["Date_Index"].dt.date <= date_range[1])
      ]

  # Display filtered count indicator
  st.caption(f"Showing **{len(filtered_df)}** records")

  # Drop internal processing/helper columns before displaying table
  cols_to_drop = [
      "Date_Index",
      "Day_of_Month",
      "Month_Name",
      "Year_Month",
      "Year",
  ]
  display_df = filtered_df.drop(columns=cols_to_drop, errors="ignore")

  # Render interactive dataframe
  st.dataframe(display_df, use_container_width=True)
