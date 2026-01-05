"""
Splash Screen module - Modern loading screen for PortPilot.
"""

from pathlib import Path

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor, QFont, QIcon, QPainter, QPainterPath, QPixmap
from PyQt6.QtWidgets import QLabel, QProgressBar, QSplashScreen, QVBoxLayout, QWidget

from src.core.version import VERSION


class SplashScreen(QWidget):
    """
    Modern splash screen with logo, app name, and loading indicator.
    
    Features a dark tech theme matching the main application.
    """
    
    def __init__(self):
        super().__init__()
        self._setup_window()
        self._setup_ui()
        self._start_animation()
    
    def _setup_window(self):
        """Configure window properties."""
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.SplashScreen
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(400, 300)
        
        # Center on screen
        screen = self.screen().geometry()
        self.move(
            (screen.width() - self.width()) // 2,
            (screen.height() - self.height()) // 2
        )
    
    def _setup_ui(self):
        """Create the splash screen UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 40, 30, 30)
        layout.setSpacing(15)
        
        # Logo/Icon
        icon_label = QLabel()
        icon_path = Path(__file__).parent.parent.parent / "resources" / "icons" / "tray_icon.png"
        if icon_path.exists():
            pixmap = QPixmap(str(icon_path))
            scaled_pixmap = pixmap.scaled(
                80, 80, 
                Qt.AspectRatioMode.KeepAspectRatio, 
                Qt.TransformationMode.SmoothTransformation
            )
            icon_label.setPixmap(scaled_pixmap)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon_label)
        
        # App Name
        name_label = QLabel("PortPilot")
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name_label.setStyleSheet("""
            QLabel {
                color: #00d4ff;
                font-size: 32px;
                font-weight: 700;
                font-family: 'Inter', 'Segoe UI', sans-serif;
                letter-spacing: 2px;
            }
        """)
        layout.addWidget(name_label)
        
        # Version
        version_label = QLabel(f"v{VERSION}")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        version_label.setStyleSheet("""
            QLabel {
                color: #7a7a8c;
                font-size: 14px;
                font-weight: 500;
            }
        """)
        layout.addWidget(version_label)
        
        # Spacer
        layout.addStretch()
        
        # Loading text
        self.status_label = QLabel("Initializing...")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("""
            QLabel {
                color: #a0a0b0;
                font-size: 12px;
            }
        """)
        layout.addWidget(self.status_label)
        
        # Progress bar
        self.progress = QProgressBar()
        self.progress.setTextVisible(False)
        self.progress.setFixedHeight(4)
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setStyleSheet("""
            QProgressBar {
                background-color: rgba(255, 255, 255, 0.1);
                border: none;
                border-radius: 2px;
            }
            QProgressBar::chunk {
                background-color: #00d4ff;
                border-radius: 2px;
            }
        """)
        layout.addWidget(self.progress)
    
    def paintEvent(self, event):
        """Paint the rounded background."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Create rounded rectangle path
        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width(), self.height(), 16, 16)
        
        # Fill with dark background
        painter.fillPath(path, QColor(10, 10, 15, 245))
        
        # Draw subtle border
        painter.setPen(QColor(0, 212, 255, 60))
        painter.drawPath(path)
    
    def _start_animation(self):
        """Start the loading animation."""
        self.progress_value = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self._update_progress)
        self.timer.start(30)
    
    def _update_progress(self):
        """Update the progress bar."""
        self.progress_value += 2
        self.progress.setValue(min(self.progress_value, 100))
        
        # Update status text
        if self.progress_value < 30:
            self.status_label.setText("Initializing...")
        elif self.progress_value < 60:
            self.status_label.setText("Loading modules...")
        elif self.progress_value < 90:
            self.status_label.setText("Starting services...")
        else:
            self.status_label.setText("Ready!")
        
        if self.progress_value >= 100:
            self.timer.stop()
    
    def set_status(self, text: str):
        """Update the status text."""
        self.status_label.setText(text)
    
    def set_progress(self, value: int):
        """Set the progress value (0-100)."""
        self.progress.setValue(min(max(value, 0), 100))
