# secure_logger.py
import os
import tempfile
from datetime import datetime
from cryptography.fernet import Fernet
import base64

class SecureLogger:
    def __init__(self, app_name="wallet_app"):
        self.app_name = app_name
        self.log_file_path = os.path.join(tempfile.gettempdir(), f"{app_name}_secure.log")
        self.key = self._load_or_create_key()
        self._setup_log_file()

    def _load_or_create_key(self):
        key_path = os.path.join(tempfile.gettempdir(), f"{self.app_name}_key.key")
        if os.path.exists(key_path):
            with open(key_path, 'rb') as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            with open(key_path, 'wb') as f:
                f.write(key)
            os.chmod(key_path, 0o400)  # Read-only for owner
            return key

    def _setup_log_file(self):
        self.fd = os.open(self.log_file_path, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
        
    def _encrypt(self, message):
        f = Fernet(self.key)
        return base64.b64encode(f.encrypt(message.encode())).decode()

    def log(self, message):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        encrypted_msg = self._encrypt(f"[{timestamp}] {message}")
        os.write(self.fd, (encrypted_msg + '\n').encode())
        os.fsync(self.fd)

    def __del__(self):
        os.close(self.fd)

    def rotate_logs(self, max_size_mb=10):
      if os.path.getsize(self.log_file_path) > max_size_mb * 1024 * 1024:
        new_path = f"{self.log_file_path}.{datetime.now().timestamp()}"
        os.rename(self.log_file_path, new_path)
        self._setup_log_file()
        self.log("Log file rotated")