"""Key generation, validation, import, and export services."""

from __future__ import annotations

import base64
from pathlib import Path

from cryptography.hazmat.primitives import serialization

from app.crypto import aes_service, rsa_service
from app.utils.exceptions import FileServiceError


def generate_aes_key_b64() -> str:
    """Generate an AES-256 key and return its Base64 representation."""
    return base64.b64encode(aes_service.generate_key()).decode("ascii")


def generate_rsa_key_pair(key_size: int = 2048) -> tuple[bytes, bytes]:
    """Generate RSA private and public PEM data."""
    return rsa_service.generate_key_pair(key_size)


def import_public_key(path: Path) -> bytes:
    """Read and validate an RSA public PEM file."""
    pem = _read_key_file(path)
    rsa_service.load_public_key(pem)
    return pem


def import_private_key(path: Path, passphrase: str = "") -> bytes:
    """Read and validate an RSA private PEM file."""
    pem = _read_key_file(path)
    password = passphrase.encode("utf-8") if passphrase else None
    rsa_service.load_private_key(pem, password)
    return pem


def export_public_key(public_pem: bytes, path: Path) -> None:
    """Validate and export an RSA public PEM file."""
    key = rsa_service.load_public_key(public_pem)
    normalized = key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    _write_key_file(path, normalized)


def export_private_key(
    private_pem: bytes,
    path: Path,
    passphrase: str = "",
    current_passphrase: str = "",
) -> None:
    """Export an RSA private PEM, optionally encrypted by a passphrase."""
    current_password = current_passphrase.encode("utf-8") if current_passphrase else None
    key = rsa_service.load_private_key(private_pem, current_password)
    encryption: serialization.KeySerializationEncryption
    if passphrase:
        encryption = serialization.BestAvailableEncryption(passphrase.encode("utf-8"))
    else:
        encryption = serialization.NoEncryption()
    normalized = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=encryption,
    )
    _write_key_file(path, normalized)


def public_key_metadata(public_pem: bytes) -> dict[str, str | int]:
    """Return non-secret RSA public key metadata."""
    key = rsa_service.load_public_key(public_pem)
    return {"type": "RSA Public Key", "algorithm": "RSA", "bits": key.key_size}


def private_key_metadata(
    private_pem: bytes,
    passphrase: str = "",
) -> dict[str, str | int]:
    """Return non-secret RSA private key metadata."""
    password = passphrase.encode("utf-8") if passphrase else None
    key = rsa_service.load_private_key(private_pem, password)
    return {"type": "RSA Private Key", "algorithm": "RSA", "bits": key.key_size}


def _read_key_file(path: Path) -> bytes:
    try:
        return Path(path).read_bytes()
    except FileNotFoundError as exc:
        raise FileServiceError("Tệp khóa không tồn tại.") from exc
    except PermissionError as exc:
        raise FileServiceError("Không có quyền đọc tệp khóa.") from exc
    except OSError as exc:
        raise FileServiceError("Không thể đọc tệp khóa.") from exc


def _write_key_file(path: Path, data: bytes) -> None:
    try:
        Path(path).write_bytes(data)
    except PermissionError as exc:
        raise FileServiceError("Không có quyền ghi tệp khóa.") from exc
    except OSError as exc:
        raise FileServiceError("Không thể ghi tệp khóa.") from exc
