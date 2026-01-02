"""
Pytest fixtures and configuration for PortPilot tests.
"""

from unittest.mock import MagicMock

import pytest


@pytest.fixture
def mock_psutil_connections():
    """Mock psutil.net_connections() response."""
    mock_connection = MagicMock()
    mock_connection.laddr = MagicMock(ip="127.0.0.1", port=8000)
    mock_connection.raddr = None
    mock_connection.pid = 1234
    mock_connection.status = "LISTEN"
    mock_connection.type = 1  # TCP

    return [mock_connection]


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
