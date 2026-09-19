"""Tests for AES-256-GCM key and password modes."""

import base64

import pytest

from app.crypto import aes_service
from app.utils.exceptions import (
    DecryptionError,
    InvalidEncryptedDataError,
    InvalidKeyError,
    ValidationError,
)


def test_generate_key_is_256_bits() -> None:
    assert len(aes_service.generate_key()) == 32


def test_key_mode_round_trip_and_random_nonce() -> None:
    key = aes_service.generate_key()
    data = "Xin chào CryptoDesk 🔐".encode()
    first = aes_service.encrypt_bytes(data, key)
    second = aes_service.encrypt_bytes(data, key)
    assert first != second
    assert aes_service.decrypt_bytes(first, key) == data


def test_wrong_key_and_tampering_fail_closed() -> None:
    key = aes_service.generate_key()
    blob = aes_service.encrypt_bytes(b"sensitive", key)
    with pytest.raises(DecryptionError):
        aes_service.decrypt_bytes(blob, aes_service.generate_key())

    tampered = bytearray(blob)
    tampered[-1] ^= 1
    with pytest.raises(DecryptionError):
        aes_service.decrypt_bytes(bytes(tampered), key)


def test_invalid_key_and_blob_header() -> None:
    with pytest.raises(InvalidKeyError):
        aes_service.encrypt_bytes(b"data", b"short")

    key = aes_service.generate_key()
    blob = aes_service.encrypt_bytes(b"data", key)
    with pytest.raises(InvalidEncryptedDataError):
        aes_service.decrypt_bytes(b"BROKEN!!" + blob[8:], key)


def test_password_mode_round_trip_randomness_and_wrong_password() -> None:
    data = b"password protected"
    first = aes_service.encrypt_with_password(data, "correct horse")
    second = aes_service.encrypt_with_password(data, "correct horse")
    assert first != second
    assert aes_service.decrypt_with_password(first, "correct horse") == data
    with pytest.raises(DecryptionError):
        aes_service.decrypt_with_password(first, "wrong battery")


def test_text_helpers_and_invalid_base64() -> None:
    key = aes_service.generate_key()
    ciphertext = aes_service.encrypt_text("Tiếng Việt", key)
    assert aes_service.decrypt_text(ciphertext, key) == "Tiếng Việt"
    assert base64.b64decode(ciphertext, validate=True)
    with pytest.raises(InvalidEncryptedDataError):
        aes_service.decrypt_text("not base64!", key)
    with pytest.raises(ValidationError):
        aes_service.encrypt_with_password(b"data", "")
