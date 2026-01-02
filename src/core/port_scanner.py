"""
PortScanner module - Maps ports to processes using psutil.
"""

from dataclasses import dataclass

import psutil


@dataclass
class PortInfo:
    """Information about a network port and its associated process."""
    local_port: int
    local_address: str
    remote_port: int | None
    remote_address: str | None
    pid: int
    process_name: str
    status: str
    protocol: str  # 'tcp' or 'udp'


class PortScanner:
    """
    Scans and maps active network ports to their processes.

    Uses psutil.net_connections() to get port-to-PID mappings,
    then resolves PIDs to process names.
    """

    def __init__(self) -> None:
        self._cache: list[PortInfo] = []

    def scan(self) -> list[PortInfo]:
        """
        Scan all active network connections and return port information.

        Returns:
            List of PortInfo objects for all listening/established connections.
        """
        ports = []

        try:
            connections = psutil.net_connections(kind='inet')

            for conn in connections:
                # Skip connections without local address
                if not conn.laddr:
                    continue

                # Get process name
                process_name = self._get_process_name(conn.pid)

                port_info = PortInfo(
                    local_port=conn.laddr.port,
                    local_address=conn.laddr.ip,
                    remote_port=conn.raddr.port if conn.raddr else None,
                    remote_address=conn.raddr.ip if conn.raddr else None,
                    pid=conn.pid or 0,
                    process_name=process_name,
                    status=conn.status,
                    protocol='tcp' if conn.type == 1 else 'udp'
                )
                ports.append(port_info)

        except psutil.AccessDenied:
            # May need admin privileges on some systems
            pass
        except Exception as e:
            print(f"Error scanning ports: {e}")

        self._cache = ports
        return ports

    def get_cached(self) -> list[PortInfo]:
        """Return the last scanned port list."""
        return self._cache

    def find_by_port(self, port: int) -> list[PortInfo]:
        """Find all connections using a specific port."""
        return [p for p in self._cache if p.local_port == port]

    def find_by_process(self, name: str) -> list[PortInfo]:
        """Find all connections for a process name (case-insensitive)."""
        name_lower = name.lower()
        return [p for p in self._cache if name_lower in p.process_name.lower()]

    def get_listening_ports(self) -> list[PortInfo]:
        """Get only ports in LISTEN status."""
        return [p for p in self._cache if p.status == 'LISTEN']

    def _get_process_name(self, pid: int | None) -> str:
        """Get process name from PID."""
        if not pid:
            return "Unknown"
        try:
            proc = psutil.Process(pid)
            return proc.name()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return "Unknown"
