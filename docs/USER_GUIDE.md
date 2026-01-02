# PortPilot User Guide

## Getting Started

### First Launch

When you first launch PortPilot, it will appear as an icon in your system tray:
- **Windows**: Bottom-right corner of the taskbar
- **macOS**: Top-right menu bar
- **Linux**: System tray (varies by desktop environment)

### System Tray Menu

Right-click the tray icon to see:

1. **🔗 Tunnels** - Quick access to your SSH tunnels
2. **🔌 Active Ports** - Top 10 listening ports
3. **📊 Open Dashboard** - Launch the full interface
4. **🔄 Refresh** - Manually refresh data
5. **❌ Exit** - Close the application

---

## Dashboard

### Active Ports Tab

View all listening network ports on your system:

| Column | Description |
|--------|-------------|
| Local Port | The port number |
| Address | IP address bound to |
| PID | Process ID |
| Process Name | Application name |
| Status | Connection status |
| Action | Kill button |

**Features:**
- **Search**: Filter by port number or process name
- **Quick Filters**: HTTP, Dev, or Database ports
- **Kill**: Click 🗑️ to terminate a process

### Tunnel Manager Tab

Manage SSH tunnels for remote port forwarding:

**Adding a Tunnel:**
1. Click **➕ Add Tunnel**
2. Fill in the form:
   - **Name**: A friendly name
   - **Remote User**: SSH username
   - **Remote Host**: Server address
   - **Local Port**: Port on your machine
   - **Remote Port**: Port on the remote server
   - **SSH Key**: (Optional) Path to private key
3. Click **OK**

**Managing Tunnels:**
- **Start/Stop**: Double-click a tunnel or use the ▶️ button
- **Edit**: Select and click ✏️ Edit
- **Delete**: Select and click 🗑️ Delete

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| F5 | Refresh data |
| Ctrl+Q | Quit application |

---

## Troubleshooting

### "Access Denied" when killing a process

Some system processes require administrator privileges. Try:
- **Windows**: Run as Administrator
- **macOS/Linux**: The app will prompt for sudo password

### Tunnel won't connect

1. Verify SSH credentials are correct
2. Ensure the remote host is reachable
3. Check if the local port is already in use
4. Verify SSH key permissions (should be 600)

### App doesn't start

1. Check if another instance is running
2. Delete config files: `~/.portpilot/` and restart

---

## Configuration

Settings are stored in:
- **Windows**: `%USERPROFILE%\.portpilot\`
- **macOS/Linux**: `~/.portpilot/`

Files:
- `config.json` - Application settings
- `tunnels.json` - Saved tunnel configurations
