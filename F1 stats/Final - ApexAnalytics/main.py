"""
F1 Analytics Suite - Main Entry Point
Production-level PyQt6 F1 Analytics Application
"""

import sys
from pathlib import Path
from datetime import datetime
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPalette, QColor
from ui_main import F1AnalyticsSuite


def install_exception_hook():
    """Log uncaught exceptions instead of silently exiting."""
    log_dir = Path(__file__).resolve().parent / "logs"
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / "error.log"

    def _hook(exc_type, exc_value, exc_traceback):
        timestamp = datetime.now().isoformat(timespec="seconds")
        trace = "".join(__import__("traceback").format_exception(exc_type, exc_value, exc_traceback))
        log_entry = f"[{timestamp}] {exc_type.__name__}: {exc_value}\n{trace}\n"
        try:
            with log_file.open("a", encoding="utf-8") as f:
                f.write(log_entry)
        except Exception:
            pass

        app = QApplication.instance()
        if app is not None:
            QMessageBox.critical(None, "Unexpected Error",
                                 "The application hit an unexpected error and needs attention.\n\n"
                                 f"Details were written to {log_file}")
        else:
            print(log_entry)

    sys.excepthook = _hook

def setup_dark_theme(app):
    """Configure dark theme for the application"""
    palette = QPalette()
    
    # Dark theme colors
    palette.setColor(QPalette.ColorRole.Window, QColor(30, 30, 30))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.Base, QColor(20, 20, 20))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(40, 40, 40))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.Text, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.Button, QColor(40, 40, 40))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.BrightText, QColor(225, 6, 0))
    palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(225, 6, 0))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
    
    app.setPalette(palette)

def main():
    """Main application entry point"""
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    install_exception_hook()
    
    app = QApplication(sys.argv)
    app.setApplicationName("ApexAnalytics")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("F1 Analytics")
    
    # Apply dark theme
    setup_dark_theme(app)
    
    # Load custom stylesheet
    style_path = Path(__file__).resolve().parent / 'styles.qss'
    if style_path.exists():
        app.setStyleSheet(style_path.read_text(encoding='utf-8'))
    else:
        print(f"Warning: {style_path.name} not found at {style_path}, using default theme")
    
    # Create and show main window
    window = F1AnalyticsSuite()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
