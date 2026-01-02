"""
Unit tests for PortScanner module.
"""

import pytest
from unittest.mock import patch, MagicMock

from src.core.port_scanner import PortScanner, PortInfo


class TestPortScanner:
    """Tests for PortScanner class."""
    
    def test_scan_returns_port_list(self, mock_psutil_connections, mock_psutil_process):
        """Test that scan() returns a list of PortInfo objects."""
        with patch('psutil.net_connections', return_value=mock_psutil_connections):
            with patch('psutil.Process', return_value=mock_psutil_process):
                scanner = PortScanner()
                ports = scanner.scan()
                
                assert len(ports) == 1
                assert isinstance(ports[0], PortInfo)
                assert ports[0].local_port == 8000
                assert ports[0].process_name == "python.exe"
    
    def test_get_cached_returns_last_scan(self, mock_psutil_connections, mock_psutil_process):
        """Test that get_cached() returns the last scan results."""
        with patch('psutil.net_connections', return_value=mock_psutil_connections):
            with patch('psutil.Process', return_value=mock_psutil_process):
                scanner = PortScanner()
                scanner.scan()
                cached = scanner.get_cached()
                
                assert len(cached) == 1
                assert cached[0].local_port == 8000
    
    def test_find_by_port(self, mock_psutil_connections, mock_psutil_process):
        """Test finding connections by port number."""
        with patch('psutil.net_connections', return_value=mock_psutil_connections):
            with patch('psutil.Process', return_value=mock_psutil_process):
                scanner = PortScanner()
                scanner.scan()
                
                found = scanner.find_by_port(8000)
                assert len(found) == 1
                
                not_found = scanner.find_by_port(9999)
                assert len(not_found) == 0
    
    def test_find_by_process(self, mock_psutil_connections, mock_psutil_process):
        """Test finding connections by process name."""
        with patch('psutil.net_connections', return_value=mock_psutil_connections):
            with patch('psutil.Process', return_value=mock_psutil_process):
                scanner = PortScanner()
                scanner.scan()
                
                found = scanner.find_by_process("python")
                assert len(found) == 1
                
                not_found = scanner.find_by_process("node")
                assert len(not_found) == 0
    
    def test_get_listening_ports(self, mock_psutil_connections, mock_psutil_process):
        """Test filtering for LISTEN status ports."""
        with patch('psutil.net_connections', return_value=mock_psutil_connections):
            with patch('psutil.Process', return_value=mock_psutil_process):
                scanner = PortScanner()
                scanner.scan()
                
                listening = scanner.get_listening_ports()
                assert len(listening) == 1
                assert listening[0].status == "LISTEN"
    
    def test_handles_access_denied(self):
        """Test graceful handling of access denied errors."""
        import psutil
        with patch('psutil.net_connections', side_effect=psutil.AccessDenied()):
            scanner = PortScanner()
            ports = scanner.scan()
            
            assert ports == []
    
    def test_handles_no_process(self):
        """Test handling when process lookup fails."""
        mock_conn = MagicMock()
        mock_conn.laddr = MagicMock(ip="127.0.0.1", port=8000)
        mock_conn.raddr = None
        mock_conn.pid = 99999
        mock_conn.status = "LISTEN"
        mock_conn.type = 1
        
        import psutil
        with patch('psutil.net_connections', return_value=[mock_conn]):
            with patch('psutil.Process', side_effect=psutil.NoSuchProcess(99999)):
                scanner = PortScanner()
                ports = scanner.scan()
                
                assert len(ports) == 1
                assert ports[0].process_name == "Unknown"
