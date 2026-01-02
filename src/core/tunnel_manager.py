"""
TunnelManager module - Manages SSH tunnel configurations and subprocess states.
"""

import json
import subprocess
import sys
from dataclasses import asdict, dataclass
from enum import Enum
from pathlib import Path


class TunnelStatus(Enum):
    """Status of an SSH tunnel."""
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    ERROR = "error"


@dataclass
class TunnelConfig:
    """Configuration for an SSH tunnel."""
    name: str
    remote_user: str
    remote_host: str
    local_port: int
    remote_port: int
    enabled: bool = False
    ssh_key: str | None = None  # Path to SSH key file

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> 'TunnelConfig':
        return cls(**data)


class TunnelManager:
    """
    Manages persistent SSH tunnel configurations and their subprocess states.

    Tunnels are saved to a JSON file for persistence across app restarts.
    Each tunnel runs as a subprocess calling the system SSH client.
    """

    def __init__(self, config_path: Path | None = None):
        self.config_path = config_path or Path.home() / ".portpilot" / "tunnels.json"
        self.tunnels: dict[str, TunnelConfig] = {}
        self._processes: dict[str, subprocess.Popen] = {}
        self._load_config()

    def _load_config(self) -> None:
        """Load tunnel configurations from file."""
        if self.config_path.exists():
            try:
                with open(self.config_path) as f:
                    data = json.load(f)
                    for name, config in data.items():
                        self.tunnels[name] = TunnelConfig.from_dict(config)
            except (json.JSONDecodeError, KeyError) as e:
                print(f"Error loading tunnel config: {e}")

    def _save_config(self) -> None:
        """Save tunnel configurations to file."""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w') as f:
            data = {name: tunnel.to_dict() for name, tunnel in self.tunnels.items()}
            json.dump(data, f, indent=2)

    def add_tunnel(self, config: TunnelConfig) -> bool:
        """Add a new tunnel configuration."""
        if config.name in self.tunnels:
            return False
        self.tunnels[config.name] = config
        self._save_config()
        return True

    def remove_tunnel(self, name: str) -> bool:
        """Remove a tunnel configuration (stops it first if running)."""
        if name not in self.tunnels:
            return False
        self.stop_tunnel(name)
        del self.tunnels[name]
        self._save_config()
        return True

    def update_tunnel(self, name: str, config: TunnelConfig) -> bool:
        """Update an existing tunnel configuration."""
        if name not in self.tunnels:
            return False
        was_running = self.get_status(name) == TunnelStatus.RUNNING
        if was_running:
            self.stop_tunnel(name)
        self.tunnels[name] = config
        self._save_config()
        if was_running and config.enabled:
            self.start_tunnel(name)
        return True

    def start_tunnel(self, name: str) -> TunnelStatus:
        """Start an SSH tunnel."""
        if name not in self.tunnels:
            return TunnelStatus.ERROR

        config = self.tunnels[name]

        # Build SSH command
        cmd = self._build_ssh_command(config)

        try:
            # Start SSH subprocess
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0x08000000) if sys.platform == 'win32' else 0
            )
            self._processes[name] = process
            config.enabled = True
            self._save_config()
            return TunnelStatus.RUNNING

        except Exception as e:
            print(f"Error starting tunnel {name}: {e}")
            return TunnelStatus.ERROR

    def stop_tunnel(self, name: str) -> TunnelStatus:
        """Stop an SSH tunnel."""
        if name in self._processes:
            process = self._processes[name]
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
            del self._processes[name]

        if name in self.tunnels:
            self.tunnels[name].enabled = False
            self._save_config()

        return TunnelStatus.STOPPED

    def get_status(self, name: str) -> TunnelStatus:
        """Get the current status of a tunnel."""
        if name not in self._processes:
            return TunnelStatus.STOPPED

        process = self._processes[name]
        if process.poll() is None:
            return TunnelStatus.RUNNING
        else:
            # Process has exited
            del self._processes[name]
            return TunnelStatus.ERROR

    def get_all_tunnels(self) -> list[TunnelConfig]:
        """Get all tunnel configurations."""
        return list(self.tunnels.values())

    def _build_ssh_command(self, config: TunnelConfig) -> list[str]:
        """Build the SSH command for a tunnel."""
        cmd = ["ssh", "-N", "-L"]
        cmd.append(f"{config.local_port}:localhost:{config.remote_port}")

        if config.ssh_key:
            cmd.extend(["-i", config.ssh_key])

        cmd.append(f"{config.remote_user}@{config.remote_host}")
        return cmd

    def stop_all(self) -> None:
        """Stop all running tunnels."""
        for name in list(self._processes.keys()):
            self.stop_tunnel(name)
