"""
Telemetry processing helpers.
Adds lightweight cleaning plus per-driver metrics for comparison.
"""
from typing import Dict, List, Union, Any

import pandas as pd


def process_telemetry_data(telemetry: Union[pd.DataFrame, Dict[str, List[float]]]) -> Union[pd.DataFrame, Dict[str, List[float]]]:
    """
    Clean and enrich telemetry data.
    
    - Sorts by Distance when available.
    - Drops duplicate Distance samples to avoid zig-zag traces.
    - Adds a BrakePct helper column when Brake exists.
    """
    if isinstance(telemetry, pd.DataFrame):
        if telemetry.empty:
            return telemetry
        
        df = telemetry.copy()
        
        if 'Distance' in df.columns:
            df = df.sort_values('Distance').drop_duplicates(subset='Distance')
        
        if 'Brake' in df.columns and 'BrakePct' not in df.columns:
            df['BrakePct'] = df['Brake'].fillna(0) * 100
        
        return df
    
    # Fallback for legacy dict-based data
    return telemetry


def summarize_telemetry(telemetry: pd.DataFrame) -> Dict[str, Any]:
    """Compute a handful of useful telemetry metrics for one driver."""
    if telemetry is None or telemetry.empty:
        return {
            "avg_speed": 0.0,
            "max_speed": 0.0,
            "throttle_avg": 0.0,
            "brake_usage_pct": 0.0,
            "distance_m": 0.0,
            "lap_duration_s": 0.0,
            "gear_changes": 0,
        }
    
    metrics: Dict[str, Any] = {}
    
    if 'Speed' in telemetry.columns:
        metrics["avg_speed"] = float(telemetry['Speed'].mean())
        metrics["max_speed"] = float(telemetry['Speed'].max())
    else:
        metrics["avg_speed"] = 0.0
        metrics["max_speed"] = 0.0
    
    if 'Throttle' in telemetry.columns:
        metrics["throttle_avg"] = float(telemetry['Throttle'].mean())
    else:
        metrics["throttle_avg"] = 0.0
    
    if 'Brake' in telemetry.columns:
        brake_series = telemetry['Brake'].fillna(0)
        metrics["brake_usage_pct"] = float((brake_series > 0).mean() * 100)
    else:
        metrics["brake_usage_pct"] = 0.0
    
    if 'Distance' in telemetry.columns:
        metrics["distance_m"] = float(telemetry['Distance'].max() - telemetry['Distance'].min())
    else:
        metrics["distance_m"] = 0.0
    
    if 'Time' in telemetry.columns:
        metrics["lap_duration_s"] = float((telemetry['Time'].max() - telemetry['Time'].min()).total_seconds())
    else:
        metrics["lap_duration_s"] = 0.0
    
    if 'nGear' in telemetry.columns:
        gear_changes = telemetry['nGear'].dropna().diff().ne(0).sum()
        metrics["gear_changes"] = int(gear_changes)
    else:
        metrics["gear_changes"] = 0
    
    return metrics


def compare_drivers(telemetry_data: Dict[str, Dict]) -> Dict[str, Dict[str, float]]:
    """
    Produce summary metrics per driver for UI display or debugging.
    
    Args:
        telemetry_data: {driver_code: {"telemetry": pd.DataFrame, ...}}
    
    Returns:
        {driver_code: metrics dict}
    """
    summary: Dict[str, Dict[str, float]] = {}
    for driver, data in telemetry_data.items():
        telemetry_df = data.get("telemetry")
        metrics = summarize_telemetry(telemetry_df if isinstance(telemetry_df, pd.DataFrame) else pd.DataFrame())
        summary[driver] = metrics
    return summary
