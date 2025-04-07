from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QLineEdit, 
                             QPushButton, QMessageBox)
from PyQt5.QtCore import pyqtSignal

class LoginWindow(QWidget):
    login_successful = pyqtSignal(str)
    switch_to_signup = pyqtSignal()

    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Wallet App - Login')
        self.setGeometry(300, 300, 300, 200)

        layout = QVBoxLayout()

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText('Username')
        layout.addWidget(self.username_input)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText('Password')
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)

        login_btn = QPushButton('Login')
        login_btn.clicked.connect(self.attempt_login)
        layout.addWidget(login_btn)

        signup_btn = QPushButton('Sign Up')
        signup_btn.clicked.connect(self.switch_to_signup.emit)
        layout.addWidget(signup_btn)

        self.setLayout(layout)

    def attempt_login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        if not username or not password:
            QMessageBox.warning(self, 'Error', 'Please fill in all fields')
            return

        if self.db_manager.validate_login(username, password):
            self.login_successful.emit(username)
        else:
            QMessageBox.warning(self, 'Login Failed', 'Invalid username or password')
            
            __all__ = ['LoginWindow']