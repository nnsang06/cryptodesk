"""Tests for RSA key and OAEP operations."""

import pytest

from app.crypto import rsa_service
from app.utils.exceptions import DecryptionError, InvalidKeyError, ValidationError


def test_generate_encrypt_decrypt_round_trip() -> None:
    private_pem, public_pem = rsa_service.generate_key_pair()
    ciphertext = rsa_service.encrypt_text("RSA xin chào", public_pem)
    assert rsa_service.decrypt_text(ciphertext, private_pem) == "RSA xin chào"


def test_wrong_private_key_fails() -> None:
    _, public_pem = rsa_service.generate_key_pair()
    other_private_pem, _ = rsa_service.generate_key_pair()
    ciphertext = rsa_service.encrypt_text("secret", public_pem)
    with pytest.raises(DecryptionError):
        rsa_service.decrypt_text(ciphertext, other_private_pem)


@pytest.mark.parametrize("pem", [b"", b"not a pem", b"-----BEGIN PUBLIC KEY-----\nBAD"])
def test_invalid_public_pem(pem: bytes) -> None:
    with pytest.raises(InvalidKeyError):
        rsa_service.encrypt_text("hello", pem)


def test_invalid_private_pem_and_ciphertext() -> None:
    private_pem, _ = rsa_service.generate_key_pair()
    with pytest.raises(InvalidKeyError):
        rsa_service.decrypt_text("AAAA", b"bad key")
    with pytest.raises(ValidationError):
        rsa_service.decrypt_text("not base64!", private_pem)


def test_plaintext_size_is_validated() -> None:
    _, public_pem = rsa_service.generate_key_pair()
    with pytest.raises(ValidationError, match="quá dài"):
        rsa_service.encrypt_text("x" * 191, public_pem)

