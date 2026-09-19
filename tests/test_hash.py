"""Tests for SHA hashing helpers."""

import hashlib

import pytest

from app.crypto import hash_service
from app.utils.exceptions import ValidationError


def test_known_text_hashes() -> None:
    assert hash_service.hash_text("abc", "sha256") == hashlib.sha256(b"abc").hexdigest()
    assert hash_service.hash_text("abc", "SHA-512") == hashlib.sha512(b"abc").hexdigest()


def test_file_hash_is_stable_and_changes_with_content(tmp_path) -> None:
    path = tmp_path / "sample.bin"
    path.write_bytes(b"first")
    original = hash_service.hash_file(path)
    assert hash_service.hash_file(path) == original
    path.write_bytes(b"firsu")
    assert hash_service.hash_file(path) != original


def test_verify_hash_is_case_insensitive() -> None:
    digest = hash_service.hash_text("value")
    assert hash_service.verify_hash(digest, f"  {digest.upper()}\n")
    assert not hash_service.verify_hash(digest, "")


def test_invalid_algorithm_and_missing_file(tmp_path) -> None:
    with pytest.raises(ValidationError):
        hash_service.hash_text("text", "md5")
    with pytest.raises(ValidationError, match="không tồn tại"):
        hash_service.hash_file(tmp_path / "missing")

