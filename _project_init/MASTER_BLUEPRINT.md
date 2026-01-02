# Project: PortPilot
> A system tray utility to visualize local ports, kill blocking processes, and manage SSH tunnels.
---
## 1. The Strategy
| Aspect | Detail |
|--------|--------|
| **Pitch** | A system tray app that visualizes every active port, offers one-click process killing, and manages SSH tunnels to solve "Port already in use" friction. |
| **Target User** | Developers, DevOps Engineers, and System Admins. |
| **Monetization** | Portfolio Flex (Primary) / Open Source / Potential "Pro" version with cloud sync. |
| **Key Value** | Saves time typing `lsof -i :8000` and `kill -9`. Visualizes the invisible network layer. |
---
## 2. Tech Architecture
### Stack
| Component | Technology |
|-----------|------------|
| **Language** | Python 3.13 |
| **GUI Framework** | PyQt6 (System Tray focus) |
| **System Monitor** | `psutil` (Cross-platform process/socket handling) |
| **Tunnels** | `subprocess` (calling System SSH client) |
| **Packaging** | PyInstaller (→ `.exe`) |
### Core Modules
1.  **PortScanner**: Runs on a background thread (QThread). Uses `psutil.net_connections()` to map `port` -> `pid` -> `process_name`.
2.  **ProcessKiller**: Wrapper around `psutil.Process(pid).kill()`. Handles permission errors gracefully (Admin rights may be needed).
3.  **TunnelManager**: Manages persistent SSH tunnel configurations and their subprocess states.
4.  **TrayIcon**: The main UI entry point. Updates icon state based on active tunnels/critical ports.
5.  **Auto Update**: Checks for updates on app startup and update using github releases. 
---
## 3. UX Vision
### Vibe
> **Technical • Dense • Functional**
### Key Views
#### 1. The "Quick Glance" (Tray Menu)
*   **Right-click System Tray**:
    *   Creates a context menu.
    *   Top section: "Active Tunnels" (Green dot = On, Grey dot = Off).
    *   Middle section: "Top Active Ports" (e.g., `8000: python`, `3000: node`).
    *   Bottom section: "Open PortPilot Dashboard", "Exit".
#### 2. The Dashboard (Main Window)
*   **Active Ports Tab**:
    *   A searchable table: `Local Port` | `PID` | `Process Name` | `Status` | `Actions`.
    *   **Action**: A red 🗑️ (Trash/Kill) button next to every row.
    *   **Filter**: Quick buttons for "HTTP (80/443)", "Dev (3000/8000/8080)", "DB (5432/3306)".
*   **Tunnel Manager Tab**:
    *   List of saved tunnels.
    *   "Add Tunnel" Form: `Name`, `Remote User`, `Remote Host`, `Local Port`, `Remote Port`.
    *   Toggle Switch: ON/OFF.
### User Story (Happy Path)
1.  **Scenario**: User tries to run a Django server but mapped port 8000 is taken.
2.  **Action**: User clicks the **PortPilot** tray icon.
3.  **Visual**: The dashboard opens. User types "8000" in the filter.
4.  **Result**: Shows `8000 -> python.exe (PID: 12345)`.
5.  **Resolution**: User clicks the red **Trash Can** icon.
6.  **Success**: PID 12345 dies. User restarts their server. Success!
---
## 4. Development Phases
### Phase 1: The killer (MVP)
*   [ ] System Tray integration (PyQt6 `QSystemTrayIcon`).
*   [ ] `psutil` integration to list listening TCP ports + Process Names.
*   [ ] UI Table to display this data.
*   [ ] "Kill Process" functionality.
### Phase 2: The Tunneler
*   [ ] UI for adding/saving SSH tunnel configs (saved to `tunnels.json`).
*   [ ] Subprocess logic to start/stop `ssh -L` commands.
*   [ ] Visual indicators for tunnel status.
### Phase 3: Polish & Portfolio
*   [ ] Auto-refresh (polling interval).
*   [ ] Admin privilege prompts (if needed for killing system processes).
*   [ ] Dark Mode styling.
*   [ ] Packaging as a standalone `.exe`.
---
## 5. Next Steps
1.  **Initialize Project**: Create `portpilot/` directory.
2.  **Dependencies**: Install `PyQt6` and `psutil`.
3.  **Hello World**: Get a System Tray icon to appear.
**Ready to start?** 🚀