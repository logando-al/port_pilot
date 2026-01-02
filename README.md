# PortPilot 🚀

> A system tray utility to visualize local ports, kill blocking processes, and manage SSH tunnels.

[![CI](https://github.com/logando-al/port_pilot/actions/workflows/ci.yml/badge.svg)](https://github.com/logando-al/port_pilot/actions/workflows/ci.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## ✨ Features

- **🔌 Port Visualization** - See all active ports and their associated processes at a glance
- **🗑️ One-Click Kill** - Terminate processes blocking your ports instantly
- **🔗 SSH Tunnel Manager** - Create, save, and manage SSH tunnels with visual status indicators
- **🖥️ System Tray** - Runs quietly in your system tray with quick access menus
- **🌙 Dark Mode** - Beautiful dark theme for comfortable viewing
- **🔄 Auto-Update** - Automatic update checks from GitHub releases

## 📥 Installation

### From Releases (Recommended)

Download the latest release for your platform:
- **Windows**: `PortPilot-Setup.exe`
- **macOS**: `PortPilot.dmg`
- **Linux**: `PortPilot.AppImage`

### From Source

```bash
# Clone the repository
git clone https://github.com/logando-al/port_pilot.git
cd port_pilot

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Run the application
python src/main.py
```

## 🚀 Usage

1. **Launch PortPilot** - The app starts minimized in your system tray
2. **Right-click the tray icon** to see:
   - Active SSH tunnels
   - Top listening ports
   - Quick actions
3. **Double-click** to open the full dashboard
4. **Kill processes** by clicking the 🗑️ button next to any port
5. **Manage tunnels** in the Tunnel Manager tab

## 🛠️ Development

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run tests
pytest tests/ -v

# Run linting
ruff check src/ tests/

# Type checking
mypy src/

# Build executable
pyinstaller --onefile --windowed src/main.py
```

## 📁 Project Structure

```
portpilot/
├── src/
│   ├── core/           # Business logic
│   ├── ui/             # PyQt6 UI components
│   └── utils/          # Utilities and helpers
├── tests/              # Unit and integration tests
├── .github/workflows/  # CI/CD pipelines
└── scripts/            # Build scripts
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [PyQt6](https://www.riverbankcomputing.com/software/pyqt/)
- Process monitoring via [psutil](https://github.com/giampaolo/psutil)
