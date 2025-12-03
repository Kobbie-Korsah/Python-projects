"""
Matplotlib helpers for consistent chart generation across modules.
"""

from typing import Optional

import matplotlib.pyplot as plt
import pandas as pd


def style_axes(ax: plt.Axes, title: str) -> None:
    """Apply a consistent style to axes."""
    ax.set_title(title, color="#e10600")
    ax.grid(True, linestyle="--", alpha=0.3)


def plot_speed_trace(df: pd.DataFrame, ax: Optional[plt.Axes] = None) -> plt.Axes:
    """Plot speed vs distance."""
    ax = ax or plt.gca()
    ax.plot(df["Distance"], df["Speed"], color="#e10600", label="Speed")
    style_axes(ax, "Speed vs Distance")
    ax.set_xlabel("Distance (m)")
    ax.set_ylabel("Speed (km/h)")
    ax.legend()
    return ax


def export_png(fig: plt.Figure, path: str) -> None:
    """Save figure to disk."""
    fig.savefig(path, dpi=150, bbox_inches="tight")


def export_md(text: str, path: str) -> None:
    """Write markdown to disk."""
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)


def convert_md_to_pdf(md_path: str, pdf_path: str) -> None:
    """
    Convert markdown to PDF using pandoc if available.
    Errors are swallowed so the UI remains stable when pandoc is missing.
    """
    import subprocess

    try:
        subprocess.run(["pandoc", md_path, "-o", pdf_path], check=True)
    except Exception:
        # In constrained environments pandoc may not exist; ignore silently.
        pass
