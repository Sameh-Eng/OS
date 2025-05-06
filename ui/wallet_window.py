from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, 
                             QMessageBox, QHBoxLayout, QLineEdit, QDialog, 
                             QFormLayout,QApplication, QListWidget)
from PyQt5.QtGui import QIcon, QFont, QPixmap
from PyQt5.QtCore import pyqtSignal, Qt, QSize
from ui.base_window import BaseWindow
from secure_logger import SecureLogger
from .profile_window import ProfileWindow
class TransactionWindow(QWidget):
    def __init__(self,image_path,title, db_manager, username,message, parent=None): 
        super().__init__(parent)
        self.db_manager = db_manager
        self.username = username
        self.setWindowTitle("Transaction History")
        self.resize(500, 400)
        self.init_ui()
        layout = QVBoxLayout()
        image_label = QLabel()
        pixmap = QPixmap(image_path).scaled(200, 200, Qt.KeepAspectRatio)
        image_label.setPixmap(pixmap)
        image_label.setAlignment(Qt.AlignCenter)
        message_label = QLabel(message)
        message_label.setAlignment(Qt.AlignCenter)
        message_label.setStyleSheet("font-size: 16px; margin: 20px 0;")
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        
        layout.addWidget(image_label)
        layout.addWidget(message_label)
        layout.addWidget(close_btn)
        self.setLayout(layout)
    def init_ui(self):
        layout = QVBoxLayout()
        
        # PIN Entry
        self.pin_label = QLabel("Enter your PIN to view transactions:")
        self.pin_input = QLineEdit()
        self.pin_input.setEchoMode(QLineEdit.Password)
        self.pin_input.setMaxLength(4)
        
        self.submit_button = QPushButton("View Transactions")
        self.submit_button.clicked.connect(self.verify_and_show)
        
        # Transaction List
        self.transaction_list = QListWidget()
        
        layout.addWidget(self.pin_label)
        layout.addWidget(self.pin_input)
        layout.addWidget(self.submit_button)
        layout.addWidget(self.transaction_list)
        
        self.setLayout(layout)
    
    def verify_and_show(self):
        pin = self.pin_input.text()
        if self.db_manager.verify_pin(self.username, pin):
            self.load_transactions()
        else:
            QMessageBox.warning(self, "Error", "Incorrect PIN!")
    
    def load_transactions(self):
        self.transaction_list.clear()
        transactions = self.db_manager.get_transaction_history(self.username)
    
        if not transactions:
            self.transaction_list.addItem("No transactions found")
            return
    
        for t in transactions:
        # t[0]=sender, t[1]=recipient, t[2]=amount, t[3]=timestamp, t[4]=type
            if t[4] == 'Sent':
                text = f"{t[3]} | Sent ${t[2]:.2f} to {t[1]}"
            else:
                text = f"{t[3]} | Received ${t[2]:.2f} from {t[0]}"
        
        self.transaction_list.addItem(text)
class SendMoneyDialog(QDialog):
    def __init__(self, db_manager, sender_username, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.sender_username = sender_username
        self.setWindowTitle('Send Money')
        self.init_ui()

    def init_ui(self):
        layout = QFormLayout()

        # Recipient Wallet ID
        self.recipient_input = QLineEdit()
        self.recipient_input.setPlaceholderText('Enter recipient\'s wallet ID')
        layout.addRow('Recipient Wallet ID:', self.recipient_input)

        # Amount Input
        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText('Enter amount to send')
        layout.addRow('Amount:', self.amount_input)

        # Send Button
        send_btn = QPushButton('Send Money')
        send_btn.clicked.connect(self.send_money)
        layout.addRow(send_btn)

        self.setLayout(layout)

    def send_money(self):
        recipient_wallet = self.recipient_input.text().strip()
        
        try:
            amount = float(self.amount_input.text())
            if amount <= 0:
                raise ValueError("Amount must be greater than zero")
                
            recipient_username = self.db_manager.get_username_by_wallet_id(recipient_wallet)
            if not recipient_username:
                raise ValueError("Wallet not found")

            # Confirm transaction
            confirm = QMessageBox.question(
                self,
                "Confirm Transfer",
                f"Send ${amount:.2f} to {recipient_username} ({recipient_wallet})?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if confirm == QMessageBox.Yes:
                # Perform transaction
                self.db_manager.send_money(
                    self.sender_username,
                    recipient_wallet,
                    amount
                )
                
                # Show success dialog
                TransactionResultDialog(
                    image_path="sucsses.png",
                    #"Transaction Successful",
                    message=f"You have sent ${amount:.2f}\nto {recipient_username}",
                    parent=self
                ).exec_()
                
                self.accept()

        except ValueError as ve:
            TransactionResultDialog(
                image_path="failure.jpg",
                title="Error",
                message="Transaction failed!",
                parent=self
            ).exec_()
        except Exception as e:
            TransactionResultDialog(
                "fialure.png",
                "Transaction Failed",
                f"An error occurred:\n{str(e)}",
                self
            ).exec_()
class ReceiveMoneyDialog(QDialog):
    def __init__(self, db_manager, username):
      super().__init__()
      self.db_manager = db_manager
      self.username = username
    # Get wallet info immediately
      self.wallet_id, _ = self.db_manager.get_user_wallet_info(self.username)  # Add this line
      self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Display Wallet ID for receiving
        wallet_label = QLabel(f'Your Wallet ID: {self.wallet_id}')
        layout.addWidget(wallet_label)

        info_label = QLabel('Share this Wallet ID to receive money.')
        layout.addWidget(info_label)

        self.setLayout(layout)

class TransactionResultDialog(QDialog):
    def __init__(self, image_path, title, message, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(400, 300)
        layout = QVBoxLayout()

        image_label = QLabel()
        pixmap = QPixmap(image_path).scaled(150, 150, Qt.KeepAspectRatio)
        image_label.setPixmap(pixmap)
        image_label.setAlignment(Qt.AlignCenter)

        message_label = QLabel(message)
        message_label.setAlignment(Qt.AlignCenter)
        message_label.setStyleSheet("font-size: 14px; margin: 20px 0;")

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)

        layout.addWidget(image_label)
        layout.addWidget(message_label)
        layout.addWidget(close_btn)
        self.setLayout(layout)

class WalletWindow(QWidget):
    logout_signal = pyqtSignal()

    def __init__(self, db_manager, username):
        super().__init__()
        self.db_manager = db_manager
        self.username = username
        self.logger = SecureLogger("wallet_ui")
        self.logger.log(f"Wallet opened for {username}")
        
        # Get wallet info immediately and store it
        wallet_info = self.db_manager.get_user_wallet_info(self.username)
        self.wallet_id, self.balance = wallet_info
        self.init_ui()
        # Create header layout for profile button
        self.header_layout = QHBoxLayout()
        self.header_layout.addStretch()  # Push button to the right
        self.add_profile_button()

    def init_ui(self):
        self.setWindowTitle('Wallet App - My Wallet')
        self.setGeometry(300, 300, 400, 350)
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Create header layout for profile button
        header_layout = QHBoxLayout()
        header_layout.addStretch()  # Push button to the right
        #add_profile_button()
        # Wallet Information
        wallet_info_layout = QVBoxLayout()
        self.balance_label = QLabel(f'Balance: ${self.balance:.2f}')
        self.balance_label.setFont(QFont('Arial', 18, QFont.Bold))
        self.balance_label.setAlignment(Qt.AlignCenter)
        
        wallet_id_label = QLabel(f'Wallet ID: {self.wallet_id}')
        wallet_id_label.setStyleSheet("color: #666; font-size: 12px;")
        wallet_id_label.setAlignment(Qt.AlignCenter)

        # Money Code Redemption Section
        code_layout = QHBoxLayout()
        self.code_input = QLineEdit()
        self.code_input.setPlaceholderText('Enter Money Code')
        redeem_btn = QPushButton('Redeem Code')
        redeem_btn.clicked.connect(self.redeem_money_code)
        code_layout.addWidget(self.code_input)
        code_layout.addWidget(redeem_btn)

        # Action Buttons
        btn_layout = QHBoxLayout()
        send_btn = QPushButton('Send Money')
        send_btn.clicked.connect(self.open_send_money_dialog)
        receive_btn = QPushButton('Receive Money')
        receive_btn.clicked.connect(self.open_receive_money_dialog)
        btn_layout.addWidget(send_btn)
        btn_layout.addWidget(receive_btn)

        # Bottom Buttons
        bottom_layout = QHBoxLayout()
        self.copy_button = QPushButton("Copy Wallet ID")
        self.copy_button.clicked.connect(self.copy_wallet_id)
        self.history_button = QPushButton("View Transactions")
        self.history_button.clicked.connect(self.show_transaction_history)
        logout_btn = QPushButton('Logout')
        logout_btn.clicked.connect(self.logout)
        bottom_layout.addWidget(self.history_button)
        bottom_layout.addWidget(self.copy_button)
        bottom_layout.addWidget(logout_btn)

        # Assemble layout
        main_layout.addLayout(header_layout)
        wallet_info_layout.addWidget(self.balance_label)
        wallet_info_layout.addWidget(wallet_id_label)
        main_layout.addLayout(wallet_info_layout)
        main_layout.addLayout(code_layout)
        main_layout.addLayout(btn_layout)
        main_layout.addLayout(bottom_layout)
        self.setLayout(main_layout)

    def add_profile_button(self):
        # Create profile button with proper styling
        self.profile_btn = QPushButton()
        self.profile_btn.setIcon(QIcon(":/icons/profile.png"))
        self.profile_btn.setIconSize(QSize(32, 32))
        self.profile_btn.setFixedSize(40, 40)
        self.profile_btn.setStyleSheet("""
            QPushButton {
                border: none;
                border-radius: 20px;
                background-color: transparent;
            }
            QPushButton:hover {
                background-color: #f0f0f0;
            }
        """)
        self.profile_btn.setCursor(Qt.PointingHandCursor)
        self.profile_btn.clicked.connect(self.show_profile)
        
        # Add to header layout
        self.layout().itemAt(0).layout().addWidget(self.profile_btn)

    def show_profile(self):
        user_data = self.db_manager.get_user_data(self.username)
        if user_data:
            profile_dialog = ProfileWindow(
                username=user_data['username'],
                email=user_data['email'],
                parent=self
            )
            profile_dialog.logout_requested.connect(self.handle_logout)
            profile_dialog.exec_()
        else:
            QMessageBox.warning(self, "Error", "User data not found!")

    def handle_logout(self):
        self.logout_signal.emit()
        self.close()

    # Keep other methods the same...
         
    def redeem_money_code(self):
      code = self.code_input.text().strip()
    
      if not code:
        QMessageBox.warning(self, 'Error', 'Please enter a money code')
        return

      amount = self.db_manager.validate_and_use_money_code(code)
    
      if amount is not None:
        self.db_manager.add_balance_to_user(self.username, amount)
        self.refresh_balance()
        QMessageBox.information(self, 'Success', 
            f'Code redeemed! ${amount:.2f} added to your wallet.')
        self.logger.log(f"Money code redeemed by {self.username}: ${amount}")
        self.code_input.clear()
      else:
        QMessageBox.warning(self, 'Error', 'Invalid or already used money code')
        self.logger.log(f"Redemption failed: {str(e)}") # type: ignore

    def open_send_money_dialog(self):
      """Open the send money dialog window"""
      dialog = SendMoneyDialog(self.db_manager, self.username, self)
      if dialog.exec_():  # This makes the dialog modal
        # Refresh balance after sending money
        self.refresh_balance()
    
    def open_receive_money_dialog(self):
      """Open the receive money dialog window"""
      dialog = ReceiveMoneyDialog(self.db_manager, self.username)
      dialog.exec_()  # This makes the dialog modal

    def copy_wallet_id(self):
      """Copy wallet ID to clipboard"""
      clipboard = QApplication.clipboard()
      clipboard.setText(self.wallet_id)
      QMessageBox.information(self, "Copied", "Wallet ID copied to clipboard!")

    def show_transaction_history(self):
      """Show transaction history window"""
    # Correct initialization for TransactionWindow
      self.transaction_window = TransactionWindow(
        db_manager=self.db_manager,
        username=self.username,
        parent=self
    )
      self.transaction_window.show()

    def refresh_balance(self):
      """Refresh the displayed balance"""
      wallet_info = self.db_manager.get_user_wallet_info(self.username)
      _, new_balance = wallet_info
      self.balance_label.setText(f'Balance: ${new_balance:.2f}')

    def logout(self):
      """Handle logout"""
      reply = QMessageBox.question(self, 'Logout', 
                               'Are you sure you want to logout?', 
                               QMessageBox.Yes | QMessageBox.No)
      if reply == QMessageBox.Yes:
        self.logout_signal.emit()
        self.close()

    def add_profile_button(self):
         profile_btn = QPushButton()
         profile_btn.setIcon(QIcon(":/icons/profile.png"))
         profile_btn.setIconSize(profile_btn.iconSize())
         profile_btn.setStyleSheet("""
            QPushButton {
                border: none;
                padding: 5px;
                background-color: transparent;
            }
            QPushButton:hover {
                background-color: #f0f0f0;
            }
        """)
         profile_btn.setCursor(Qt.PointingHandCursor)
         profile_btn.clicked.connect(self.show_profile)
         self.layout().addWidget(profile_btn, alignment=Qt.AlignRight)
        
    def show_profile(self):
        user_data = self.db_manager.get_user_data(self.username)
        profile_dialog = ProfileWindow(
            username=user_data['username'],
            email=user_data['email'],
            parent=self
        )
        profile_dialog.logout_requested.connect(self.handle_logout)
        profile_dialog.exec_()