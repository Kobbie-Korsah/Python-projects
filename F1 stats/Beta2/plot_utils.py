"""
F1 Dashboard Beta 2 - Plotting Utilities
Generate matplotlib charts for lap times and telemetry
"""
import matplotlib.pyplot as plt
import pandas as pd
from datetime import timedelta

def plot_lap_times(ax, laps, driver_code):
    """
    Plot lap times for a driver
    
    Args:
        ax (matplotlib.axes.Axes): Matplotlib axes object
        laps (pd.DataFrame): Lap data from FastF1
        driver_code (str): Three-letter driver code
    """
    if laps is None or laps.empty:
        ax.text(0.5, 0.5, 'No data available', 
                horizontalalignment='center', verticalalignment='center',
                transform=ax.transAxes, fontsize=14)
        return
    
    # Convert LapTime to seconds for plotting
    # Support both pandas Timedelta and Python timedelta
    if hasattr(laps['LapTime'].dtype, 'unit') or pd.api.types.is_timedelta64_dtype(laps['LapTime']):
        lap_times_sec = laps['LapTime'].dt.total_seconds()
    else:
        lap_times_sec = laps['LapTime'].apply(lambda x: x.total_seconds() if hasattr(x, 'total_seconds') else float(x))

    lap_numbers = laps['LapNumber']
    
    # Plot lap times
    ax.plot(lap_numbers, lap_times_sec, marker='o', linestyle='-', 
            linewidth=2, markersize=4, color='#e10600', label=driver_code)
    
    # Highlight personal best laps
    if 'IsPersonalBest' in laps.columns:
        best_laps = laps[laps['IsPersonalBest'] == True]
        if not best_laps.empty:
            if pd.api.types.is_timedelta64_dtype(best_laps['LapTime']):
                best_times = best_laps['LapTime'].dt.total_seconds()
            else:
                best_times = best_laps['LapTime'].apply(lambda x: x.total_seconds() if hasattr(x, 'total_seconds') else float(x))
            best_numbers = best_laps['LapNumber']
            ax.scatter(best_numbers, best_times, color='gold', s=100, 
                      zorder=5, label='Personal Best', edgecolors='black', linewidths=1.5)
    
    # Formatting
    ax.set_xlabel('Lap Number', fontsize=12, fontweight='bold')
    ax.set_ylabel('Lap Time (seconds)', fontsize=12, fontweight='bold')
    ax.set_title(f'{driver_code} Lap Times', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(loc='upper right')
    
    # Format y-axis to show times nicely (guard against empty series)
    try:
        ax.set_ylim([lap_times_sec.min() - 2, lap_times_sec.max() + 2])
    except Exception:
        pass

def plot_speed_trace(ax, telemetry, driver_code):
    """
    Plot speed trace for a lap
    
    Args:
        ax (matplotlib.axes.Axes): Matplotlib axes object
        telemetry (pd.DataFrame): Telemetry data
        driver_code (str): Driver code
    """
    if telemetry is None or telemetry.empty:
        ax.text(0.5, 0.5, 'No telemetry available', 
                horizontalalignment='center', verticalalignment='center',
                transform=ax.transAxes, fontsize=14)
        return
    
    ax.plot(telemetry['Distance'], telemetry['Speed'], 
            color='#e10600', linewidth=2, label=driver_code)
    
    ax.set_xlabel('Distance (m)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Speed (km/h)', fontsize=12, fontweight='bold')
    ax.set_title(f'{driver_code} Speed Trace', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend()

def plot_throttle_brake(ax, telemetry, driver_code):
    """
    Plot throttle and brake application
    
    Args:
        ax (matplotlib.axes.Axes): Matplotlib axes object
        telemetry (pd.DataFrame): Telemetry data
        driver_code (str): Driver code
    """
    if telemetry is None or telemetry.empty:
        return
    
    ax.plot(telemetry['Distance'], telemetry['Throttle'], 
            color='green', linewidth=1.5, label='Throttle')
    ax.plot(telemetry['Distance'], telemetry['Brake'], 
            color='red', linewidth=1.5, label='Brake')
    
    ax.set_xlabel('Distance (m)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Input (%)', fontsize=12, fontweight='bold')
    ax.set_title(f'{driver_code} Throttle & Brake', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend()
    ax.set_ylim([0, 110])

def plot_tyre_strategy(ax, laps):
    """
    Plot tyre compound strategy
    
    Args:
        ax (matplotlib.axes.Axes): Matplotlib axes object
        laps (pd.DataFrame): Lap data with compound info
    """
    if laps is None or laps.empty or 'Compound' not in laps.columns:
        ax.text(0.5, 0.5, 'No tyre data available', 
                horizontalalignment='center', verticalalignment='center',
                transform=ax.transAxes, fontsize=14)
        return
    
    # Color map for compounds
    compound_colors = {
        'SOFT': '#FF3333',
        'MEDIUM': '#FFF200',
        'HARD': '#EBEBEB',
        'INTERMEDIATE': '#43B02A',
        'WET': '#0067AD'
    }
    
    # Plot each stint with different color
    for stint in laps['Stint'].unique():
        stint_laps = laps[laps['Stint'] == stint]
        compound = stint_laps['Compound'].iloc[0]
        color = compound_colors.get(compound, 'gray')
        
        lap_times_sec = stint_laps['LapTime'].dt.total_seconds()
        
        ax.plot(stint_laps['LapNumber'], lap_times_sec, 
                marker='o', color=color, linewidth=2, 
                markersize=5, label=f'Stint {stint} ({compound})')
    
    ax.set_xlabel('Lap Number', fontsize=12, fontweight='bold')
    ax.set_ylabel('Lap Time (seconds)', fontsize=12, fontweight='bold')
    ax.set_title('Tyre Strategy', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(loc='best')

def plot_comparison(ax, laps1, laps2, driver1, driver2):
    """
    Compare lap times between two drivers
    
    Args:
        ax (matplotlib.axes.Axes): Matplotlib axes object
        laps1 (pd.DataFrame): Laps for driver 1
        laps2 (pd.DataFrame): Laps for driver 2
        driver1 (str): Driver 1 code
        driver2 (str): Driver 2 code
    """
    if laps1 is not None and not laps1.empty:
        lap_times1 = laps1['LapTime'].dt.total_seconds()
        ax.plot(laps1['LapNumber'], lap_times1, 
                marker='o', label=driver1, linewidth=2)
    
    if laps2 is not None and not laps2.empty:
        lap_times2 = laps2['LapTime'].dt.total_seconds()
        ax.plot(laps2['LapNumber'], lap_times2, 
                marker='s', label=driver2, linewidth=2)
    
    ax.set_xlabel('Lap Number', fontsize=12, fontweight='bold')
    ax.set_ylabel('Lap Time (seconds)', fontsize=12, fontweight='bold')
    ax.set_title(f'{driver1} vs {driver2}', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend()