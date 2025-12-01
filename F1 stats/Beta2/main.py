"""
F1 Dashboard Beta 2 - Main Entry Point
Launches the PyQt5 application
"""
import sys
from PyQt5.QtWidgets import QApplication
from ui_main import F1DashboardWindow

def main():
    print("[DEBUG] Creating QApplication...")
    app = QApplication(sys.argv)
    print("[DEBUG] QApplication created")
    app.setApplicationName("F1 Dashboard Beta 2 - UI Version")
    
    print("[DEBUG] Creating F1DashboardWindow...")
    window = F1DashboardWindow()
    print("[DEBUG] F1DashboardWindow created")
    
    print("[DEBUG] Showing window...")
    window.show()
    print("[DEBUG] Window shown, calling app.exec_()...")
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()