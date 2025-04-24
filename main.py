import sys
import pyqtgraph as pg
from PyQt5.QtWidgets import QApplication, QStackedWidget
from PyQt5.QtWidgets import QSplashScreen
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QTimer
from database import DatabaseManager
from ui.login_window import LoginWindow
from ui.signup_window import SignupWindow
from ui.wallet_window import WalletWindow
import os
os.environ['QT_AUTO_SCREEN_SCALE_FACTOR'] = '1'

def main():
    app = QApplication(sys.argv)
    
    # Create and show splash screen
    splash_pix = QPixmap('logo.png')
    splash = QSplashScreen(splash_pix, Qt.WindowStaysOnTopHint)
    splash.show()
    
    # Center the splash screen
    splash.move(app.primaryScreen().geometry().center() - splash.rect().center())
    
    # Load your main application
    wallet_app = WalletApp()
    
    # Close splash after 2 seconds (2000ms)
    QTimer.singleShot(2000, splash.close)
    QTimer.singleShot(2000, wallet_app.show)
    
    sys.exit(app.exec_())
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
        
        self.addWidget(self.wallet_window)
        self.setCurrentWidget(self.wallet_window)

    def closeEvent(self, event):
        # Close database connection
        
        event.accept()

def main():
    app = QApplication(sys.argv)
    wallet_app = WalletApp()
    wallet_app.setWindowTitle('Wallet App')
    wallet_app.resize(400, 300)
    wallet_app.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()