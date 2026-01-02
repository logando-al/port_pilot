"""
ProcessKiller module - Safely terminates processes by PID.
"""

from enum import Enum

import psutil


class KillResult(Enum):
    """Result of a process kill attempt."""
    SUCCESS = "success"
    NOT_FOUND = "not_found"
    ACCESS_DENIED = "access_denied"
    ERROR = "error"


class ProcessKiller:
    """
    Handles process termination with proper error handling.

    Attempts graceful termination first, then force kills if needed.
    Handles permission errors gracefully (admin rights may be required).
    """

    @staticmethod
    def kill(pid: int, force: bool = False) -> tuple[KillResult, str]:
        """
        Terminate a process by PID.

        Args:
            pid: Process ID to terminate.
            force: If True, use SIGKILL immediately. Otherwise try SIGTERM first.

        Returns:
            Tuple of (KillResult, message string).
        """
        try:
            process = psutil.Process(pid)
            process_name = process.name()

            if force:
                process.kill()  # SIGKILL
            else:
                process.terminate()  # SIGTERM

                # Wait briefly for graceful termination
                try:
                    process.wait(timeout=3)
                except psutil.TimeoutExpired:
                    # Force kill if still running
                    process.kill()
                    process.wait(timeout=2)

            return (KillResult.SUCCESS, f"Successfully terminated {process_name} (PID: {pid})")

        except psutil.NoSuchProcess:
            return (KillResult.NOT_FOUND, f"Process with PID {pid} not found")

        except psutil.AccessDenied:
            return (KillResult.ACCESS_DENIED,
                    f"Access denied. Admin privileges may be required to kill PID {pid}")

        except Exception as e:
            return (KillResult.ERROR, f"Error killing process {pid}: {str(e)}")

    @staticmethod
    def is_running(pid: int) -> bool:
        """Check if a process is still running."""
        try:
            process = psutil.Process(pid)
            return bool(process.is_running())
        except psutil.NoSuchProcess:
            return False

    @staticmethod
    def get_process_info(pid: int) -> dict:
        """Get detailed information about a process."""
        try:
            process = psutil.Process(pid)
            return {
                "pid": pid,
                "name": process.name(),
                "status": process.status(),
                "create_time": process.create_time(),
                "cmdline": process.cmdline(),
                "username": process.username(),
            }
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return {"pid": pid, "error": "Unable to get process info"}
