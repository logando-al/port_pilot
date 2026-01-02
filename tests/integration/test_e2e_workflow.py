"""
End-to-end workflow tests.
"""

from unittest.mock import MagicMock, patch


class TestE2EWorkflow:
    """End-to-end workflow tests."""

    def test_scan_and_kill_workflow(self, mock_psutil_connections, mock_psutil_process):
        """Test complete scan -> find -> kill workflow."""
        from src.core.port_scanner import PortScanner
        from src.core.process_killer import KillResult, ProcessKiller

        with patch('psutil.net_connections', return_value=mock_psutil_connections):
            with patch('psutil.Process', return_value=mock_psutil_process):
                # Scan ports
                scanner = PortScanner()
                scanner.scan()

                # Find port 8000
                matches = scanner.find_by_port(8000)
                assert len(matches) == 1

                # Kill the process
                pid = matches[0].pid
                result, message = ProcessKiller.kill(pid)

                assert result == KillResult.SUCCESS

    def test_tunnel_lifecycle(self, temp_config_dir, sample_tunnel_config):
        """Test complete tunnel add -> start -> stop -> remove workflow."""
        from src.core.tunnel_manager import TunnelManager, TunnelStatus

        manager = TunnelManager(temp_config_dir / "tunnels.json")

        # Add tunnel
        assert manager.add_tunnel(sample_tunnel_config) is True

        # Start tunnel
        with patch('subprocess.Popen') as mock_popen:
            mock_process = MagicMock()
            mock_process.poll.return_value = None  # Process running
            mock_popen.return_value = mock_process

            status = manager.start_tunnel("test-tunnel")
            assert status == TunnelStatus.RUNNING

            # Verify running
            assert manager.get_status("test-tunnel") == TunnelStatus.RUNNING

            # Stop tunnel
            status = manager.stop_tunnel("test-tunnel")
            assert status == TunnelStatus.STOPPED

        # Remove tunnel
        assert manager.remove_tunnel("test-tunnel") is True
        assert len(manager.get_all_tunnels()) == 0
