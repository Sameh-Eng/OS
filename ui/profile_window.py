# ui/profile_window.py
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon, QFont

class ProfileWindow(QDialog):
    logout_requested = pyqtSignal()
    
    def __init__(self, username, email, parent=None):
        super().__init__(parent)
        self.username = username
        self.email = email
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle("Profile Settings")
        self.setFixedSize(400, 500)
        self.setStyleSheet(self._get_stylesheet())
        self._create_layout()
        
    def _get_stylesheet(self):
        return """
            QDialog {
                background-color: #ffffff;
                border-radius: 15px;
            }
            QLabel {
                color: #333333;
            }
            QPushButton {
                border: none;
                padding: 15px;
                text-align: left;
                font-size: 16px;
                background-color: #ffffff;
            }
            QPushButton:hover {
                background-color: #f5f5f5;
            }
        """
        
    def _create_layout(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Add components
        main_layout.addLayout(self._create_header())
        main_layout.addLayout(self._create_sections())
        main_layout.addLayout(self._create_footer())
        
        self.setLayout(main_layout)
        
    def _create_header(self):
        header_layout = QVBoxLayout()
        
        # Profile Icon
        icon_label = QLabel()
        icon_label.setPixmap(QIcon(":/icons/profile.png").pixmap(80, 80))
        icon_label.setAlignment(Qt.AlignCenter)
        
        # Username
        username_label = QLabel(self.username)
        username_label.setFont(QFont("Arial", 16, QFont.Bold))
        username_label.setAlignment(Qt.AlignCenter)
        
        # Email
        email_label = QLabel(self.email)
        email_label.setFont(QFont("Arial", 12))
        email_label.setStyleSheet("color: #666666;")
        email_label.setAlignment(Qt.AlignCenter)
        
        header_layout.addWidget(icon_label)
        header_layout.addWidget(username_label)
        header_layout.addWidget(email_label)
        
        return header_layout
        
    def _create_sections(self):
        sections_layout = QVBoxLayout()
        
        sections = [
            ("Personal Details", ":/icons/person.png"),
            ("Security", ":/icons/security.png"),
            ("Privacy", ":/icons/privacy.png"),
            ("Support", ":/icons/support.png")
        ]
        
        for text, icon in sections:
            btn = self._create_section_button(text, icon)
            sections_layout.addWidget(btn)
            
        return sections_layout
        
    def _create_section_button(self, text, icon_path):
        btn = QPushButton(text)
        btn.setIcon(QIcon(icon_path))
        btn.setIconSize(btn.iconSize())
        btn.setCursor(Qt.PointingHandCursor)
        return btn
        
    def _create_footer(self):
        footer_layout = QHBoxLayout()
        
        # Logout Button
        logout_btn = QPushButton("Logout")
        logout_btn.setStyleSheet(self._get_logout_style())
        logout_btn.clicked.connect(self._handle_logout)
        
        # Rate Button
        rate_btn = QPushButton("Rate App")
        rate_btn.setStyleSheet(self._get_rate_style())
        rate_btn.clicked.connect(self._handle_rate)
        
        footer_layout.addWidget(logout_btn)
        footer_layout.addWidget(rate_btn)
        
        return footer_layout
        
    def _get_logout_style(self):
        return """
            QPushButton {
                color: #ffffff;
                background-color: #ff4444;
                border-radius: 8px;
                padding: 12px 25px;
            }
            QPushButton:hover {
                background-color: #cc0000;
            }
        """
        
    def _get_rate_style(self):
        return """
            QPushButton {
                color: #ffffff;
                background-color: #4CAF50;
                border-radius: 8px;
                padding: 12px 25px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """
        
    def _handle_logout(self):
        self.logout_requested.emit()
        self.close()
        
    def _handle_rate(self):
        # Implement rating functionality
        pass