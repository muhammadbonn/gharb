import pandas as pd

def get_available_stations(master_data_dict):
    """Extract a unique list of stations across all equipment sheets."""
    stations = set()
    for df in master_data_dict.values():
        if 'station' in df.columns:
            stations.update(df['station'].dropna().unique().tolist())
    return sorted(list(stations))

def filter_master_data(df, station_name):
    """Filter equipment data by the selected station."""
    if 'station' in df.columns:
        return df[df['station'] == station_name]
    return df
