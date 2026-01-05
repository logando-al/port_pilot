"""
PortPilot - Main Entry Point

A system tray utility to visualize local ports, kill blocking processes,
and manage SSH tunnels.
"""

import sys

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import QApplication

from src.core.version import VERSION
from src.ui.splash_screen import SplashScreen
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

    # Show splash screen
    splash = SplashScreen()
    splash.show()
    app.processEvents()

    # Load configuration
    config = Config()
    splash.set_status("Loading configuration...")
    splash.set_progress(30)
    app.processEvents()

    # Check for updates on startup
    splash.set_status("Checking for updates...")
    splash.set_progress(50)
    app.processEvents()

    update_available = False
    update_message = ""
    if config.get("check_updates", True):
        updater = Updater()
        update_available, update_message = updater.check_for_updates()

    splash.set_status("Initializing tray...")
    splash.set_progress(70)
    app.processEvents()

    # Create system tray icon
    tray = TrayIcon(app)

    splash.set_status("Ready!")
    splash.set_progress(100)
    app.processEvents()

    # Close splash and show main UI
    def finish_startup():
        splash.close()
        tray.show()

        # Show update notification if available
        if update_available:
            from PyQt6.QtWidgets import QMessageBox
            reply = QMessageBox.question(
                None,
                "Update Available",
                f"{update_message}\n\nWould you like to download the update?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                updater.download_and_install()

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

    # Delay closing splash for smooth transition
    QTimer.singleShot(1500, finish_startup)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()

