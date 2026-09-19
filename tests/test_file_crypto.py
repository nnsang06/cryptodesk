"""Tests for AES-GCM file encryption services."""

from pathlib import Path

import pytest

from app.crypto import aes_service, hash_service
from app.services import file_service
from app.utils.exceptions import DecryptionError, ValidationError


@pytest.mark.parametrize(
    "name,content",
    [
        ("message.txt", "Nội dung UTF-8".encode()),
        ("image.bin", bytes(range(256)) * 4),
    ],
)
def test_key_file_round_trip(tmp_path: Path, name: str, content: bytes) -> None:
    source = tmp_path / name
    encrypted = tmp_path / f"{name}.cdesk"
    restored = tmp_path / f"restored-{name}"
    source.write_bytes(content)
    key = aes_service.generate_key()

    file_service.encrypt_file(source, encrypted, key)
    file_service.decrypt_file(encrypted, restored, key)

    assert hash_service.hash_file(source) == hash_service.hash_file(restored)


def test_password_file_round_trip_and_wrong_password(tmp_path: Path) -> None:
    source = tmp_path / "archive.zip"
    encrypted = tmp_path / "archive.zip.cdesk"
    restored = tmp_path / "archive-restored.zip"
    source.write_bytes(b"PK\x03\x04" + bytes(range(128)))

    file_service.encrypt_file_with_password(source, encrypted, "strong password")
    file_service.decrypt_file_with_password(encrypted, restored, "strong password")
    assert restored.read_bytes() == source.read_bytes()

    with pytest.raises(DecryptionError):
        file_service.decrypt_file_with_password(encrypted, restored, "wrong")


def test_missing_file_and_same_output_are_rejected(tmp_path: Path) -> None:
    key = aes_service.generate_key()
    with pytest.raises(ValidationError, match="không tồn tại"):
        file_service.encrypt_file(tmp_path / "missing", tmp_path / "out", key)

    source = tmp_path / "same"
    source.write_bytes(b"content")
    with pytest.raises(ValidationError, match="khác"):
        file_service.encrypt_file(source, source, key)


def test_tampered_file_fails_without_writing_plaintext(tmp_path: Path) -> None:
    source = tmp_path / "source"
    encrypted = tmp_path / "encrypted"
    output = tmp_path / "output"
    source.write_bytes(b"sensitive file")
    key = aes_service.generate_key()
    file_service.encrypt_file(source, encrypted, key)
    blob = bytearray(encrypted.read_bytes())
    blob[-1] ^= 1
    encrypted.write_bytes(blob)

    with pytest.raises(DecryptionError):
        file_service.decrypt_file(encrypted, output, key)
    assert not output.exists()

