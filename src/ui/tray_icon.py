"""
TrayIcon module - Main system tray entry point for PortPilot.
"""

from PyQt6.QtWidgets import QSystemTrayIcon, QMenu, QApplication
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import QTimer
import qtawesome as qta

from src.core.port_scanner import PortScanner
from src.core.tunnel_manager import TunnelManager, TunnelStatus


class TrayIcon(QSystemTrayIcon):
    """
    System tray icon that serves as the main UI entry point.
    
    Provides quick access to:
    - Active tunnel status
    - Top active ports
    - Dashboard window
    """
    
    def __init__(self, app: QApplication, parent=None):
        super().__init__(parent)
        self.app = app
        self.port_scanner = PortScanner()
        self.tunnel_manager = TunnelManager()
        self.dashboard = None
        
        self._setup_icon()
        self._setup_menu()
        self._setup_refresh_timer()
        
        self.activated.connect(self._on_activated)
    
    def _setup_icon(self):
        """Set up the tray icon."""
        from pathlib import Path
        icon_path = Path(__file__).parent.parent.parent / "resources" / "icons" / "tray_icon.png"
        if icon_path.exists():
            icon = QIcon(str(icon_path))
        else:
            icon = QIcon()
        self.setIcon(icon)
        self.setToolTip("PortPilot - Port Manager")
    
    def _setup_menu(self):
        """Create the context menu."""
        self.menu = QMenu()
        
        # Tunnels section
        self.tunnels_menu = self.menu.addMenu(qta.icon('fa5s.link', color='#00d4ff'), "Tunnels")
        self._update_tunnels_menu()
        
        self.menu.addSeparator()
        
        # Active ports section
        self.ports_menu = self.menu.addMenu(qta.icon('fa5s.plug', color='#4CAF50'), "Active Ports")
        self._update_ports_menu()
        
        self.menu.addSeparator()
        
        # Dashboard action
        dashboard_action = QAction(qta.icon('fa5s.tachometer-alt', color='#2196F3'), "Open Dashboard", self.menu)
        dashboard_action.triggered.connect(self._open_dashboard)
        self.menu.addAction(dashboard_action)
        
        # Refresh action
        refresh_action = QAction(qta.icon('fa5s.sync-alt', color='#e0e0e0'), "Refresh", self.menu)
        refresh_action.triggered.connect(self._refresh_all)
        self.menu.addAction(refresh_action)
        
        self.menu.addSeparator()
        
        # Exit action
        exit_action = QAction(qta.icon('fa5s.power-off', color='#f44336'), "Exit", self.menu)
        exit_action.triggered.connect(self._exit_app)
        self.menu.addAction(exit_action)
        
        self.setContextMenu(self.menu)
    
    def _setup_refresh_timer(self):
        """Set up auto-refresh timer."""
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self._refresh_all)
        self.refresh_timer.start(30000)  # Refresh every 30 seconds
    
    def _update_tunnels_menu(self):
        """Update the tunnels submenu."""
        self.tunnels_menu.clear()
        
        tunnels = self.tunnel_manager.get_all_tunnels()
        if not tunnels:
            action = QAction("No tunnels configured", self.tunnels_menu)
            action.setEnabled(False)
            self.tunnels_menu.addAction(action)
            return
        
        for tunnel in tunnels:
            status = self.tunnel_manager.get_status(tunnel.name)
            status_text = "[ON]" if status == TunnelStatus.RUNNING else "[OFF]"
            action = QAction(f"{status_text} {tunnel.name} ({tunnel.local_port})", self.tunnels_menu)
            action.setCheckable(True)
            action.setChecked(status == TunnelStatus.RUNNING)
            action.triggered.connect(lambda checked, t=tunnel: self._toggle_tunnel(t.name, checked))
            self.tunnels_menu.addAction(action)
    
    def _update_ports_menu(self):
        """Update the active ports submenu."""
        self.ports_menu.clear()
        
        ports = self.port_scanner.scan()
        listening = [p for p in ports if p.status == 'LISTEN'][:10]  # Top 10
        
        if not listening:
            action = QAction("No listening ports", self.ports_menu)
            action.setEnabled(False)
            self.ports_menu.addAction(action)
            return
        
        for port in listening:
            action = QAction(f"{port.local_port}: {port.process_name}", self.ports_menu)
            self.ports_menu.addAction(action)
    
    def _toggle_tunnel(self, name: str, start: bool):
        """Toggle a tunnel on/off."""
        if start:
            self.tunnel_manager.start_tunnel(name)
        else:
            self.tunnel_manager.stop_tunnel(name)
        self._update_tunnels_menu()
    
    def _open_dashboard(self):
        """Open the main dashboard window."""
        from src.ui.dashboard import Dashboard
        
        if self.dashboard is None:
            self.dashboard = Dashboard(self.port_scanner, self.tunnel_manager)
        
        self.dashboard.show()
        self.dashboard.raise_()
        self.dashboard.activateWindow()
    
    def _refresh_all(self):
        """Refresh all data."""
        self._update_ports_menu()
        self._update_tunnels_menu()
    
    def _exit_app(self):
        """Clean up and exit the application."""
        self.tunnel_manager.stop_all()
        self.refresh_timer.stop()
        self.hide()
        self.app.quit()
    
    def _on_activated(self, reason):
        """Handle tray icon activation."""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self._open_dashboard()
