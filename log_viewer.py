# log_viewer.py
from secure_logger import SecureLogger
from cryptography.fernet import Fernet
import base64
import os
import tempfile

class LogViewer:
    def __init__(self, app_name="wallet_app"):
        self.logger = SecureLogger(app_name)
        
    def view_logs(self):
        key_path = os.path.join(tempfile.gettempdir(), f"{self.app_name}_key.key")
        with open(key_path, 'rb') as f:
            key = f.read()
            
        log_path = os.path.join(tempfile.gettempdir(), f"{self.app_name}_secure.log")
        with open(log_path, 'rb') as f:
            for line in f:
                try:
                    f = Fernet(key)
                    print(f.decrypt(base64.b64decode(line)).decode())
                except:
                    print(line.decode())