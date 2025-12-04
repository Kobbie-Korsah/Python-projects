"""
F1 Analytics Suite - UI Helper Functions
Utilities for loading images, formatting data, and creating widgets
"""

from PyQt6.QtWidgets import QLabel, QFrame
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import Qt
from pathlib import Path
from difflib import SequenceMatcher
import unicodedata
import os

def _normalize_name(val: str) -> str:
    """Normalize names for loose filename matching."""
    normalized = unicodedata.normalize("NFKD", val)
    return "".join(ch.lower() for ch in normalized if ch.isalnum())


def load_driver_photo(driver_code: str, size: tuple = (150, 150)) -> QPixmap:
    """
    Load driver photo from assets folder
    
    Args:
        driver_code: Three-letter driver code (e.g., 'VER', 'HAM')
        size: Desired size (width, height)
    
    Returns:
        QPixmap: Loaded and scaled photo, or placeholder if not found
    """
    base_dir = Path(__file__).resolve().parent.parent / "assets" / "logos" / "drivers"
    driver_code = driver_code.upper()
    name_map = {
        "VER": "Max Verstappen",
        "PER": "Sergio Perez",
        "HAM": "Lewis Hamilton",
        "RUS": "George Russell",
        "LEC": "Charles Leclerc",
        "SAI": "Carlos Sainz",
        "NOR": "Lando Norris",
        "PIA": "Oscar Piastri",
        "ALO": "Fernando Alonso",
        "STR": "Lance Stroll",
        "GAS": "Pierre Gasly",
        "OCO": "Esteban Ocon",
        "RIC": "Daniel Ricciardo",
        "TSU": "Yuki Tsunoda",
        "BOT": "Valtteri Bottas",
        "ZHO": "Zhou Guanyu",
        "HUL": "Nico H\u00fclkenberg",
        "MAG": "Kevin Magnussen",
        "ALB": "Alexander Albon",
        "SAR": "Logan Sargeant",
    }

    candidates = []
    full_name = name_map.get(driver_code)
    if full_name:
        candidates.extend([
            full_name,
            full_name.replace(" ", "_"),
            full_name.replace(" ", ""),
            full_name.replace(" ", "-"),
            full_name.replace(" ", "_").replace("-", "_"),
            full_name.replace(" ", "-").replace("_", "-"),
        ])
    # Some assets use dashed names like Max-Verstappen.png
    if full_name:
        parts = full_name.split()
        if len(parts) >= 2:
            candidates.append(f"{parts[0]}-{parts[1]}")
    candidates.extend([driver_code, driver_code.lower()])

    exts = ["png", "jpg", "jpeg"]
    for candidate in candidates:
        for ext in exts:
            photo_path = base_dir / f"{candidate}.{ext}"
            if photo_path.exists():
                pixmap = QPixmap(str(photo_path))
                if not pixmap.isNull():
                    return pixmap.scaled(
                        size[0],
                        size[1],
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation,
                    )

    # Fallback: scan directory for a close match by normalized name
    target_norm = _normalize_name(full_name or driver_code)
    if base_dir.exists():
        best_match = None
        best_score = 0.0
        for file in base_dir.iterdir():
            if file.is_file() and file.suffix.lower().lstrip(".") in exts:
                stem_norm = _normalize_name(file.stem.replace("logo", ""))
                if target_norm and (target_norm in stem_norm or stem_norm in target_norm):
                    pixmap = QPixmap(str(file))
                    if not pixmap.isNull():
                        return pixmap.scaled(
                            size[0],
                            size[1],
                            Qt.AspectRatioMode.KeepAspectRatio,
                            Qt.TransformationMode.SmoothTransformation,
                        )
                score = SequenceMatcher(None, target_norm, stem_norm).ratio()
                if score > best_score:
                    best_score = score
                    best_match = file
        if best_match and best_score >= 0.6:
            pixmap = QPixmap(str(best_match))
            if not pixmap.isNull():
                return pixmap.scaled(
                    size[0],
                    size[1],
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )

    # Return placeholder if nothing found
    return create_placeholder_image(driver_code, size)

def load_team_logo(team_name: str, size: tuple = (120, 80)) -> QPixmap:
    """
    Load team logo from assets folder
    
    Args:
        team_name: Team name (e.g., 'Red Bull Racing', 'Ferrari')
        size: Desired size (width, height)
    
    Returns:
        QPixmap: Loaded and scaled logo, or placeholder if not found
    """
    base_dir = Path(__file__).resolve().parent.parent / "assets" / "logos" / "teams"
    team_name = team_name.strip()

    # Try common filename patterns first
    safe_names = [
        team_name.lower().replace(" ", "_"),
        team_name.lower().replace(" ", "-"),
        team_name.lower().replace(" racing", "").replace(" ", "_"),
        team_name.split()[0].lower(),  # First word only
    ]

    exts = ["png", "jpg", "jpeg", "svg"]
    for safe_name in safe_names:
        for ext in exts:
            logo_path = base_dir / f"{safe_name}.{ext}"
            if logo_path.exists():
                pixmap = QPixmap(str(logo_path))
                if not pixmap.isNull():
                    return pixmap.scaled(
                        size[0],
                        size[1],
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation,
                    )

    # Fallback: scan directory for closest normalized match
    target_norm = _normalize_name(team_name)
    if base_dir.exists():
        best_match = None
        best_score = 0.0
        for file in base_dir.iterdir():
            if file.is_file() and file.suffix.lower().lstrip(".") in exts:
                stem_norm = _normalize_name(file.stem.replace("logo", "").replace("team", "").replace("f1", ""))
                if target_norm and (target_norm in stem_norm or stem_norm in target_norm):
                    pixmap = QPixmap(str(file))
                    if not pixmap.isNull():
                        return pixmap.scaled(
                            size[0],
                            size[1],
                            Qt.AspectRatioMode.KeepAspectRatio,
                            Qt.TransformationMode.SmoothTransformation,
                        )
                score = SequenceMatcher(None, target_norm, stem_norm).ratio()
                if score > best_score:
                    best_score = score
                    best_match = file
        if best_match and best_score >= 0.6:
            pixmap = QPixmap(str(best_match))
            if not pixmap.isNull():
                return pixmap.scaled(
                    size[0],
                    size[1],
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )

    # Return placeholder
    return create_placeholder_image(team_name[:3].upper(), size)

def create_placeholder_image(text: str, size: tuple) -> QPixmap:
    """
    Create a placeholder image with text
    
    Args:
        text: Text to display
        size: Image size (width, height)
    
    Returns:
        QPixmap: Placeholder image
    """
    pixmap = QPixmap(size[0], size[1])
    pixmap.fill(Qt.GlobalColor.darkGray)
    
    # You could add text rendering here using QPainter
    # For simplicity, returning solid color
    return pixmap

def format_lap_time(seconds: float) -> str:
    """
    Format lap time in seconds to MM:SS.mmm
    
    Args:
        seconds: Lap time in seconds
    
    Returns:
        str: Formatted time string
    """
    if seconds is None or seconds == 0:
        return "N/A"
    
    minutes = int(seconds // 60)
    secs = seconds % 60
    
    return f"{minutes}:{secs:06.3f}"

def format_delta(delta_seconds: float) -> str:
    """
    Format time delta with +/- prefix
    
    Args:
        delta_seconds: Time difference in seconds
    
    Returns:
        str: Formatted delta (e.g., '+0.234' or '-0.156')
    """
    if delta_seconds is None:
        return "N/A"
    
    prefix = "+" if delta_seconds >= 0 else ""
    return f"{prefix}{delta_seconds:.3f}"

def format_speed(speed_kmh: float) -> str:
    """
    Format speed value
    
    Args:
        speed_kmh: Speed in km/h
    
    Returns:
        str: Formatted speed string
    """
    if speed_kmh is None:
        return "N/A"
    
    return f"{speed_kmh:.1f} km/h"

def format_percentage(value: float) -> str:
    """
    Format percentage value
    
    Args:
        value: Percentage value (0-100)
    
    Returns:
        str: Formatted percentage string
    """
    if value is None:
        return "N/A"
    
    return f"{value:.1f}%"

def create_stat_card(title: str, value: str, parent=None) -> QFrame:
    """
    Create a styled stat card widget
    
    Args:
        title: Stat title
        value: Stat value
        parent: Parent widget
    
    Returns:
        QFrame: Styled stat card
    """
    from PyQt6.QtWidgets import QVBoxLayout
    
    card = QFrame(parent)
    card.setFrameShape(QFrame.Shape.Box)
    card.setStyleSheet("""
        QFrame {
            background-color: #2A2A2A;
            border: 1px solid #3A3A3A;
            border-radius: 6px;
            padding: 10;px;
        }
    """)
    
    layout = QVBoxLayout(card)
    
    title_label = QLabel(title)
    title_label.setObjectName("stat_title")
    title_label.setStyleSheet("color: #AAAAAA; font-size: 10pt;")
    title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    
    value_label = QLabel(value)
    # Use camelCase id to match findChild lookups in hub modules
    value_label.setObjectName("statValue")
    value_label.setStyleSheet("color: #E10600; font-size: 18pt; font-weight: bold;")
    value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    
    layout.addWidget(title_label)
    layout.addWidget(value_label)
    
    return card

def create_section_header(text: str) -> QLabel:
    """
    Create a styled section header
    
    Args:
        text: Header text
    
    Returns:
        QLabel: Styled header
    """
    header = QLabel(text)
    header.setStyleSheet("""
        QLabel {
            font-size: 16pt;
            font-weight: bold;
            color: #E10600;
            padding: 8px 0px;
            border-bottom: 2px solid #E10600;
        }
    """)
    return header

def get_tyre_compound_color(compound: str) -> str:
    """
    Get color for tyre compound
    
    Args:
        compound: Tyre compound name
    
    Returns:
        str: Hex color code
    """
    colors = {
        'SOFT': '#FF3333',
        'MEDIUM': '#FFF200',
        'HARD': '#FFFFFF',
        'INTERMEDIATE': '#43B02A',
        'WET': '#0067AD'
    }
    
    return colors.get(compound.upper(), '#999999')

def get_status_color(status: str) -> str:
    """
    Get color for race status
    
    Args:
        status: Status text
    
    Returns:
        str: Hex color code
    """
    if 'Finished' in status or '+' in status:
        return '#00FF00'  # Green
    elif 'Lap' in status:
        return '#FFFF00'  # Yellow
    else:
        return '#FF0000'  # Red (DNF)

def ensure_assets_exist():
    """
    Ensure assets directories exist
    """
    dirs = [
        'assets',
        'assets/logos',
        'assets/logos/drivers',
        'assets/logos/teams',
        'assets/icons',
        'fastf1_cache',
        'cache'
    ]
    
    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)

def get_flag_emoji(nationality: str) -> str:
    """
    Get flag emoji for nationality
    """
    flags = {
        'Dutch': '🇳🇱',
        'British': '🇬🇧',
        'Monegasque': '🇲🇨',
        'Spanish': '🇪🇸',
        'Mexican': '🇲🇽',
        'German': '🇩🇪',
        'Finnish': '🇫🇮',
        'Australian': '🇦🇺',
        'French': '🇫🇷',
        'Canadian': '🇨🇦',
        'Danish': '🇩🇰',
        'Thai': '🇹🇭',
        'Japanese': '🇯🇵',
        'Chinese': '🇨🇳',
        'American': '🇺🇸',
        'Italian': '🇮🇹',
        'Austrian': '🇦🇹',
        'Polish': '🇵🇱',
        'Brazilian': '🇧🇷',
        'Swedish': '🇸🇪',
        'Belgian': '🇧🇪'
    }
    return flags.get(nationality, '')
