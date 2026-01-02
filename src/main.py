"""
PortPilot - Main Entry Point

A system tray utility to visualize local ports, kill blocking processes,
and manage SSH tunnels.
"""

import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

from src.core.version import VERSION
from src.ui.tray_icon import TrayIcon
from src.utils.config import Config
from src.utils.updater import Updater


def main():
    """Application entry point."""
    # Enable high DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    app.setApplicationName("PortPilot")
    app.setApplicationVersion(VERSION)
    
    # Load configuration
    config = Config()
    
    # Check for updates on startup
    if config.get("check_updates", True):
        updater = Updater()
        has_update, message = updater.check_for_updates()
        if has_update:
            from PyQt6.QtWidgets import QMessageBox
            reply = QMessageBox.question(
                None,
                "Update Available",
                f"{message}\n\nWould you like to download the update?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                updater.download_and_install()
    
    # Create system tray icon
    tray = TrayIcon(app)
    tray.show()
    
    # Show notification
    tray.showMessage(
        "PortPilot",
        "PortPilot is running in the system tray.",
        TrayIcon.MessageIcon.Information,
        2000
    )
    
    # Start minimized or show dashboard
    if not config.get("start_minimized", False):
        tray._open_dashboard()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
