import os
import pandas as pd
import streamlit as st


@st.cache_data
def load_master_data():
  """Loads equipment master data sheets from data/master_data.xlsx.

  Returns a dictionary where keys are sheet names (equipment types)
  and values are DataFrames containing specifications.
  """

file_paths = [
    os.path.join("data", "transactions_data.csv"),
    os.path.join("data", "transactions_data.xls"),
    os.path.join("data", "transactions_data.xlsx"),
    os.path.join("data", "transactions_data_clean.csv"),
    "transactions_data.csv",
    "transactions_data.xls",
    "transactions_data.xlsx",
]


  target_path = next((p for p in file_paths if os.path.exists(p)), None)

  if not target_path:
    st.error(
      "Operations data file 'transactions_data.csv' "
      "or Excel equivalent not found in data/ folder.")
  return None

  try:
    xls = pd.ExcelFile(target_path)
    master_dict = {}

    for sheet_name in xls.sheet_names:
      df = pd.read_excel(xls, sheet_name=sheet_name)
      df.columns = df.columns.astype(str).str.strip()
      master_dict[sheet_name] = df

    return master_dict

  except Exception as e:
    st.error(f"Error loading master data file: {e}")
    return None


@st.cache_data
def load_operations_data():
  """Loads consolidated operational transactions data from data/transactions_data.xls.

  Parses dates, handles station filtering, and computes temporal features.
  """
  file_paths = [
      os.path.join("data", "transactions_data.xls"),
      os.path.join("data", "transactions_data.xlsx"),
      os.path.join("data", "transactions_data_clean.csv"),
      "transactions_data.xls",
      "transactions_data.xlsx",
  ]

  target_path = next((p for p in file_paths if os.path.exists(p)), None)

  if not target_path:
    st.error(
        "Operations data file 'transactions_data.xls' not found in data/"
        " folder."
    )
    return None

  try:
    if target_path.endswith(".csv"):
      df = pd.read_csv(target_path)
    else:
      df = pd.read_excel(target_path)

    # Standardize column header names
    df.columns = df.columns.astype(str).str.strip().str.lower()

    # Convert date column to datetime
    df["Date_Index"] = pd.to_datetime(
        df["date"], errors="coerce", format="mixed"
    )
    df = df.dropna(subset=["Date_Index"]).copy()

    # Temporal feature extraction for dashboard filters & groupings
    df["Day_of_Month"] = df["Date_Index"].dt.day
    df["Month_Name"] = df["Date_Index"].dt.strftime("%b")
    df["Year_Month"] = df["Date_Index"].dt.strftime("%Y-%m")
    df["Year"] = df["Date_Index"].dt.year

    # Ensure numeric casting for operational metrics
    numeric_targets = [
        col
        for col in df.columns
        if col.startswith("unit_")
        or col
        in [
            "total_hr",
            "suction_8am",
            "avg_suction",
            "avg_delivery",
            "avg_head",
            "energy_consumed",
            "energy",
        ]
    ]

    for col in numeric_targets:
      if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    return df

  except Exception as e:
    st.error(f"Error reading operational dataset: {e}")
    return None


def get_station_unit_columns(df_station):
  """Filters and returns unit operating hour columns that contain valid, non-null data for the active station."""
  candidate_units = [
      f"unit_{i}" for i in range(1, 7) if f"unit_{i}" in df_station.columns
  ]

  # Retain units with at least one non-null and non-zero record
  active_units = [
      col
      for col in candidate_units
      if df_station[col].notna().any() and (df_station[col] > 0).any()
  ]
  return active_units
