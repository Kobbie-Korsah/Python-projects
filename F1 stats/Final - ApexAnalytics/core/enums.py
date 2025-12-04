"""
F1 Analytics Suite - Core Enumerations
Define application-wide constants and enums
"""

from enum import Enum

class AppMode(Enum):
    """Application mode - Driver or Team focus"""
    DRIVER = "Driver"
    TEAM = "Team"

class SessionType(Enum):
    """F1 Session types"""
    RACE = "R"
    QUALIFYING = "Q"
    SPRINT = "S"
    PRACTICE_1 = "FP1"
    PRACTICE_2 = "FP2"
    PRACTICE_3 = "FP3"

class ExportFormat(Enum):
    """Available export formats"""
    PNG = "png"
    CSV = "csv"
    JSON = "json"
    PDF = "pdf"

# Team colors for visualization
TEAM_COLORS = {
    "Red Bull Racing": "#1E41FF",
    "Mercedes": "#00D2BE",
    "Ferrari": "#DC0000",
    "McLaren": "#FF8700",
    "Aston Martin": "#006F62",
    "Alpine": "#0090FF",
    "Williams": "#005AFF",
    "AlphaTauri": "#2B4562",
    "Alfa Romeo": "#900000",
    "Haas": "#FFFFFF",
    "RB": "#2B4562"
}

# Driver colors
DRIVER_COLORS = {
    "VER": "#1E41FF", "PER": "#1E41FF",
    "HAM": "#00D2BE", "RUS": "#00D2BE",
    "LEC": "#DC0000", "SAI": "#DC0000",
    "NOR": "#FF8700", "PIA": "#FF8700",
    "ALO": "#006F62", "STR": "#006F62",
    "GAS": "#0090FF", "OCO": "#0090FF",
    "TSU": "#2B4562", "RIC": "#2B4562",
    "BOT": "#900000", "ZHO": "#900000",
    "HUL": "#FFFFFF", "MAG": "#FFFFFF",
    "ALB": "#005AFF", "SAR": "#005AFF"
}

# API endpoints
JOLPICA_BASE_URL = "https://api.jolpi.ca/ergast/f1"

# Cache settings
CACHE_EXPIRY_HOURS = 24
MAX_CACHE_SIZE_MB = 500