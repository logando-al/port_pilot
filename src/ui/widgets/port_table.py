"""
PortTableWidget - Searchable table of active ports with kill functionality.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLineEdit, QLabel, QHeaderView, QMessageBox
)
import qtawesome as qta
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

from src.core.port_scanner import PortScanner
from src.core.process_killer import ProcessKiller, KillResult


class PortTableWidget(QWidget):
    """
    Widget displaying active ports in a searchable, filterable table.
    
    Features:
    - Search/filter by port number or process name
    - Quick filter buttons for common port ranges
    - Kill button for each process
    """
    
    def __init__(self, port_scanner: PortScanner, parent=None):
        super().__init__(parent)
        self.port_scanner = port_scanner
        self._setup_ui()
        self.refresh()
    
    def _setup_ui(self):
        """Set up the widget layout."""
        layout = QVBoxLayout(self)
        
        # Search and filter bar
        filter_layout = QHBoxLayout()
        
        # Search box
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search by port or process name...")
        self.search_box.textChanged.connect(self._apply_filter)
        filter_layout.addWidget(self.search_box)
        
        # Quick filter buttons
        filter_layout.addWidget(QLabel("Quick Filters:"))
        
        self.filter_all = QPushButton("All")
        self.filter_all.clicked.connect(lambda: self._quick_filter(None))
        filter_layout.addWidget(self.filter_all)
        
        self.filter_http = QPushButton("HTTP (80/443)")
        self.filter_http.clicked.connect(lambda: self._quick_filter([80, 443, 8080, 8443]))
        filter_layout.addWidget(self.filter_http)
        
        self.filter_dev = QPushButton("Dev (3000/8000)")
        self.filter_dev.clicked.connect(lambda: self._quick_filter([3000, 5000, 8000, 8080, 5173, 5174]))
        filter_layout.addWidget(self.filter_dev)
        
        self.filter_db = QPushButton("DB (5432/3306)")
        self.filter_db.clicked.connect(lambda: self._quick_filter([5432, 3306, 27017, 6379]))
        filter_layout.addWidget(self.filter_db)
        
        layout.addLayout(filter_layout)
        
        # Port table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Local Port", "Address", "PID", "Process Name", "Status", "Action"
        ])
        
        # Configure table
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.setSortingEnabled(True)
        
        layout.addWidget(self.table)
        
        # Refresh button
        refresh_layout = QHBoxLayout()
        refresh_layout.addStretch()
        
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.setIcon(qta.icon('fa5s.sync-alt', color='#e0e0e0'))
        self.refresh_btn.clicked.connect(self.refresh)
        refresh_layout.addWidget(self.refresh_btn)
        
        layout.addLayout(refresh_layout)
        
        self._current_filter = None
    
    def refresh(self):
        """Refresh the port list."""
        self.port_scanner.scan()
        self._populate_table()
    
    def _populate_table(self):
        """Populate the table with port data."""
        ports = self.port_scanner.get_listening_ports()
        
        # Apply quick filter if set
        if self._current_filter:
            ports = [p for p in ports if p.local_port in self._current_filter]
        
        # Apply search filter
        search_text = self.search_box.text().lower()
        if search_text:
            ports = [p for p in ports if 
                     search_text in str(p.local_port) or 
                     search_text in p.process_name.lower()]
        
        self.table.setRowCount(len(ports))
        
        for row, port in enumerate(ports):
            # Port
            port_item = QTableWidgetItem(str(port.local_port))
            port_item.setData(Qt.ItemDataRole.UserRole, port.pid)
            self.table.setItem(row, 0, port_item)
            
            # Address
            self.table.setItem(row, 1, QTableWidgetItem(port.local_address))
            
            # PID
            self.table.setItem(row, 2, QTableWidgetItem(str(port.pid)))
            
            # Process Name
            self.table.setItem(row, 3, QTableWidgetItem(port.process_name))
            
            # Status
            status_item = QTableWidgetItem(port.status)
            if port.status == 'LISTEN':
                status_item.setForeground(QColor("#4CAF50"))
            self.table.setItem(row, 4, status_item)
            
            # Kill button
            kill_btn = QPushButton("Kill")
            kill_btn.setIcon(qta.icon('fa5s.trash-alt', color='white'))
            kill_btn.setStyleSheet("background-color: #c62828; color: white;")
            kill_btn.clicked.connect(lambda _, p=port.pid, n=port.process_name: self._kill_process(p, n))
            self.table.setCellWidget(row, 5, kill_btn)
    
    def _apply_filter(self):
        """Apply search filter."""
        self._populate_table()
    
    def _quick_filter(self, ports):
        """Apply quick filter."""
        self._current_filter = ports
        self._populate_table()
    
    def _kill_process(self, pid: int, name: str):
        """Kill a process after confirmation."""
        reply = QMessageBox.question(
            self,
            "Confirm Kill",
            f"Are you sure you want to kill '{name}' (PID: {pid})?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            result, message = ProcessKiller.kill(pid)
            
            if result == KillResult.SUCCESS:
                QMessageBox.information(self, "Success", message)
                self.refresh()
            elif result == KillResult.ACCESS_DENIED:
                # Offer to run as admin
                admin_reply = QMessageBox.question(
                    self,
                    "Admin Required",
                    f"{message}\n\nWould you like to restart PortPilot with administrator privileges?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No
                )
                if admin_reply == QMessageBox.StandardButton.Yes:
                    from src.utils.platform_utils import request_admin_privileges
                    success, admin_msg = request_admin_privileges()
                    if not success:
                        QMessageBox.warning(self, "Error", admin_msg)
            else:
                QMessageBox.critical(self, "Error", message)
