import sqlite3
import hashlib
import uuid
import secrets
import os
import datetime
import json
from cryptography.fernet import Fernet

class DatabaseManager:
    def __init__(self, db_name='wallet_app.db'):
        self.conn = sqlite3.connect(db_name)
        self.create_tables()
        self.initialize_money_codes()
        self.logs_dir = 'user_logs'
        
        # Create logs directory if it doesn't exist
        if not os.path.exists(self.logs_dir):
            os.makedirs(self.logs_dir)
            
        # Initialize encryption key for logs
        self.key_file = 'log_key.key'
        if not os.path.exists(self.key_file):
            self.generate_encryption_key()
        else:
            with open(self.key_file, 'rb') as file:
                self.key = file.read()
        
        self.cipher = Fernet(self.key)

    def generate_encryption_key(self):
        """Generate and save encryption key"""
        self.key = Fernet.generate_key()
        with open(self.key_file, 'wb') as file:
            file.write(self.key)

    def create_tables(self):
        cursor = self.conn.cursor()
    
        # Create users table with all columns from the start
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            wallet_id TEXT UNIQUE NOT NULL,
            balance REAL DEFAULT 0.0,
            pin TEXT NOT NULL,
            log_password TEXT DEFAULT NULL
        )
        ''')
    
        # Money codes table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS money_codes (
                code TEXT PRIMARY KEY,
                amount REAL NOT NULL,
                is_used INTEGER DEFAULT 0
            )
        ''')
    
        # Transactions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sender_username TEXT NOT NULL,
                recipient_username TEXT NOT NULL,
                amount REAL NOT NULL,
                timestamp DATETIME NOT NULL,
                transaction_type TEXT NOT NULL,
                description TEXT
            )
        ''')
    
        self.conn.commit()

    def set_user_pin(self, username, pin):
        if len(pin) != 4 or not pin.isdigit():
            raise ValueError("PIN must be 4 digits")
    
        hashed_pin = self.hash_pin(pin)
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE users SET pin = ? WHERE username = ?
        ''', (hashed_pin, username))
        self.conn.commit()
        
        # Log PIN change
        self.log_activity(username, "PIN_CHANGE", f"User changed their PIN")

    def set_log_password(self, username, password):
        """Set password for accessing transaction logs"""
        if not password or len(password) < 6:
            raise ValueError("Log password must be at least 6 characters")
        
        hashed_password = self.hash_password(password)
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE users SET log_password = ? WHERE username = ?
        ''', (hashed_password, username))
        self.conn.commit()
        
        # Log password change
        self.log_activity(username, "LOG_PASSWORD_SET", "User set log access password")
        return True

    def verify_log_password(self, username, password):
        """Verify the password for accessing transaction logs"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT log_password FROM users WHERE username = ?
        ''', (username,))
        result = cursor.fetchone()
        
        if not result or not result[0]:
            return False
            
        stored_hash = result[0]
        input_hash = self.hash_password(password)
        return stored_hash == input_hash

    def verify_pin(self, username, pin):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT pin FROM users WHERE username = ?
        ''', (username,))
        result = cursor.fetchone()
    
        if not result:
            return False
            
        stored_hash = result[0]
        input_hash = self.hash_pin(pin)
        return stored_hash == input_hash

    def hash_pin(self, pin):
        # Add salt for better security
        salt = "fixed_salt_placeholder"  # In production, use a unique salt per user
        return hashlib.sha256((pin + salt).encode()).hexdigest()

    def initialize_money_codes(self):
        # Predefined money codes
        codes = [
            ('01024847873', 1000),
            ('01282186279', 1000),
            ('01063536993', 5),
            ('01152903264', 5),
            ('01066112306', 1000000)
        ]
        
        cursor = self.conn.cursor()
        
        # First, delete any existing codes to ensure a clean slate
        cursor.execute('DELETE FROM money_codes')
        
        # Insert new codes
        for code, amount in codes:
            cursor.execute('''
                INSERT INTO money_codes (code, amount, is_used) 
                VALUES (?, ?, 0)
            ''', (code, amount))
        
        self.conn.commit()

        # Verify inserted codes
        cursor.execute('SELECT * FROM money_codes')
        print("Inserted Money Codes:")
        for row in cursor.fetchall():
            print(row)

    def validate_and_use_money_code(self, code):
        cursor = self.conn.cursor()
        
        # Print out the code being checked for debugging
        print(f"Checking code: {code}")
        
        # Check if code exists and is not used
        cursor.execute('''
            SELECT amount FROM money_codes 
            WHERE code = ? AND is_used = 0
        ''', (code,))
        
        result = cursor.fetchone()
        print(f"Query result: {result}")
        
        if result:
            # Mark code as used and return amount
            amount = result[0]
            cursor.execute('''
                UPDATE money_codes 
                SET is_used = 1 
                WHERE code = ?
            ''', (code,))
            self.conn.commit()
            return amount
        
        # If no result, check if code exists at all
        cursor.execute('SELECT * FROM money_codes WHERE code = ?', (code,))
        existing_code = cursor.fetchone()
        print(f"Existing code check: {existing_code}")
        
        return None

    def add_balance_to_user(self, username, amount):
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE users 
            SET balance = balance + ? 
            WHERE username = ?
        ''', (amount, username))
        self.conn.commit()
        
        # Record this transaction
        self.record_transaction(
            username, 
            "SYSTEM", 
            amount, 
            "DEPOSIT", 
            "Added funds with money code"
        )
        
        # Log the activity
        self.log_activity(
            username, 
            "DEPOSIT", 
            f"Added ${amount:.2f} using money code"
        )

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def register_user(self, username, password, pin='0000'):
        try:
            # Validate PIN
            if len(pin) != 4 or not pin.isdigit():
                raise ValueError("PIN must be 4 digits")
                
            wallet_id = f'233439{str(uuid.uuid4())[:10]}'
            hashed_password = self.hash_password(password)
            hashed_pin = self.hash_pin(pin)
            
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO users (username, password, wallet_id, pin) 
                VALUES (?, ?, ?, ?)
            ''', (username, hashed_password, wallet_id, hashed_pin))
            self.conn.commit()
            
            # Log new account creation
            self.log_activity(username, "REGISTRATION", "New user account created")
            
            return wallet_id
        except sqlite3.IntegrityError:
            return None

    def is_default_pin(self, username):
        """Check if user still has default PIN"""
        default_pin_hash = self.hash_pin('0000')
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT pin FROM users WHERE username = ?
        ''', (username,))
        result = cursor.fetchone()
        return result and result[0] == default_pin_hash

    def validate_login(self, username, password):
        cursor = self.conn.cursor()
        hashed_password = self.hash_password(password)
        cursor.execute('''
            SELECT * FROM users 
            WHERE username = ? AND password = ?
        ''', (username, hashed_password))
        
        result = cursor.fetchone() is not None
        
        if result:
            # Log successful login
            self.log_activity(username, "LOGIN", "User logged in successfully")
        else:
            # Log failed login attempt
            self.log_activity(username, "LOGIN_FAILED", "Failed login attempt")
            
        return result

    def get_username_by_wallet_id(self, wallet_id):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT username FROM users WHERE wallet_id = ?
        ''', (wallet_id,))
        result = cursor.fetchone()
        return result[0] if result else None

    def get_user_wallet_info(self, username):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT wallet_id, balance 
            FROM users 
            WHERE username = ?
        ''', (username,))
        return cursor.fetchone()

    def close(self):
        self.conn.close()

    def send_money(self, sender_username, recipient_wallet, amount):
        cursor = self.conn.cursor()
        
        # Validate amount
        if amount <= 0:
            raise ValueError("Amount must be greater than zero")
        
        # Check sender's details and balance
        cursor.execute('''
            SELECT wallet_id, balance FROM users 
            WHERE username = ?
        ''', (sender_username,))
        sender_details = cursor.fetchone()
        
        if not sender_details:
            raise ValueError("Sender account not found")
        
        sender_wallet_id, sender_balance = sender_details
        
        # Prevent sending money to own wallet
        if sender_wallet_id == recipient_wallet:
            raise ValueError("Cannot send money to your own wallet")
        
        # Check sender's balance
        if sender_balance < amount:
            raise ValueError(f"Insufficient funds. Current balance: ${sender_balance:.2f}")
        
        # Find recipient by wallet ID
        cursor.execute('''
            SELECT username FROM users 
            WHERE wallet_id = ?
        ''', (recipient_wallet,))
        recipient = cursor.fetchone()
        
        if not recipient:
            raise ValueError("Recipient wallet not found. Please check the wallet ID.")
        
        recipient_username = recipient[0]
        
        # Prevent sending to the same user
        if recipient_username == sender_username:
            raise ValueError("Cannot send money to yourself")
        
        try:
            # Deduct from sender
            cursor.execute('''
                UPDATE users 
                SET balance = balance - ? 
                WHERE username = ?
            ''', (amount, sender_username))
            
            # Add to recipient
            cursor.execute('''
                UPDATE users 
                SET balance = balance + ? 
                WHERE username = ?
            ''', (amount, recipient_username))
            
            # Record the transaction
            self.record_transaction(
                sender_username, 
                recipient_username, 
                amount, 
                "TRANSFER", 
                f"Transfer to {recipient_wallet}"
            )
            
            # Log the activities
            self.log_activity(
                sender_username, 
                "SEND_MONEY", 
                f"Sent ${amount:.2f} to {recipient_username} ({recipient_wallet})"
            )
            
            self.log_activity(
                recipient_username, 
                "RECEIVE_MONEY", 
                f"Received ${amount:.2f} from {sender_username}"
            )
            
            # Commit transaction
            self.conn.commit()
            return True
            
        except Exception as e:
            # Rollback in case of any error
            self.conn.rollback()
            raise  # Re-raise the exception to be handled in the UI

    def record_transaction(self, sender, recipient, amount, transaction_type, description=None):
        """Record a transaction in the database"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO transactions (
                sender_username, 
                recipient_username, 
                amount, 
                timestamp,
                transaction_type,
                description
            ) VALUES (?, ?, ?, datetime('now'), ?, ?)
        ''', (sender, recipient, amount, transaction_type, description))
        self.conn.commit()

    def get_user_transactions(self, username):
        """Get all transactions for a user (both sent and received)"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT 
                id,
                sender_username, 
                recipient_username, 
                amount, 
                timestamp,
                transaction_type,
                description
            FROM transactions 
            WHERE sender_username = ? OR recipient_username = ? 
            ORDER BY timestamp DESC
        ''', (username, username))
        
        return cursor.fetchall()

    def log_activity(self, username, action_type, description):
        """Create a log entry for user activity"""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Create the log entry
        log_entry = {
            "timestamp": timestamp,
            "action": action_type,
            "description": description
        }
        
        # Generate log filename for this user
        filename = os.path.join(self.logs_dir, f"{username}_logs.txt")
        
        # Check if file already exists
        file_exists = os.path.exists(filename)
        
        # Read existing logs if file exists
        logs = []
        if file_exists:
            try:
                with open(filename, 'rb') as file:
                    encrypted_data = file.read()
                    decrypted_data = self.cipher.decrypt(encrypted_data).decode()
                    logs = json.loads(decrypted_data)
            except Exception as e:
                print(f"Error reading log file: {e}")
                logs = []
        
        # Add new log entry
        logs.append(log_entry)
        
        # Write updated logs back to file (encrypted)
        try:
            encrypted_data = self.cipher.encrypt(json.dumps(logs).encode())
            with open(filename, 'wb') as file:
                file.write(encrypted_data)
        except Exception as e:
            print(f"Error writing to log file: {e}")

    def get_user_logs(self, username, password):
        """Retrieve and decrypt user logs if password is correct"""
        if not self.verify_log_password(username, password):
            return None
        
        filename = os.path.join(self.logs_dir, f"{username}_logs.txt")
        
        if not os.path.exists(filename):
            return []
        
        try:
            with open(filename, 'rb') as file:
                encrypted_data = file.read()
                decrypted_data = self.cipher.decrypt(encrypted_data).decode()
                return json.loads(decrypted_data)
        except Exception as e:
            print(f"Error reading log file: {e}")
            return []

    def has_log_password(self, username):
        """Check if user has set a log password"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT log_password FROM users WHERE username = ?
        ''', (username,))
        result = cursor.fetchone()
        return result and result[0] is not None