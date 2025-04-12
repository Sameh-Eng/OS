from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QFont, QColor
import datetime

class TransactionHistoryWindow(QWidget):
    back_to_wallet_signal = pyqtSignal()
    
    def __init__(self, db_manager, username):
        super().__init__()
        self.db_manager = db_manager
        self.username = username
        
        self.init_ui()
        self.load_transactions()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Header
        header_layout = QHBoxLayout()
        title_label = QLabel("Transaction History")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        
        back_btn = QPushButton("Back to Wallet")
        back_btn.clicked.connect(self.back_to_wallet)
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(back_btn)
        
        layout.addLayout(header_layout)
        
        # Transaction table
        self.transaction_table = QTableWidget()
        self.transaction_table.setColumnCount(6)
        self.transaction_table.setHorizontalHeaderLabels([
            "Date", "Type", "Description", "Sender", "Recipient", "Amount"
        ])
        
        # Adjust column widths
        header = self.transaction_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        
        layout.addWidget(self.transaction_table)
        
        # Refresh button
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.load_transactions)
        layout.addWidget(refresh_btn)
        
        self.setLayout(layout)
        
    def load_transactions(self):
        # Clear existing table
        self.transaction_table.setRowCount(0)
        
        # Get transactions from database
        transactions = self.db_manager.get_user_transactions(self.username)
        
        if not transactions:
            self.transaction_table.setRowCount(1)
            no_data = QTableWidgetItem("No transactions found")
            self.transaction_table.setSpan(0, 0, 1, 6)
            self.transaction_table.setItem(0, 0, no_data)
            return
        
        # Populate table
        self.transaction_table.setRowCount(len(transactions))
        
        for row, tx in enumerate(transactions):
            tx_id, sender, recipient, amount, timestamp, tx_type, description = tx
            
            # Format timestamp
            try:
                tx_date = datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
                formatted_date = tx_date.strftime("%Y-%m-%d %H:%M")
            except:
                formatted_date = timestamp
                
            # Add to table
            self.transaction_table.setItem(row, 0, QTableWidgetItem(formatted_date))
            self.transaction_table.setItem(row, 1, QTableWidgetItem(tx_type))
            self.transaction_table.setItem(row, 2, QTableWidgetItem(description or ""))
            self.transaction_table.setItem(row, 3, QTableWidgetItem(sender))
            self.transaction_table.setItem(row, 4, QTableWidgetItem(recipient))
            
            # Format amount with color based on transaction direction
            amount_item = QTableWidgetItem(f"${amount:.2f}")
            if sender == self.username and recipient != "SYSTEM":
                amount_item.setForeground(QColor("red"))
                amount_str = f"-${amount:.2f}"
            else:
                amount_item.setForeground(QColor("green"))
                amount_str = f"+${amount:.2f}"
                
            amount_item = QTableWidgetItem(amount_str)
            self.transaction_table.setItem(row, 5, amount_item)
            
    def back_to_wallet(self):
        self.back_to_wallet_signal.emit()