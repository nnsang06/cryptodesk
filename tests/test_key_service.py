"""Tests for key import/export services."""

from pathlib import Path

import base64
import pytest

from app.services import key_service
from app.utils.exceptions import InvalidKeyError


def test_generate_aes_key_and_rsa_metadata() -> None:
    assert len(base64.b64decode(key_service.generate_aes_key_b64(), validate=True)) == 32
    private_pem, public_pem = key_service.generate_rsa_key_pair()
    assert key_service.public_key_metadata(public_pem)["bits"] == 2048
    assert key_service.private_key_metadata(private_pem)["bits"] == 2048


def test_import_export_public_and_encrypted_private_key(tmp_path: Path) -> None:
    private_pem, public_pem = key_service.generate_rsa_key_pair()
    public_path = tmp_path / "public.pem"
    private_path = tmp_path / "private.pem"
    key_service.export_public_key(public_pem, public_path)
    key_service.export_private_key(private_pem, private_path, "export-passphrase")

    assert key_service.import_public_key(public_path).startswith(b"-----BEGIN PUBLIC KEY-----")
    imported_private = key_service.import_private_key(private_path, "export-passphrase")
    assert b"ENCRYPTED PRIVATE KEY" in imported_private
    assert key_service.private_key_metadata(imported_private, "export-passphrase")["bits"] == 2048


def test_invalid_pem_is_rejected(tmp_path: Path) -> None:
    invalid = tmp_path / "invalid.pem"
    invalid.write_text("not a key")
    with pytest.raises(InvalidKeyError):
        key_service.import_public_key(invalid)

