import sys
import pyqtgraph as pg
from PyQt5.QtWidgets import QApplication, QStackedWidget
from database import DatabaseManager
from ui.login_window import LoginWindow
from ui.signup_window import SignupWindow
from ui.wallet_window import WalletWindow
from ui.transaction_history_window import TransactionHistoryWindow
from ui.logs_window import LogsWindow

class WalletApp(QStackedWidget):
    def __init__(self):
        super().__init__()
        
        # Initialize database
        self.db_manager = DatabaseManager()
        print("Database initialized")
        
        # Check money codes
        cursor = self.db_manager.conn.cursor()
        cursor.execute('SELECT * FROM money_codes')
        print("Money Codes in Database:")
        for row in cursor.fetchall():
            print(row)
            
        # Create windows
        self.login_window = LoginWindow(self.db_manager)
        self.signup_window = SignupWindow(self.db_manager)
        self.wallet_window = None
        self.transaction_history_window = None
        self.logs_window = None

        # Add windows to stacked widget
        self.addWidget(self.login_window)
        self.addWidget(self.signup_window)

        # Connect signals
        self.login_window.login_successful.connect(self.show_wallet)
        self.login_window.switch_to_signup.connect(self.show_signup)
        
        self.signup_window.signup_successful.connect(self.show_wallet)
        self.signup_window.switch_to_login.connect(self.show_login)

        # Set initial view
        self.setCurrentWidget(self.login_window)

    def show_login(self):
        self.setCurrentWidget(self.login_window)

    def show_signup(self):
        self.setCurrentWidget(self.signup_window)

    def show_wallet(self, username):
        # Create new wallet window or update existing
        if self.wallet_window:
            self.removeWidget(self.wallet_window)
        
        self.wallet_window = WalletWindow(self.db_manager, username)
        self.wallet_window.logout_signal.connect(self.show_login)
        self.wallet_window.show_transaction_history_signal.connect(
            lambda: self.show_transaction_history(username)
        )
        self.wallet_window.show_logs_signal.connect(
            lambda: self.show_logs(username)
        )
        
        self.addWidget(self.wallet_window)
        self.setCurrentWidget(self.wallet_window)

    def show_transaction_history(self, username):
        # Create or update transaction history window
        if self.transaction_history_window:
            self.removeWidget(self.transaction_history_window)
            
        self.transaction_history_window = TransactionHistoryWindow(self.db_manager, username)
        self.transaction_history_window.back_to_wallet_signal.connect(
            lambda: self.setCurrentWidget(self.wallet_window)
        )
        
        self.addWidget(self.transaction_history_window)
        self.setCurrentWidget(self.transaction_history_window)

    def show_logs(self, username):
        # Create or update logs window
        if self.logs_window:
            self.removeWidget(self.logs_window)
            
        self.logs_window = LogsWindow(self.db_manager, username)
        self.logs_window.back_to_wallet_signal.connect(
            lambda: self.setCurrentWidget(self.wallet_window)
        )
        
        self.addWidget(self.logs_window)
        self.setCurrentWidget(self.logs_window)

    def closeEvent(self, event):
        # Close database connection
        self.db_manager.close()
        event.accept()

def main():
    app = QApplication(sys.argv)
    wallet_app = WalletApp()
    wallet_app.setWindowTitle('Wallet App')
    wallet_app.resize(500, 400)  # Slightly larger to accommodate new features
    wallet_app.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()