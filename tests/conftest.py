"""
Pytest fixtures and configuration for PortPilot tests.
"""

import pytest
from unittest.mock import MagicMock, patch


@pytest.fixture
def mock_psutil_connections():
    """Mock psutil.net_connections() response."""
    MockConnection = MagicMock()
    MockConnection.laddr = MagicMock(ip="127.0.0.1", port=8000)
    MockConnection.raddr = None
    MockConnection.pid = 1234
    MockConnection.status = "LISTEN"
    MockConnection.type = 1  # TCP
    
    return [MockConnection]


@pytest.fixture
def mock_psutil_process():
    """Mock psutil.Process."""
    process = MagicMock()
    process.name.return_value = "python.exe"
    process.pid = 1234
    process.is_running.return_value = True
    process.status.return_value = "running"
    process.cmdline.return_value = ["python", "app.py"]
    process.username.return_value = "testuser"
    process.create_time.return_value = 1234567890.0
    return process


@pytest.fixture
def sample_tunnel_config():
    """Sample tunnel configuration."""
    from src.core.tunnel_manager import TunnelConfig
    return TunnelConfig(
        name="test-tunnel",
        remote_user="testuser",
        remote_host="example.com",
        local_port=8080,
        remote_port=80,
        enabled=False
    )


@pytest.fixture
def temp_config_dir(tmp_path):
    """Temporary directory for config files."""
    config_dir = tmp_path / ".portpilot"
    config_dir.mkdir()
    return config_dir
