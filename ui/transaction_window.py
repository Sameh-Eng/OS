from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QListWidget, 
                            QLineEdit, QPushButton, QMessageBox)

class TransactionWindow(QWidget):
    def __init__(self, db_manager, username):
        super().__init__()
        self.db_manager = db_manager
        self.username = username
        self.setWindowTitle("Transaction History")
        self.resize(500, 400)
        self.setup_ui()
        
    def setup_ui(self):
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