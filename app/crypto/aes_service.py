"""AES-256-GCM encryption for bytes and UTF-8 text."""

from __future__ import annotations

import base64
import binascii
import os
from collections.abc import Callable

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from app.utils.exceptions import (
    DecryptionError,
    InvalidEncryptedDataError,
    InvalidKeyError,
    ValidationError,
)

MAGIC = b"CRYPTO01"
VERSION = 1
MODE_KEY = 1
MODE_PASSWORD = 2
KEY_SIZE = 32
NONCE_SIZE = 12
SALT_SIZE = 16
TAG_SIZE = 16
PBKDF2_ITERATIONS = 600_000

_PREFIX_SIZE = len(MAGIC) + 2


def generate_key() -> bytes:
    """Generate a random 256-bit AES key."""
    return AESGCM.generate_key(bit_length=256)


def _validate_key(key: bytes) -> None:
    if not isinstance(key, bytes) or len(key) != KEY_SIZE:
        raise InvalidKeyError("Khóa AES-256 phải có đúng 32 byte.")


def _header(mode: int) -> bytes:
    return MAGIC + bytes((VERSION, mode))


def _validate_header(blob: bytes, expected_mode: int) -> bytes:
    minimum_size = _PREFIX_SIZE + NONCE_SIZE + TAG_SIZE
    if expected_mode == MODE_PASSWORD:
        minimum_size += SALT_SIZE
    if not isinstance(blob, bytes) or len(blob) < minimum_size:
        raise InvalidEncryptedDataError("Dữ liệu mã hóa không đầy đủ hoặc không hợp lệ.")
    if blob[: len(MAGIC)] != MAGIC:
        raise InvalidEncryptedDataError("Dữ liệu không phải định dạng CryptoDesk.")
    version = blob[len(MAGIC)]
    mode = blob[len(MAGIC) + 1]
    if version != VERSION:
        raise InvalidEncryptedDataError("Phiên bản dữ liệu mã hóa chưa được hỗ trợ.")
    if mode != expected_mode:
        raise InvalidEncryptedDataError("Chế độ giải mã không khớp với dữ liệu.")
    return blob[:_PREFIX_SIZE]


def encrypt_bytes(data: bytes, key: bytes) -> bytes:
    """Encrypt bytes with AES-256-GCM using a fresh random nonce."""
    _validate_key(key)
    if not isinstance(data, bytes):
        raise ValidationError("Dữ liệu mã hóa phải ở dạng bytes.")
    header = _header(MODE_KEY)
    nonce = os.urandom(NONCE_SIZE)
    ciphertext = AESGCM(key).encrypt(nonce, data, header)
    return header + nonce + ciphertext


def decrypt_bytes(blob: bytes, key: bytes) -> bytes:
    """Authenticate and decrypt a key-mode CryptoDesk payload."""
    _validate_key(key)
    header = _validate_header(blob, MODE_KEY)
    nonce_start = _PREFIX_SIZE
    nonce_end = nonce_start + NONCE_SIZE
    nonce = blob[nonce_start:nonce_end]
    try:
        return AESGCM(key).decrypt(nonce, blob[nonce_end:], header)
    except InvalidTag as exc:
        raise DecryptionError(
            "Không thể giải mã. Khóa không đúng hoặc dữ liệu đã bị thay đổi."
        ) from exc


def _derive_key(password: str, salt: bytes) -> bytes:
    if not password:
        raise ValidationError("Vui lòng nhập mật khẩu.")
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=KEY_SIZE,
        salt=salt,
        iterations=PBKDF2_ITERATIONS,
    )
    return kdf.derive(password.encode("utf-8"))


def encrypt_with_password(data: bytes, password: str) -> bytes:
    """Derive an AES key with PBKDF2 and encrypt bytes using AES-GCM."""
    if not isinstance(data, bytes):
        raise ValidationError("Dữ liệu mã hóa phải ở dạng bytes.")
    salt = os.urandom(SALT_SIZE)
    key = _derive_key(password, salt)
    header = _header(MODE_PASSWORD)
    nonce = os.urandom(NONCE_SIZE)
    ciphertext = AESGCM(key).encrypt(nonce, data, header)
    return header + salt + nonce + ciphertext


def decrypt_with_password(blob: bytes, password: str) -> bytes:
    """Authenticate and decrypt a password-mode CryptoDesk payload."""
    header = _validate_header(blob, MODE_PASSWORD)
    salt_start = _PREFIX_SIZE
    salt_end = salt_start + SALT_SIZE
    nonce_end = salt_end + NONCE_SIZE
    salt = blob[salt_start:salt_end]
    nonce = blob[salt_end:nonce_end]
    key = _derive_key(password, salt)
    try:
        return AESGCM(key).decrypt(nonce, blob[nonce_end:], header)
    except InvalidTag as exc:
        raise DecryptionError(
            "Không thể giải mã. Mật khẩu không đúng hoặc dữ liệu đã bị thay đổi."
        ) from exc


def encrypt_text(text: str, key: bytes) -> str:
    """Encrypt UTF-8 text and return a Base64 payload."""
    return base64.b64encode(encrypt_bytes(text.encode("utf-8"), key)).decode("ascii")


def decrypt_text(value: str, key: bytes) -> str:
    """Decrypt a Base64 key-mode payload into UTF-8 text."""
    return _decrypt_text_payload(value, lambda blob: decrypt_bytes(blob, key))


def encrypt_text_with_password(text: str, password: str) -> str:
    """Encrypt UTF-8 text with a password and return a Base64 payload."""
    blob = encrypt_with_password(text.encode("utf-8"), password)
    return base64.b64encode(blob).decode("ascii")


def decrypt_text_with_password(value: str, password: str) -> str:
    """Decrypt a Base64 password-mode payload into UTF-8 text."""
    return _decrypt_text_payload(value, lambda blob: decrypt_with_password(blob, password))


def _decrypt_text_payload(value: str, decryptor: Callable[[bytes], bytes]) -> str:
    try:
        blob = base64.b64decode(value.strip(), validate=True)
    except (binascii.Error, ValueError) as exc:
        raise InvalidEncryptedDataError("Ciphertext phải là Base64 hợp lệ.") from exc
    try:
        plaintext = decryptor(blob)
        return plaintext.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise DecryptionError("Dữ liệu giải mã không phải văn bản UTF-8 hợp lệ.") from exc
