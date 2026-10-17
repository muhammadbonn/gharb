
import os

import pandas as pd
import streamlit as st


@st.cache_data
def load_master_data():
    """Load equipment master data from an Excel workbook."""
    file_paths = [
        os.path.join("data", "master_data.xlsx"),
        os.path.join("data", "master_data.xls"),
        "master_data.xlsx",
        "master_data.xls",
    ]

    target_path = next(
        (path for path in file_paths if os.path.exists(path)),
        None,
    )

    if target_path is None:
        st.error(
            "Master data file was not found in the data/ folder."
        )
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
    """Load operational transactions from CSV or Excel."""
    file_paths = [
        os.path.join("data", "transactions_data.csv"),
        os.path.join("data", "transactions_data.xls"),
        os.path.join("data", "transactions_data.xlsx"),
        os.path.join("data", "transactions_data_clean.csv"),
        "transactions_data.csv",
        "transactions_data.xls",
        "transactions_data.xlsx",
    ]

    target_path = next(
        (path for path in file_paths if os.path.exists(path)),
        None,
    )

    if target_path is None:
        st.error(
            "Operations data file was not found in the data/ folder."
        )
        return None

    try:
        if target_path.lower().endswith(".csv"):
            df = pd.read_csv(target_path)
        else:
            df = pd.read_excel(target_path)

        # Standardize column names.
        df.columns = (
            df.columns.astype(str).str.strip().str.lower()
        )

        # Validate the required date column.
        if "date" not in df.columns:
            st.error(
                "Operations dataset is missing the required 'date' column."
            )
            return None

        # Parse dates and remove invalid date records.
        df["Date_Index"] = pd.to_datetime(
            df["date"],
            errors="coerce",
            format="mixed",
        )
        df = df.dropna(subset=["Date_Index"]).copy()

        # Create temporal features for dashboard filters.
        df["Day_of_Month"] = df["Date_Index"].dt.day
        df["Month_Name"] = df["Date_Index"].dt.strftime("%b")
        df["Year_Month"] = df["Date_Index"].dt.strftime("%Y-%m")
        df["Year"] = df["Date_Index"].dt.year

        # Convert operational metrics to numeric values.
        numeric_targets = [
            col
            for col in df.columns
            if col.startswith("unit_")
            or col in [
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
            df[col] = pd.to_numeric(
                df[col],
                errors="coerce",
            )

        return df

    except Exception as e:
        st.error(f"Error reading operational dataset: {e}")
        return None


def get_station_unit_columns(df_station):
    """Return active unit-hour columns for the selected station."""
    candidate_units = [
        f"unit_{i}"
        for i in range(1, 7)
        if f"unit_{i}" in df_station.columns
    ]

    active_units = [
        col
        for col in candidate_units
        if df_station[col].notna().any()
        and (df_station[col] > 0).any()
    ]

    return active_units
