"""RSA key generation and OAEP text encryption services."""

from __future__ import annotations

import base64
import binascii

from cryptography.exceptions import UnsupportedAlgorithm
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa

from app.utils.exceptions import DecryptionError, InvalidKeyError, ValidationError

DEFAULT_KEY_SIZE = 2048
PUBLIC_EXPONENT = 65537


def generate_key_pair(key_size: int = DEFAULT_KEY_SIZE) -> tuple[bytes, bytes]:
    """Return an unencrypted PKCS8 private PEM and SubjectPublicKeyInfo PEM."""
    if key_size not in (2048, 3072, 4096):
        raise ValidationError("Kích thước khóa RSA phải là 2048, 3072 hoặc 4096 bit.")
    private_key = rsa.generate_private_key(
        public_exponent=PUBLIC_EXPONENT,
        key_size=key_size,
    )
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    public_pem = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    return private_pem, public_pem


def load_public_key(public_key_pem: bytes) -> rsa.RSAPublicKey:
    """Validate and load an RSA public key from PEM."""
    try:
        key = serialization.load_pem_public_key(public_key_pem)
    except (ValueError, TypeError, UnsupportedAlgorithm) as exc:
        raise InvalidKeyError("Public key PEM không hợp lệ.") from exc
    if not isinstance(key, rsa.RSAPublicKey):
        raise InvalidKeyError("PEM không chứa RSA public key.")
    return key


def load_private_key(
    private_key_pem: bytes,
    password: bytes | None = None,
) -> rsa.RSAPrivateKey:
    """Validate and load an RSA private key from PEM."""
    try:
        key = serialization.load_pem_private_key(private_key_pem, password=password)
    except (ValueError, TypeError, UnsupportedAlgorithm) as exc:
        raise InvalidKeyError("Private key PEM hoặc passphrase không hợp lệ.") from exc
    if not isinstance(key, rsa.RSAPrivateKey):
        raise InvalidKeyError("PEM không chứa RSA private key.")
    return key


def _oaep_padding() -> padding.OAEP:
    return padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None,
    )


def encrypt_text(text: str, public_key_pem: bytes) -> str:
    """Encrypt short UTF-8 text with RSA-OAEP and return Base64."""
    public_key = load_public_key(public_key_pem)
    plaintext = text.encode("utf-8")
    hash_size = hashes.SHA256().digest_size
    maximum_size = public_key.key_size // 8 - 2 * hash_size - 2
    if len(plaintext) > maximum_size:
        raise ValidationError(
            f"Văn bản quá dài cho RSA-{public_key.key_size}. "
            f"Giới hạn hiện tại là {maximum_size} byte UTF-8."
        )
    ciphertext = public_key.encrypt(plaintext, _oaep_padding())
    return base64.b64encode(ciphertext).decode("ascii")


def decrypt_text(
    ciphertext_b64: str,
    private_key_pem: bytes,
    password: bytes | None = None,
) -> str:
    """Decrypt Base64 RSA-OAEP ciphertext with a private PEM key."""
    private_key = load_private_key(private_key_pem, password)
    try:
        ciphertext = base64.b64decode(ciphertext_b64.strip(), validate=True)
    except (binascii.Error, ValueError) as exc:
        raise ValidationError("Ciphertext RSA phải là Base64 hợp lệ.") from exc
    try:
        plaintext = private_key.decrypt(ciphertext, _oaep_padding())
        return plaintext.decode("utf-8")
    except (ValueError, UnicodeDecodeError) as exc:
        raise DecryptionError(
            "Không thể giải mã RSA. Khóa không đúng hoặc ciphertext không hợp lệ."
        ) from exc

