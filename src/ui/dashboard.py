"""
Dashboard module - Main window with tabs for ports and tunnels.
"""

from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QMainWindow, QStatusBar, QTabWidget, QVBoxLayout, QWidget

from src.core.port_scanner import PortScanner
from src.core.tunnel_manager import TunnelManager
from src.core.version import VERSION
from src.ui.widgets.port_table import PortTableWidget
from src.ui.widgets.tunnel_list import TunnelListWidget


class Dashboard(QMainWindow):
    """
    Main dashboard window with tabbed interface.

    Tabs:
    - Active Ports: Searchable table of listening ports with kill functionality
    - Tunnel Manager: List of saved tunnels with add/edit/toggle controls
    """

    def __init__(self, port_scanner: PortScanner, tunnel_manager: TunnelManager, parent=None):
        super().__init__(parent)
        self.port_scanner = port_scanner
        self.tunnel_manager = tunnel_manager

        self._setup_window()
        self._setup_menubar()
        self._setup_ui()
        self._setup_statusbar()
        self._setup_refresh_timer()
        self._load_stylesheet()

    def _setup_window(self):
        """Configure window properties."""
        self.setWindowTitle(f"PortPilot v{VERSION}")
        self.setMinimumSize(800, 600)
        self.resize(1000, 700)

        # Center on screen
        screen = self.screen().geometry()
        self.move(
            (screen.width() - self.width()) // 2,
            (screen.height() - self.height()) // 2
        )

    def _setup_menubar(self):
        """Create the menu bar."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("&File")

        refresh_action = QAction("&Refresh", self)
        refresh_action.setShortcut("F5")
        refresh_action.triggered.connect(self._refresh_all)
        file_menu.addAction(refresh_action)

        file_menu.addSeparator()

        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # View menu
        view_menu = menubar.addMenu("&View")

        dark_mode_action = QAction("&Dark Mode", self)
        dark_mode_action.setCheckable(True)
        dark_mode_action.setChecked(True)
        view_menu.addAction(dark_mode_action)

        # Help menu
        help_menu = menubar.addMenu("&Help")

        about_action = QAction("&About", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

    def _setup_ui(self):
        """Set up the main UI layout."""
        central = QWidget()
        self.setCentralWidget(central)

        layout = QVBoxLayout(central)
        layout.setContentsMargins(10, 10, 10, 10)

        # Tabbed interface
        self.tabs = QTabWidget()

        # Active Ports tab
        self.port_table = PortTableWidget(self.port_scanner)
        self.tabs.addTab(self.port_table, "Active Ports")

        # Tunnel Manager tab
        self.tunnel_list = TunnelListWidget(self.tunnel_manager)
        self.tabs.addTab(self.tunnel_list, "Tunnel Manager")

        layout.addWidget(self.tabs)

    def _setup_statusbar(self):
        """Create the status bar."""
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        self._update_status()

    def _setup_refresh_timer(self):
        """Set up auto-refresh timer."""
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self._refresh_all)
        self.refresh_timer.start(5000)  # Refresh every 5 seconds

    def _load_stylesheet(self):
        """Load the dark theme stylesheet."""
        try:
            from pathlib import Path
            style_path = Path(__file__).parent / "styles" / "dark_theme.qss"
            if style_path.exists():
                with open(style_path) as f:
                    self.setStyleSheet(f.read())
        except Exception as e:
            print(f"Error loading stylesheet: {e}")

    def _refresh_all(self):
        """Refresh all data."""
        self.port_table.refresh()
        self.tunnel_list.refresh()
        self._update_status()

    def _update_status(self):
        """Update the status bar."""
        ports = len(self.port_scanner.get_listening_ports())
        tunnels = len([t for t in self.tunnel_manager.get_all_tunnels() if t.enabled])
        self.statusbar.showMessage(f"Listening Ports: {ports} | Active Tunnels: {tunnels}")

    def _show_about(self):
        """Show about dialog."""
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.about(
            self,
            "About PortPilot",
            f"<h3>PortPilot v{VERSION}</h3>"
            "<p>A system tray utility to visualize local ports, "
            "kill blocking processes, and manage SSH tunnels.</p>"
            "<p>© 2026 logando-al</p>"
        )

    def closeEvent(self, event):  # noqa: N802
        """Handle window close - hide instead of quit."""
        event.ignore()
        self.hide()
