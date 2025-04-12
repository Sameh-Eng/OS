from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QTableWidget, QTableWidgetItem, QHeaderView, QInputDialog,
    QLineEdit, QMessageBox, QDialog, QFormLayout
)
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QFont

class SetLogPasswordDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Set Log Password")
        
        self.password = ""
        self.confirm_password = ""
        
        layout = QFormLayout()
        
        self.password_field = QLineEdit()
        self.password_field.setEchoMode(QLineEdit.Password)
        layout.addRow("Password:", self.password_field)
        
        self.confirm_field = QLineEdit()
        self.confirm_field.setEchoMode(QLineEdit.Password)
        layout.addRow("Confirm Password:", self.confirm_field)
        
        buttons_layout = QHBoxLayout()
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept_password)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        
        buttons_layout.addWidget(ok_button)
        buttons_layout.addWidget(cancel_button)
        
        layout.addRow("", buttons_layout)
        self.setLayout(layout)
        
    def accept_password(self):
        self.password = self.password_field.text()
        self.confirm_password = self.confirm_field.text()
        
        if not self.password:
            QMessageBox.warning(self, "Error", "Password cannot be empty")
            return
            
        if len(self.password) < 6:
            QMessageBox.warning(self, "Error", "Password must be at least 6 characters")
            return
            
        if self.password != self.confirm_password:
            QMessageBox.warning(self, "Error", "Passwords do not match")
            return
            
        self.accept()
        
    def get_password(self):
        return self.password

class EnterLogPasswordDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Enter Log Password")
        
        self.password = ""
        
        layout = QFormLayout()
        
        self.password_field = QLineEdit()
        self.password_field.setEchoMode(QLineEdit.Password)
        layout.addRow("Password:", self.password_field)
        
        buttons_layout = QHBoxLayout()
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept_password)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        
        buttons_layout.addWidget(ok_button)
        buttons_layout.addWidget(cancel_button)
        
        layout.addRow("", buttons_layout)
        self.setLayout(layout)
        
    def accept_password(self):
        self.password = self.password_field.text()
        
        if not self.password:
            QMessageBox.warning(self, "Error", "Password cannot be empty")
            return
            
        self.accept()
        
    def get_password(self):
        return self.password

class LogsWindow(QWidget):
    back_to_wallet_signal = pyqtSignal()
    
    def __init__(self, db_manager, username):
        super().__init__()
        self.db_manager = db_manager
        self.username = username
        
        self.init_ui()
        self.check_log_password()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Header
        header_layout = QHBoxLayout()
        title_label = QLabel("Activity Logs")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        
        back_btn = QPushButton("Back to Wallet")
        back_btn.clicked.connect(self.back_to_wallet)
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(back_btn)
        
        layout.addLayout(header_layout)
        
        # Info label
        self.info_label = QLabel("Logs are encrypted and password protected. Set a password to view your logs.")
        layout.addWidget(self.info_label)
        
        # Logs table
        self.logs_table = QTableWidget()
        self.logs_table.setColumnCount(3)
        self.logs_table.setHorizontalHeaderLabels([
            "Timestamp", "Action", "Description"
        ])
        
        # Adjust column widths
        header = self.logs_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        
        layout.addWidget(self.logs_table)
        
        # Button layout
        button_layout = QHBoxLayout()
        
        self.set_password_btn = QPushButton("Set/Change Log Password")
        self.set_password_btn.clicked.connect(self.set_log_password)
        
        self.view_logs_btn = QPushButton("View Logs")
        self.view_logs_btn.clicked.connect(self.view_logs)
        self.view_logs_btn.setEnabled(False)  # Initially disabled until password is set
        
        button_layout.addWidget(self.set_password_btn)
        button_layout.addWidget(self.view_logs_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
    def check_log_password(self):