"""
F1 Dashboard Beta 3 - Advanced Plotting Utilities
Create telemetry and comparison charts
"""
import matplotlib.pyplot as plt
import numpy as np

# Driver team colors (approximate)
DRIVER_COLORS = {
    'VER': '#1E41FF', 'PER': '#1E41FF',  # Red Bull
    'HAM': '#00D2BE', 'RUS': '#00D2BE',  # Mercedes
    'LEC': '#DC0000', 'SAI': '#DC0000',  # Ferrari
    'NOR': '#FF8700', 'PIA': '#FF8700',  # McLaren
    'ALO': '#006F62', 'STR': '#006F62',  # Aston Martin
    'GAS': '#0090FF', 'OCO': '#0090FF',  # Alpine
    'TSU': '#2B4562', 'RIC': '#2B4562',  # AlphaTauri/RB
    'BOT': '#900000', 'ZHO': '#900000',  # Alfa Romeo
    'HUL': '#FFFFFF', 'MAG': '#FFFFFF',  # Haas
    'ALB': '#005AFF', 'SAR': '#005AFF'   # Williams
}

def plot_speed_trace(ax, telemetry, driver_code):
    """
    Plot speed trace over distance
    
    Args:
        ax: Matplotlib axes
        telemetry (pd.DataFrame): Telemetry data
        driver_code (str): Driver code
    """
    if telemetry.empty:
        ax.text(0.5, 0.5, 'No telemetry data', 
                ha='center', va='center', transform=ax.transAxes)
        return
    
    color = DRIVER_COLORS.get(driver_code, '#e10600')
    
    ax.plot(telemetry['Distance'], telemetry['Speed'], 
            color=color, linewidth=2, label=driver_code)
    
    ax.set_xlabel('Distance (m)', fontsize=11, fontweight='bold')
    ax.set_ylabel('Speed (km/h)', fontsize=11, fontweight='bold')
    ax.set_title(f'{driver_code} - Speed Trace', fontsize=13, fontweight='bold')
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.legend(loc='best')

def plot_throttle_brake_gear(ax, telemetry, driver_code):
    """
    Plot throttle, brake, and gear over distance
    
    Args:
        ax: Matplotlib axes
        telemetry (pd.DataFrame): Telemetry data
        driver_code (str): Driver code
    """
    if telemetry.empty:
        ax.text(0.5, 0.5, 'No telemetry data', 
                ha='center', va='center', transform=ax.transAxes)
        return
    
    # Create secondary y-axis for gear
    ax2 = ax.twinx()
    
    # Plot throttle and brake
    ax.plot(telemetry['Distance'], telemetry['Throttle'], 
            color='green', linewidth=1.5, label='Throttle', alpha=0.8)
    ax.plot(telemetry['Distance'], telemetry['Brake'] * 100,  # Scale brake to %
            color='red', linewidth=1.5, label='Brake', alpha=0.8)
    
    # Plot gear on secondary axis
    if 'nGear' in telemetry.columns:
        ax2.plot(telemetry['Distance'], telemetry['nGear'], 
                color='yellow', linewidth=2, label='Gear', alpha=0.6)
        ax2.set_ylabel('Gear', fontsize=11, fontweight='bold', color='yellow')
        ax2.tick_params(axis='y', labelcolor='yellow')
        ax2.set_ylim([0, 9])
    
    ax.set_xlabel('Distance (m)', fontsize=11, fontweight='bold')
    ax.set_ylabel('Input (%)', fontsize=11, fontweight='bold')
    ax.set_title(f'{driver_code} - Throttle, Brake & Gear', fontsize=13, fontweight='bold')
    ax.set_ylim([0, 110])
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.legend(loc='upper left')

def plot_lap_comparison(ax, laps_dict):
    """
    Compare lap times across multiple drivers
    
    Args:
        ax: Matplotlib axes
        laps_dict (dict): {driver_code: laps_df}
    """
    if not laps_dict:
        ax.text(0.5, 0.5, 'No lap data', 
                ha='center', va='center', transform=ax.transAxes)
        return
    
    for driver, laps in laps_dict.items():
        if laps.empty:
            continue
        
        color = DRIVER_COLORS.get(driver, '#e10600')
        lap_times_sec = laps['LapTime'].dt.total_seconds()
        
        ax.plot(laps['LapNumber'], lap_times_sec, 
                marker='o', label=driver, color=color, 
                linewidth=2, markersize=5, alpha=0.8)
    
    ax.set_xlabel('Lap Number', fontsize=11, fontweight='bold')
    ax.set_ylabel('Lap Time (seconds)', fontsize=11, fontweight='bold')
    ax.set_title('Lap Time Comparison', fontsize=13, fontweight='bold')
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.legend(loc='best')

def plot_telemetry_comparison(ax, telemetry_dict, metric, title):
    """
    Compare a specific telemetry metric across drivers
    
    Args:
        ax: Matplotlib axes
        telemetry_dict (dict): {driver_code: {'telemetry': df, 'laps': df}}
        metric (str): Metric to compare ('Speed', 'Throttle', 'Brake', etc.)
        title (str): Chart title
    """
    if not telemetry_dict:
        ax.text(0.5, 0.5, 'No telemetry data', 
                ha='center', va='center', transform=ax.transAxes)
        return
    
    for driver, data in telemetry_dict.items():
        telemetry = data['telemetry']
        
        if telemetry.empty or metric not in telemetry.columns:
            continue
        
        color = DRIVER_COLORS.get(driver, '#e10600')
        
        ax.plot(telemetry['Distance'], telemetry[metric], 
                label=driver, color=color, linewidth=2, alpha=0.8)
    
    ax.set_xlabel('Distance (m)', fontsize=11, fontweight='bold')
    ax.set_ylabel(metric, fontsize=11, fontweight='bold')
    ax.set_title(title, fontsize=13, fontweight='bold')
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.legend(loc='best')

def plot_delta_time(ax, telemetry1, telemetry2, driver1, driver2):
    """
    Plot time delta between two drivers
    
    Args:
        ax: Matplotlib axes
        telemetry1 (pd.DataFrame): First driver telemetry
        telemetry2 (pd.DataFrame): Second driver telemetry
        driver1 (str): First driver code
        driver2 (str): Second driver code
    """
    if telemetry1.empty or telemetry2.empty:
        ax.text(0.5, 0.5, 'Insufficient data for delta', 
                ha='center', va='center', transform=ax.transAxes)
        return
    
    # Calculate delta (simplified - assumes similar distances)
    min_len = min(len(telemetry1), len(telemetry2))
    
    distances = telemetry1['Distance'].iloc[:min_len]
    time_delta = (telemetry1['Time'].iloc[:min_len].reset_index(drop=True) - 
                  telemetry2['Time'].iloc[:min_len].reset_index(drop=True)).dt.total_seconds()
    
    # Plot delta
    ax.plot(distances, time_delta, color='purple', linewidth=2)
    ax.axhline(y=0, color='white', linestyle='--', alpha=0.5)
    
    # Fill areas
    ax.fill_between(distances, time_delta, 0, 
                     where=(time_delta > 0), color='green', alpha=0.3, 
                     label=f'{driver1} ahead')
    ax.fill_between(distances, time_delta, 0, 
                     where=(time_delta < 0), color='red', alpha=0.3, 
                     label=f'{driver2} ahead')
    
    ax.set_xlabel('Distance (m)', fontsize=11, fontweight='bold')
    ax.set_ylabel('Delta (seconds)', fontsize=11, fontweight='bold')
    ax.set_title(f'Time Delta: {driver1} vs {driver2}', fontsize=13, fontweight='bold')
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.legend(loc='best')

def plot_tyre_strategy(ax, laps):
    """
    Visualize tyre strategy
    
    Args:
        ax: Matplotlib axes
        laps (pd.DataFrame): Lap data with compound info
    """
    if laps.empty or 'Compound' not in laps.columns:
        ax.text(0.5, 0.5, 'No tyre data', 
                ha='center', va='center', transform=ax.transAxes)
        return
    
    compound_colors = {
        'SOFT': '#FF3333',
        'MEDIUM': '#FFF200',
        'HARD': '#EBEBEB',
        'INTERMEDIATE': '#43B02A',
        'WET': '#0067AD'
    }
    
    for stint in laps['Stint'].unique():
        stint_laps = laps[laps['Stint'] == stint]
        compound = stint_laps['Compound'].iloc[0]
        color = compound_colors.get(compound, 'gray')
        
        lap_times_sec = stint_laps['LapTime'].dt.total_seconds()
        
        ax.plot(stint_laps['LapNumber'], lap_times_sec, 
                marker='o', color=color, linewidth=2, markersize=5,
                label=f'Stint {stint} ({compound})')
    
    ax.set_xlabel('Lap Number', fontsize=11, fontweight='bold')
    ax.set_ylabel('Lap Time (seconds)', fontsize=11, fontweight='bold')
    ax.set_title('Tyre Strategy', fontsize=13, fontweight='bold')
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.legend(loc='best')

def plot_cornering_analysis(ax, telemetry, driver_code):
    """
    Analyze cornering behavior
    
    Args:
        ax: Matplotlib axes
        telemetry (pd.DataFrame): Telemetry data
        driver_code (str): Driver code
    """
    if telemetry.empty:
        ax.text(0.5, 0.5, 'No telemetry data', 
                ha='center', va='center', transform=ax.transAxes)
        return
    
    # Find low-speed sections (corners)
    corners = telemetry[telemetry['Speed'] < 150]
    
    if corners.empty:
        ax.text(0.5, 0.5, 'No corner data detected', 
                ha='center', va='center', transform=ax.transAxes)
        return
    
    # Plot speed through corners
    color = DRIVER_COLORS.get(driver_code, '#e10600')
    ax.scatter(corners['Distance'], corners['Speed'], 
               c=color, s=20, alpha=0.6, label=driver_code)
    
    ax.set_xlabel('Distance (m)', fontsize=11, fontweight='bold')
    ax.set_ylabel('Corner Speed (km/h)', fontsize=11, fontweight='bold')
    ax.set_title(f'{driver_code} - Corner Analysis', fontsize=13, fontweight='bold')
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.legend(loc='best')