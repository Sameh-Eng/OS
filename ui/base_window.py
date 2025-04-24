from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

class BaseWindow(QWidget):
    """Base window class with logo for all application windows"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_base_ui()
        
    def setup_base_ui(self):
        """Setup the common UI elements (logo and main layout)"""
        # Main vertical layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(15)
        
        # Add logo at top
        self.add_logo()
        
        # Content container (child widgets will add their content here)
        self.content_widget = QWidget()
        self.main_layout.addWidget(self.content_widget)
        
    def add_logo(self):
        """Add the application logo"""
        try:
            self.logo = QLabel()
            pixmap = QPixmap('logo.png')
            if pixmap.isNull():
                raise FileNotFoundError
                
            # Scale logo proportionally (max width 300px)
            self.logo.setPixmap(
                pixmap.scaledToWidth(300, Qt.SmoothTransformation)
            )
            self.logo.setAlignment(Qt.AlignCenter)
            self.logo.setStyleSheet("""
                QLabel {
                    padding: 10px;
                    margin-bottom: 15px;
                }
            """)
            self.main_layout.addWidget(self.logo)
            
        except Exception as e:
            print(f"Error loading logo: {str(e)}")
            # Fallback text if logo fails to load
            self.logo = QLabel("My Wallet App")
            self.logo.setAlignment(Qt.AlignCenter)
            self.logo.setStyleSheet("""
                QLabel {
                    font-size: 24px;
                    font-weight: bold;
                    padding: 15px;
                    color: #2c3e50;
                }
            """)
            self.main_layout.addWidget(self.logo)