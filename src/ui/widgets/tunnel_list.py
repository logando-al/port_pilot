"""
TunnelListWidget - Manage SSH tunnel configurations.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QPushButton, QDialog, QFormLayout, QLineEdit, QSpinBox,
    QDialogButtonBox, QLabel, QMessageBox
)
import qtawesome as qta
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

from src.core.tunnel_manager import TunnelManager, TunnelConfig, TunnelStatus


class TunnelDialog(QDialog):
    """Dialog for adding/editing a tunnel."""
    
    def __init__(self, tunnel: TunnelConfig = None, parent=None):
        super().__init__(parent)
        self.tunnel = tunnel
        self.setWindowTitle("Edit Tunnel" if tunnel else "Add Tunnel")
        self.setMinimumWidth(400)
        self._setup_ui()
        if tunnel:
            self._populate_fields()
    
    def _setup_ui(self):
        layout = QFormLayout(self)
        
        self.name_input = QLineEdit()
        layout.addRow("Name:", self.name_input)
        
        self.user_input = QLineEdit()
        layout.addRow("Remote User:", self.user_input)
        
        self.host_input = QLineEdit()
        layout.addRow("Remote Host:", self.host_input)
        
        self.local_port_input = QSpinBox()
        self.local_port_input.setRange(1, 65535)
        self.local_port_input.setValue(8080)
        layout.addRow("Local Port:", self.local_port_input)
        
        self.remote_port_input = QSpinBox()
        self.remote_port_input.setRange(1, 65535)
        self.remote_port_input.setValue(80)
        layout.addRow("Remote Port:", self.remote_port_input)
        
        self.ssh_key_input = QLineEdit()
        self.ssh_key_input.setPlaceholderText("Optional: /path/to/key")
        layout.addRow("SSH Key:", self.ssh_key_input)
        
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)
    
    def _populate_fields(self):
        self.name_input.setText(self.tunnel.name)
        self.name_input.setReadOnly(True)
        self.user_input.setText(self.tunnel.remote_user)
        self.host_input.setText(self.tunnel.remote_host)
        self.local_port_input.setValue(self.tunnel.local_port)
        self.remote_port_input.setValue(self.tunnel.remote_port)
        if self.tunnel.ssh_key:
            self.ssh_key_input.setText(self.tunnel.ssh_key)
    
    def get_config(self) -> TunnelConfig:
        return TunnelConfig(
            name=self.name_input.text(),
            remote_user=self.user_input.text(),
            remote_host=self.host_input.text(),
            local_port=self.local_port_input.value(),
            remote_port=self.remote_port_input.value(),
            ssh_key=self.ssh_key_input.text() or None
        )


class TunnelListWidget(QWidget):
    """Widget for managing SSH tunnel configurations."""
    
    def __init__(self, tunnel_manager: TunnelManager, parent=None):
        super().__init__(parent)
        self.tunnel_manager = tunnel_manager
        self._setup_ui()
        self.refresh()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Tunnel list
        self.list_widget = QListWidget()
        self.list_widget.itemDoubleClicked.connect(self._toggle_tunnel)
        layout.addWidget(self.list_widget)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        self.add_btn = QPushButton("Add Tunnel")
        self.add_btn.setIcon(qta.icon('fa5s.plus-circle', color='#4CAF50'))
        self.add_btn.clicked.connect(self._add_tunnel)
        btn_layout.addWidget(self.add_btn)
        
        self.edit_btn = QPushButton("Edit")
        self.edit_btn.setIcon(qta.icon('fa5s.edit', color='#2196F3'))
        self.edit_btn.clicked.connect(self._edit_tunnel)
        btn_layout.addWidget(self.edit_btn)
        
        self.delete_btn = QPushButton("Delete")
        self.delete_btn.setIcon(qta.icon('fa5s.trash-alt', color='#f44336'))
        self.delete_btn.clicked.connect(self._delete_tunnel)
        btn_layout.addWidget(self.delete_btn)
        
        btn_layout.addStretch()
        
        self.toggle_btn = QPushButton("Start")
        self.toggle_btn.setIcon(qta.icon('fa5s.play-circle', color='#4CAF50'))
        self.toggle_btn.clicked.connect(self._toggle_selected)
        btn_layout.addWidget(self.toggle_btn)
        
        layout.addLayout(btn_layout)
    
    def refresh(self):
        self.list_widget.clear()
        for tunnel in self.tunnel_manager.get_all_tunnels():
            status = self.tunnel_manager.get_status(tunnel.name)
            status_text = "[ON]" if status == TunnelStatus.RUNNING else "[OFF]"
            item = QListWidgetItem(
                f"{status_text} {tunnel.name} | {tunnel.local_port} -> "
                f"{tunnel.remote_user}@{tunnel.remote_host}:{tunnel.remote_port}"
            )
            item.setData(Qt.ItemDataRole.UserRole, tunnel.name)
            self.list_widget.addItem(item)
    
    def _add_tunnel(self):
        dialog = TunnelDialog(parent=self)
        if dialog.exec():
            config = dialog.get_config()
            if self.tunnel_manager.add_tunnel(config):
                self.refresh()
            else:
                QMessageBox.warning(self, "Error", "Tunnel name already exists.")
    
    def _edit_tunnel(self):
        item = self.list_widget.currentItem()
        if not item:
            return
        name = item.data(Qt.ItemDataRole.UserRole)
        tunnel = self.tunnel_manager.tunnels.get(name)
        if tunnel:
            dialog = TunnelDialog(tunnel, parent=self)
            if dialog.exec():
                self.tunnel_manager.update_tunnel(name, dialog.get_config())
                self.refresh()
    
    def _delete_tunnel(self):
        item = self.list_widget.currentItem()
        if not item:
            return
        name = item.data(Qt.ItemDataRole.UserRole)
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Delete tunnel '{name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.tunnel_manager.remove_tunnel(name)
            self.refresh()
    
    def _toggle_selected(self):
        item = self.list_widget.currentItem()
        if item:
            self._toggle_tunnel(item)
    
    def _toggle_tunnel(self, item):
        name = item.data(Qt.ItemDataRole.UserRole)
        status = self.tunnel_manager.get_status(name)
        if status == TunnelStatus.RUNNING:
            self.tunnel_manager.stop_tunnel(name)
        else:
            self.tunnel_manager.start_tunnel(name)
        self.refresh()
