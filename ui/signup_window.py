from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QLineEdit, 
                             QPushButton, QMessageBox)
from PyQt5.QtCore import pyqtSignal

class SignupWindow(QWidget):
    signup_successful = pyqtSignal(str)
    switch_to_login = pyqtSignal()

    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Wallet App - Sign Up')
        self.setGeometry(300, 300, 300, 200)

        layout = QVBoxLayout()

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText('Choose Username')
        layout.addWidget(self.username_input)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText('Choose Password')
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)

        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setPlaceholderText('Confirm Password')
        self.confirm_password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.confirm_password_input)

        signup_btn = QPushButton('Create Account')
        signup_btn.clicked.connect(self.attempt_signup)
        layout.addWidget(signup_btn)

        login_btn = QPushButton('Back to Login')
        login_btn.clicked.connect(self.switch_to_login.emit)
        layout.addWidget(login_btn)

        self.setLayout(layout)

    def attempt_signup(self):
        username = self.username_input.text()
        password = self.password_input.text()
        confirm_password = self.confirm_password_input.text()

        # Validation checks
        if not username or not password or not confirm_password:
            QMessageBox.warning(self, 'Error', 'Please fill in all fields')
            return

        if password != confirm_password:
            QMessageBox.warning(self, 'Error', 'Passwords do not match')
            return

        if len(password) < 6:
            QMessageBox.warning(self, 'Error', 'Password must be at least 6 characters')
            return

        # Attempt to register user
        wallet_id = self.db_manager.register_user(username, password)
        if wallet_id:
            QMessageBox.information(self, 'Success', f'Account created!\nYour Wallet ID is: {wallet_id}')
            self.signup_successful.emit(username)
        else:
            QMessageBox.warning(self, 'Error', 'Username already exists')

# Ensure the class is explicitly exported
__all__ = ['SignupWindow']