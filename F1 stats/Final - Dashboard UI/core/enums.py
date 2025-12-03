"""Common enums shared across the application."""

import enum


class HubMode(enum.Enum):
    """Determines which hub is visible."""

    DRIVER = "driver"
    TEAM = "team"


class ExportFormat(enum.Enum):
    """Export targets supported across modules."""

    CSV = "csv"
    JSON = "json"
    PNG = "png"
    MARKDOWN = "md"
