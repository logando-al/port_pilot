"""
Integration tests for tray icon functionality.
"""

import pytest
from unittest.mock import patch, MagicMock

# Skip if PyQt6 not available (CI without display)
pytest.importorskip("PyQt6")


class TestTrayIntegration:
    """Integration tests for system tray functionality."""
    
    @pytest.fixture
    def qapp(self):
        """Create QApplication for testing."""
        from PyQt6.QtWidgets import QApplication
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        yield app
    
    def test_tray_icon_creation(self, qapp):
        """Test that tray icon can be created."""
        from src.ui.tray_icon import TrayIcon
        
        with patch('src.ui.tray_icon.PortScanner'):
            with patch('src.ui.tray_icon.TunnelManager'):
                tray = TrayIcon(qapp)
                assert tray is not None
    
    def test_tray_menu_exists(self, qapp):
        """Test that tray icon has context menu."""
        from src.ui.tray_icon import TrayIcon
        
        with patch('src.ui.tray_icon.PortScanner'):
            with patch('src.ui.tray_icon.TunnelManager'):
                tray = TrayIcon(qapp)
                assert tray.contextMenu() is not None
