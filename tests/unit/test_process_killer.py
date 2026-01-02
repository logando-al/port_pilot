"""
Unit tests for ProcessKiller module.
"""

import pytest
from unittest.mock import patch, MagicMock

from src.core.process_killer import ProcessKiller, KillResult


class TestProcessKiller:
    """Tests for ProcessKiller class."""
    
    def test_kill_success(self, mock_psutil_process):
        """Test successful process termination."""
        with patch('psutil.Process', return_value=mock_psutil_process):
            result, message = ProcessKiller.kill(1234)
            
            assert result == KillResult.SUCCESS
            assert "Successfully terminated" in message
            mock_psutil_process.terminate.assert_called_once()
    
    def test_kill_force(self, mock_psutil_process):
        """Test forced process termination."""
        with patch('psutil.Process', return_value=mock_psutil_process):
            result, message = ProcessKiller.kill(1234, force=True)
            
            assert result == KillResult.SUCCESS
            mock_psutil_process.kill.assert_called_once()
    
    def test_kill_not_found(self):
        """Test killing non-existent process."""
        import psutil
        with patch('psutil.Process', side_effect=psutil.NoSuchProcess(99999)):
            result, message = ProcessKiller.kill(99999)
            
            assert result == KillResult.NOT_FOUND
            assert "not found" in message
    
    def test_kill_access_denied(self):
        """Test killing process without permission."""
        import psutil
        with patch('psutil.Process', side_effect=psutil.AccessDenied()):
            result, message = ProcessKiller.kill(1)
            
            assert result == KillResult.ACCESS_DENIED
            assert "Access denied" in message
    
    def test_is_running_true(self, mock_psutil_process):
        """Test checking if process is running."""
        with patch('psutil.Process', return_value=mock_psutil_process):
            assert ProcessKiller.is_running(1234) is True
    
    def test_is_running_false(self):
        """Test checking if process is not running."""
        import psutil
        with patch('psutil.Process', side_effect=psutil.NoSuchProcess(99999)):
            assert ProcessKiller.is_running(99999) is False
    
    def test_get_process_info(self, mock_psutil_process):
        """Test getting process information."""
        with patch('psutil.Process', return_value=mock_psutil_process):
            info = ProcessKiller.get_process_info(1234)
            
            assert info["pid"] == 1234
            assert info["name"] == "python.exe"
            assert info["status"] == "running"
    
    def test_get_process_info_not_found(self):
        """Test getting info for non-existent process."""
        import psutil
        with patch('psutil.Process', side_effect=psutil.NoSuchProcess(99999)):
            info = ProcessKiller.get_process_info(99999)
            
            assert "error" in info
