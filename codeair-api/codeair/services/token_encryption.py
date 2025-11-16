import base64
import hashlib

from cryptography.fernet import Fernet

__all__ = ["TokenEncryption"]


class TokenEncryption:
    def __init__(self, encryption_key: str) -> None:
        if len(encryption_key) != 32:
            raise ValueError("Encryption key must be 32 characters long")
        fernet_key = base64.urlsafe_b64encode(encryption_key.encode())
        self.fernet = Fernet(fernet_key)

    def encrypt(self, token: str) -> str:
        if not token:
            raise ValueError("Token must not be empty")
        return self.fernet.encrypt(token.encode()).decode()

    def decrypt(self, encrypted_token: str) -> str:
        if not encrypted_token:
            raise ValueError("Encrypted token must not be empty")
        return self.fernet.decrypt(encrypted_token.encode()).decode()

    def hash_token(self, token: str) -> str:
        if not token:
            raise ValueError("Token must not be empty")
        return hashlib.sha256(token.encode()).hexdigest()
