import logging
import secrets
from base64 import urlsafe_b64encode as b64e, urlsafe_b64decode as b64d
from getpass import getpass

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

log = logging.getLogger(__name__)

backend = default_backend()
iterations = 100_000


def _derive_key(password: bytes, salt: bytes, iterations: int = iterations) -> bytes:
    """Derive a secret key from a given password and salt"""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(), length=32, salt=salt,
        iterations=iterations, backend=backend)
    return b64e(kdf.derive(password))


def _encrypt(message: bytes, password: str, iterations: int = iterations) -> bytes:
    salt = secrets.token_bytes(16)
    key = _derive_key(password.encode(), salt, iterations)
    return b64e(
        b'%b%b%b' % (
            salt,
            iterations.to_bytes(4, 'big'),
            b64d(Fernet(key).encrypt(message)),
        )
    )


def _decrypt(token: bytes, password: str) -> bytes:
    decoded = b64d(token)
    salt, iter, token = decoded[:16], decoded[16:20], b64e(decoded[20:])
    iterations = int.from_bytes(iter, 'big')
    key = _derive_key(password.encode(), salt, iterations)
    return Fernet(key).decrypt(token)


def encrypt(message, password):
    return _encrypt(message.encode(), password)


def decrypt(encrypted_message, password):
    return _decrypt(encrypted_message, password).decode()

def encrypt_private_key():
    private_key = getpass(prompt="[+] Input private key: ")
    password = getpass(prompt="[+] Input password: ")
    encrypted_private_key = encrypt(private_key, password).decode("utf-8")
    print("[!] Add private_key = \"" + encrypted_private_key + "\" to config.py")

def decrypt_private_key(private_key):
    password = getpass(prompt="[+] Input password: ")
    try:
        decrypted_private_key = decrypt(private_key, password)
    except InvalidToken:
        msg = f"[?] Invalid password"
        print(msg)
        log.error(msg)
        exit(1)
    return decrypted_private_key

def main():
    message = 'John Doe'
    password = 'mypass'
    encrypted_message = encrypt(message, password)
    print(decrypt(encrypted_message, password))


if __name__ == "__main__":
    main()
