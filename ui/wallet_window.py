from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, 
                             QMessageBox, QHBoxLayout, QLineEdit, QDialog, 
                             QFormLayout,QApplication, QListWidget)
from PyQt5.QtCore import pyqtSignal
from ui.base_window import BaseWindow
class TransactionWindow(QWidget):
    def __init__(self, db_manager, username):
        super().__init__()
        self.db_manager = db_manager
        self.username = username
        self.setWindowTitle("Transaction History")
        self.resize(500, 400)
        self.init_ui()
    
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
            raise ValueError("Amount must be positive")
            
        # Get recipient username for confirmation
        recipient_username = self.db_manager.get_username_by_wallet_id(recipient_wallet)
        if not recipient_username:
            raise ValueError("Wallet not found")
            
        # Confirmation dialog
        confirm = QMessageBox.question(
            self,
            "Confirm Transfer",
            f"Send ${amount:.2f} to {recipient_username} ({recipient_wallet})?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if confirm == QMessageBox.Yes:
            # Correct call with proper arguments
            self.db_manager.send_money(
                self.sender_username,
                recipient_wallet,
                amount
            )
            QMessageBox.information(
                self,
                "Success",
                f"Sent ${amount:.2f} to {recipient_username}"
            )
            self.accept()
            
      except ValueError as ve:
        QMessageBox.warning(self, "Input Error", str(ve))
      except Exception as e:
        QMessageBox.critical(
            self,
            "Transfer Failed",
            f"An error occurred: {str(e)}"
        )
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

class WalletWindow(QWidget):
    logout_signal = pyqtSignal()

    def __init__(self, db_manager, username):
        super().__init__()
        self.db_manager = db_manager
        self.username = username
        # Get wallet info immediately and store it
        wallet_info = self.db_manager.get_user_wallet_info(self.username)
        self.wallet_id, self.balance = wallet_info  # Store both wallet_id and balance
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Wallet App - My Wallet')
        self.setGeometry(300, 300, 400, 350)

        layout = QVBoxLayout()

        # Wallet ID Display (now using self.wallet_id which was set in __init__)
        self.wallet_id_label = QLabel(f'Wallet ID: {self.wallet_id}')
        layout.addWidget(self.wallet_id_label)

        # Balance Display (using self.balance which was set in __init__)
        self.balance_label = QLabel(f'Balance: ${self.balance:.2f}')
        layout.addWidget(self.balance_label)

        # Money Code Redemption Section
        code_layout = QHBoxLayout()
        
        self.code_input = QLineEdit()
        self.code_input.setPlaceholderText('Enter Money Code')
        code_layout.addWidget(self.code_input)

        redeem_btn = QPushButton('Redeem Code')
        redeem_btn.clicked.connect(self.redeem_money_code)
        code_layout.addWidget(redeem_btn)

        layout.addLayout(code_layout)

        # Buttons Layout
        btn_layout = QHBoxLayout()

        # Send Money Button 
        send_btn = QPushButton('Send Money')
        send_btn.clicked.connect(self.open_send_money_dialog)
        btn_layout.addWidget(send_btn)

        # Receive Money Button 
        receive_btn = QPushButton('Receive Money')
        receive_btn.clicked.connect(self.open_receive_money_dialog)
        btn_layout.addWidget(receive_btn)

        # Add button layout to main layout
        layout.addLayout(btn_layout)

        self.copy_button = QPushButton("Copy Wallet ID")
        self.copy_button.clicked.connect(self.copy_wallet_id)
        self.history_button = QPushButton("View Transaction History")
        self.history_button.clicked.connect(self.show_transaction_history)
        layout.addWidget(self.history_button)
        layout.addWidget(self.copy_button)

        # Logout Button
        logout_btn = QPushButton('Logout')
        logout_btn.clicked.connect(self.logout)
        layout.addWidget(logout_btn)

        self.setLayout(layout)
         
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
        self.code_input.clear()
      else:
        QMessageBox.warning(self, 'Error', 'Invalid or already used money code')

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
      self.transaction_window = TransactionWindow(self.db_manager, self.username)
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