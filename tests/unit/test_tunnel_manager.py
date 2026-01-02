"""
Unit tests for TunnelManager module.
"""

from unittest.mock import MagicMock, patch

from src.core.tunnel_manager import TunnelConfig, TunnelManager, TunnelStatus


class TestTunnelConfig:
    """Tests for TunnelConfig dataclass."""

    def test_to_dict(self, sample_tunnel_config):
        """Test conversion to dictionary."""
        data = sample_tunnel_config.to_dict()

        assert data["name"] == "test-tunnel"
        assert data["remote_user"] == "testuser"
        assert data["local_port"] == 8080

    def test_from_dict(self):
        """Test creation from dictionary."""
        data = {
            "name": "test",
            "remote_user": "user",
            "remote_host": "host.com",
            "local_port": 8080,
            "remote_port": 80,
            "enabled": False,
            "ssh_key": None
        }
        config = TunnelConfig.from_dict(data)

        assert config.name == "test"
        assert config.local_port == 8080


class TestTunnelManager:
    """Tests for TunnelManager class."""

    def test_add_tunnel(self, temp_config_dir, sample_tunnel_config):
        """Test adding a new tunnel."""
        manager = TunnelManager(temp_config_dir / "tunnels.json")
        result = manager.add_tunnel(sample_tunnel_config)

        assert result is True
        assert "test-tunnel" in manager.tunnels

    def test_add_duplicate_tunnel(self, temp_config_dir, sample_tunnel_config):
        """Test adding a duplicate tunnel fails."""
        manager = TunnelManager(temp_config_dir / "tunnels.json")
        manager.add_tunnel(sample_tunnel_config)
        result = manager.add_tunnel(sample_tunnel_config)

        assert result is False

    def test_remove_tunnel(self, temp_config_dir, sample_tunnel_config):
        """Test removing a tunnel."""
        manager = TunnelManager(temp_config_dir / "tunnels.json")
        manager.add_tunnel(sample_tunnel_config)
        result = manager.remove_tunnel("test-tunnel")

        assert result is True
        assert "test-tunnel" not in manager.tunnels

    def test_remove_nonexistent_tunnel(self, temp_config_dir):
        """Test removing non-existent tunnel fails."""
        manager = TunnelManager(temp_config_dir / "tunnels.json")
        result = manager.remove_tunnel("nonexistent")

        assert result is False

    def test_get_all_tunnels(self, temp_config_dir, sample_tunnel_config):
        """Test getting all tunnels."""
        manager = TunnelManager(temp_config_dir / "tunnels.json")
        manager.add_tunnel(sample_tunnel_config)

        tunnels = manager.get_all_tunnels()

        assert len(tunnels) == 1
        assert tunnels[0].name == "test-tunnel"

    def test_config_persistence(self, temp_config_dir, sample_tunnel_config):
        """Test that tunnels are persisted to disk."""
        manager1 = TunnelManager(temp_config_dir / "tunnels.json")
        manager1.add_tunnel(sample_tunnel_config)

        # Create new manager to test loading
        manager2 = TunnelManager(temp_config_dir / "tunnels.json")
        tunnels = manager2.get_all_tunnels()

        assert len(tunnels) == 1
        assert tunnels[0].name == "test-tunnel"

    def test_start_tunnel(self, temp_config_dir, sample_tunnel_config):
        """Test starting a tunnel."""
        manager = TunnelManager(temp_config_dir / "tunnels.json")
        manager.add_tunnel(sample_tunnel_config)

        with patch('subprocess.Popen') as mock_popen:
            mock_popen.return_value = MagicMock()
            status = manager.start_tunnel("test-tunnel")

            assert status == TunnelStatus.RUNNING
            mock_popen.assert_called_once()

    def test_stop_tunnel(self, temp_config_dir, sample_tunnel_config):
        """Test stopping a tunnel."""
        manager = TunnelManager(temp_config_dir / "tunnels.json")
        manager.add_tunnel(sample_tunnel_config)

        with patch('subprocess.Popen') as mock_popen:
            mock_process = MagicMock()
            mock_popen.return_value = mock_process

            manager.start_tunnel("test-tunnel")
            status = manager.stop_tunnel("test-tunnel")

            assert status == TunnelStatus.STOPPED
            mock_process.terminate.assert_called_once()

    def test_get_status_stopped(self, temp_config_dir, sample_tunnel_config):
        """Test getting status of stopped tunnel."""
        manager = TunnelManager(temp_config_dir / "tunnels.json")
        manager.add_tunnel(sample_tunnel_config)

        status = manager.get_status("test-tunnel")
        assert status == TunnelStatus.STOPPED

    def test_build_ssh_command(self, temp_config_dir, sample_tunnel_config):
        """Test SSH command building."""
        manager = TunnelManager(temp_config_dir / "tunnels.json")
        cmd = manager._build_ssh_command(sample_tunnel_config)

        assert cmd[0] == "ssh"
        assert "-N" in cmd
        assert "-L" in cmd
        assert "8080:localhost:80" in cmd
        assert "testuser@example.com" in cmd
