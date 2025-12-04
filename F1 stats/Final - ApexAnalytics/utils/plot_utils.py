"""
F1 Analytics Suite - Plotting Utilities
Professional matplotlib charts with F1 styling
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import pandas as pd
import numpy as np
from typing import List, Dict, Optional
from core.enums import DRIVER_COLORS, TEAM_COLORS
from utils.ui_helpers import get_tyre_compound_color
from typing import Callable

# F1 Style settings
plt.style.use('dark_background')
F1_RED = '#E10600'
BACKGROUND_COLOR = '#1E1E1E'
GRID_COLOR = '#3A3A3A'

def setup_f1_style(ax):
    """Apply F1 styling to matplotlib axis"""
    ax.set_facecolor(BACKGROUND_COLOR)
    ax.grid(True, alpha=0.2, color=GRID_COLOR, linestyle='--')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color(GRID_COLOR)
    ax.spines['bottom'].set_color(GRID_COLOR)
    ax.tick_params(colors='white')

def plot_season_progression(ax, seasons: List[Dict], driver_code: str):
    """
    Plot driver's points progression over seasons
    
    Args:
        ax: Matplotlib axis
        seasons: List of season data
        driver_code: Driver code
    """
    if not seasons:
        ax.text(0.5, 0.5, 'No season data available', 
                ha='center', va='center', transform=ax.transAxes,
                fontsize=14, color='white')
        return
    
    years = [s['year'] for s in seasons]
    points = []
    
    for season in seasons:
        season_points = sum(float(r.get('points', 0)) for r in season.get('results', []))
        points.append(season_points)
    
    color = DRIVER_COLORS.get(driver_code, F1_RED)
    
    ax.plot(years, points, marker='o', linewidth=3, markersize=8, 
            color=color, label=driver_code)
    ax.fill_between(years, points, alpha=0.2, color=color)
    
    ax.set_xlabel('Season', fontsize=12, fontweight='bold', color='white')
    ax.set_ylabel('Points', fontsize=12, fontweight='bold', color='white')
    ax.set_title(f'{driver_code} - Season Points Progression', 
                 fontsize=16, fontweight='bold', color=F1_RED)
    
    setup_f1_style(ax)
    ax.legend(fontsize=10, framealpha=0.8)

def plot_qualifying_vs_race(ax, seasons: List[Dict], driver_code: str):
    """
    Plot average qualifying position vs race finish position
    
    Args:
        ax: Matplotlib axis
        seasons: List of season data
        driver_code: Driver code
    """
    if not seasons:
        ax.text(0.5, 0.5, 'No season data available', 
                ha='center', va='center', transform=ax.transAxes,
                fontsize=14, color='white')
        return
    
    years = []
    quali_positions = []
    race_positions = []
    
    for season in seasons:
        results = season.get('results', [])
        if not results:
            continue
        
        # Calculate averages
        quali_avg = np.mean([float(r.get('grid', 20)) for r in results if r.get('grid')])
        race_avg = np.mean([float(r.get('position', 20)) for r in results if r.get('position')])
        
        years.append(season['year'])
        quali_positions.append(quali_avg)
        race_positions.append(race_avg)
    
    if not years:
        return
    
    color = DRIVER_COLORS.get(driver_code, F1_RED)
    
    ax.plot(years, quali_positions, marker='s', label='Avg Qualifying', 
            linewidth=2, markersize=6, color=color, linestyle='--')
    ax.plot(years, race_positions, marker='o', label='Avg Race Finish', 
            linewidth=2, markersize=6, color=color)
    
    ax.set_xlabel('Season', fontsize=12, fontweight='bold', color='white')
    ax.set_ylabel('Position', fontsize=12, fontweight='bold', color='white')
    ax.set_title(f'{driver_code} - Qualifying vs Race Performance', 
                 fontsize=16, fontweight='bold', color=F1_RED)
    ax.invert_yaxis()  # Lower position number is better
    
    setup_f1_style(ax)
    ax.legend(fontsize=10, framealpha=0.8)

def plot_speed_trace(ax, telemetry: pd.DataFrame, driver_code: str):
    """
    Plot speed vs distance telemetry
    
    Args:
        ax: Matplotlib axis
        telemetry: Telemetry dataframe
        driver_code: Driver code
    """
    if telemetry.empty or 'Speed' not in telemetry.columns:
        ax.text(0.5, 0.5, 'No telemetry data', 
                ha='center', va='center', transform=ax.transAxes,
                fontsize=14, color='white')
        return
    
    color = DRIVER_COLORS.get(driver_code, F1_RED)
    
    ax.plot(telemetry['Distance'], telemetry['Speed'], 
            linewidth=2, color=color, label=driver_code)
    
    ax.set_xlabel('Distance (m)', fontsize=12, fontweight='bold', color='white')
    ax.set_ylabel('Speed (km/h)', fontsize=12, fontweight='bold', color='white')
    ax.set_title(f'{driver_code} - Speed Trace', 
                 fontsize=16, fontweight='bold', color=F1_RED)
    
    setup_f1_style(ax)
    ax.legend(fontsize=10, framealpha=0.8)

def plot_throttle_brake_gear(ax, telemetry: pd.DataFrame, driver_code: str):
    """
    Plot throttle, brake, and gear traces
    
    Args:
        ax: Matplotlib axis
        telemetry: Telemetry dataframe
        driver_code: Driver code
    """
    if telemetry.empty:
        ax.text(0.5, 0.5, 'No telemetry data', 
                ha='center', va='center', transform=ax.transAxes,
                fontsize=14, color='white')
        return
    
    # Create twin axis for gear
    ax2 = ax.twinx()
    
    # Plot throttle and brake
    if 'Throttle' in telemetry.columns:
        ax.plot(telemetry['Distance'], telemetry['Throttle'], 
                color='#00FF00', linewidth=1.5, label='Throttle', alpha=0.8)
    
    if 'Brake' in telemetry.columns:
        ax.plot(telemetry['Distance'], telemetry['Brake'] * 100, 
                color='#FF0000', linewidth=1.5, label='Brake', alpha=0.8)
    
    # Plot gear on secondary axis
    if 'nGear' in telemetry.columns:
        ax2.plot(telemetry['Distance'], telemetry['nGear'], 
                color='#FFFF00', linewidth=2, label='Gear', alpha=0.6)
        ax2.set_ylabel('Gear', fontsize=11, fontweight='bold', color='#FFFF00')
        ax2.tick_params(axis='y', labelcolor='#FFFF00')
        ax2.set_ylim([0, 9])
        ax2.spines['right'].set_color('#FFFF00')
    
    ax.set_xlabel('Distance (m)', fontsize=12, fontweight='bold', color='white')
    ax.set_ylabel('Input (%)', fontsize=12, fontweight='bold', color='white')
    ax.set_title(f'{driver_code} - Throttle, Brake & Gear', 
                 fontsize=16, fontweight='bold', color=F1_RED)
    ax.set_ylim([0, 110])
    
    setup_f1_style(ax)
    ax.legend(loc='upper left', fontsize=10, framealpha=0.8)

def plot_tyre_strategy(ax, strategy: List[Dict], driver_code: str):
    """
    Visualize tyre strategy with stint bars
    
    Args:
        ax: Matplotlib axis
        strategy: List of stint dictionaries
        driver_code: Driver code
    """
    if not strategy:
        ax.text(0.5, 0.5, 'No tyre strategy data', 
                ha='center', va='center', transform=ax.transAxes,
                fontsize=14, color='white')
        return
    
    y_pos = 0.5
    
    for stint in strategy:
        compound = stint['compound']
        start = stint['start_lap']
        end = stint['end_lap']
        duration = end - start + 1
        
        color = get_tyre_compound_color(compound)
        
        # Draw stint bar
        rect = patches.Rectangle((start, y_pos - 0.3), duration, 0.6,
                                 linewidth=2, edgecolor='white',
                                 facecolor=color, alpha=0.8)
        ax.add_patch(rect)
        
        # Add label
        ax.text(start + duration/2, y_pos, f"{compound}\n({duration} laps)",
               ha='center', va='center', fontsize=9, fontweight='bold',
               color='black' if compound == 'MEDIUM' or compound == 'HARD' else 'white')
    
    ax.set_xlim([0, max(s['end_lap'] for s in strategy) + 5])
    ax.set_ylim([0, 1])
    ax.set_xlabel('Lap Number', fontsize=12, fontweight='bold', color='white')
    ax.set_title(f'{driver_code} - Tyre Strategy', 
                 fontsize=14, fontweight='bold', color=F1_RED)
    ax.set_yticks([])
    
    setup_f1_style(ax)

def plot_lap_comparison(ax, laps_dict: Dict[str, pd.DataFrame]):
    """
    Compare lap times across multiple drivers
    
    Args:
        ax: Matplotlib axis
        laps_dict: Dictionary of {driver_code: laps_dataframe}
    """
    if not laps_dict:
        ax.text(0.5, 0.5, 'No lap data', 
                ha='center', va='center', transform=ax.transAxes,
                fontsize=14, color='white')
        return
    
    for driver, laps in laps_dict.items():
        if laps.empty or 'LapTime' not in laps.columns:
            continue
        
        lap_times = laps['LapTime'].dt.total_seconds()
        lap_numbers = laps['LapNumber']
        
        color = DRIVER_COLORS.get(driver, F1_RED)
        
        ax.plot(lap_numbers, lap_times, marker='o', label=driver, 
                color=color, linewidth=2, markersize=5, alpha=0.8)
    
    ax.set_xlabel('Lap Number', fontsize=12, fontweight='bold', color='white')
    ax.set_ylabel('Lap Time (seconds)', fontsize=12, fontweight='bold', color='white')
    ax.set_title('Lap Time Comparison', fontsize=14, fontweight='bold', color=F1_RED)
    
    setup_f1_style(ax)
    ax.legend(fontsize=10, framealpha=0.8)

def plot_telemetry_comparison(ax, telemetry_dict: Dict, metric: str, title: str):
    """
    Compare specific telemetry metric across drivers
    
    Args:
        ax: Matplotlib axis
        telemetry_dict: Dictionary of driver telemetry
        metric: Metric to compare ('Speed', 'Throttle', etc.)
        title: Chart title
    """
    if not telemetry_dict:
        ax.text(0.5, 0.5, 'No telemetry data', 
                ha='center', va='center', transform=ax.transAxes,
                fontsize=14, color='white')
        return
    
    for driver, data in telemetry_dict.items():
        telemetry = data.get('telemetry', pd.DataFrame())
        
        if telemetry.empty or metric not in telemetry.columns:
            continue
        
        color = DRIVER_COLORS.get(driver, F1_RED)
        
        ax.plot(telemetry['Distance'], telemetry[metric], 
                label=driver, color=color, linewidth=2, alpha=0.8)
    
    ax.set_xlabel('Distance (m)', fontsize=12, fontweight='bold', color='white')
    ax.set_ylabel(metric, fontsize=12, fontweight='bold', color='white')
    ax.set_title(title, fontsize=14, fontweight='bold', color=F1_RED)
    
    setup_f1_style(ax)
    ax.legend(fontsize=10, framealpha=0.8)

def plot_pace_consistency(ax, laps: pd.DataFrame, driver_code: str):
    """
    Plot lap time distribution histogram
    
    Args:
        ax: Matplotlib axis
        laps: Lap dataframe
        driver_code: Driver code
    """
    if laps.empty or 'LapTime' not in laps.columns:
        ax.text(0.5, 0.5, 'No lap data', 
                ha='center', va='center', transform=ax.transAxes,
                fontsize=14, color='white')
        return
    
    lap_times = laps['LapTime'].dt.total_seconds().dropna()
    
    if lap_times.empty:
        return
    
    color = DRIVER_COLORS.get(driver_code, F1_RED)
    
    ax.hist(lap_times, bins=15, color=color, alpha=0.7, edgecolor='white')
    
    # Add mean line
    mean_time = lap_times.mean()
    ax.axvline(mean_time, color=F1_RED, linestyle='--', linewidth=2, 
               label=f'Mean: {mean_time:.2f}s')
    
    ax.set_xlabel('Lap Time (seconds)', fontsize=12, fontweight='bold', color='white')
    ax.set_ylabel('Frequency', fontsize=12, fontweight='bold', color='white')
    ax.set_title(f'{driver_code} - Pace Consistency', 
                 fontsize=14, fontweight='bold', color=F1_RED)
    
    setup_f1_style(ax)
    ax.legend(fontsize=10, framealpha=0.8)

def plot_position_changes(ax, position_data: pd.DataFrame, driver_code: str):
    """
    Plot position changes throughout race
    
    Args:
        ax: Matplotlib axis
        position_data: Position by lap dataframe
        driver_code: Driver code
    """
    if position_data.empty:
        ax.text(0.5, 0.5, 'No position data', 
                ha='center', va='center', transform=ax.transAxes,
                fontsize=14, color='white')
        return
    
    color = DRIVER_COLORS.get(driver_code, F1_RED)
    
    ax.plot(position_data['LapNumber'], position_data['Position'], 
            marker='o', linewidth=3, markersize=6, color=color, label=driver_code)
    
    ax.set_xlabel('Lap Number', fontsize=12, fontweight='bold', color='white')
    ax.set_ylabel('Position', fontsize=12, fontweight='bold', color='white')
    ax.set_title(f'{driver_code} - Position Changes', 
                 fontsize=14, fontweight='bold', color=F1_RED)
    ax.invert_yaxis()  # Lower position is better
    ax.set_yticks(range(1, 21))
    
    setup_f1_style(ax)
    ax.legend(fontsize=10, framealpha=0.8)

def plot_feature_importance(ax, feature_names: List[str], importances: np.ndarray):
    """
    Plot ML model feature importance
    
    Args:
        ax: Matplotlib axis
        feature_names: List of feature names
        importances: Array of importance scores
    """
    # Sort by importance
    indices = np.argsort(importances)[::-1][:10]  # Top 10
    
    ax.barh(range(len(indices)), importances[indices], color=F1_RED, alpha=0.8)
    ax.set_yticks(range(len(indices)))
    ax.set_yticklabels([feature_names[i] for i in indices])
    
    ax.set_xlabel('Importance', fontsize=12, fontweight='bold', color='white')
    ax.set_title('Feature Importance', fontsize=14, fontweight='bold', color=F1_RED)
    
    setup_f1_style(ax)

def add_hover_tooltips(ax, xfmt: Callable[[float], str] | None = None,
                       yfmt: Callable[[float], str] | None = None):
    """
    Attach lightweight hover tooltips to matplotlib artists on an axis.
    Silently no-ops if mplcursors is not installed.
    """
    try:
        import mplcursors
    except Exception:
        return

    artists = list(ax.lines) + list(ax.containers)
    if not artists:
        return

    xfmt = xfmt or (lambda v: f"{v:.1f}")
    yfmt = yfmt or (lambda v: f"{v:.1f}")

    cursor = mplcursors.cursor(artists, hover=True)

    @cursor.connect("add")
    def on_add(sel):
        artist = sel.artist
        label = artist.get_label() if hasattr(artist, "get_label") else ""
        if label and label.startswith("_"):
            label = ""

        # Bar container
        if hasattr(artist, "__iter__") and not hasattr(artist, "get_xdata"):
            patch = artist[sel.index]
            x = patch.get_x() + patch.get_width() / 2
            y = patch.get_height()
        else:
            x, y = sel.target

        parts = []
        if label:
            parts.append(label)
        parts.append(f"x: {xfmt(x)}")
        parts.append(f"y: {yfmt(y)}")
        sel.annotation.set_text("\n".join(parts))
        sel.annotation.get_bbox_patch().set(fc="#2A2A2A", ec="#E10600", alpha=0.9)
