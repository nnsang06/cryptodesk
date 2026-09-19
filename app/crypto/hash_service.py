"""SHA-256 and SHA-512 hashing helpers."""

from __future__ import annotations

import hashlib
import hmac
from pathlib import Path

from app.utils.exceptions import ValidationError

SUPPORTED_ALGORITHMS = {"sha256", "sha512"}
CHUNK_SIZE = 1024 * 1024


def _new_hasher(algorithm: str) -> "hashlib._Hash":
    normalized = algorithm.lower().replace("-", "")
    if normalized not in SUPPORTED_ALGORITHMS:
        raise ValidationError("Chỉ hỗ trợ SHA-256 và SHA-512.")
    return hashlib.new(normalized)


def hash_text(text: str, algorithm: str = "sha256") -> str:
    """Return the hexadecimal digest of UTF-8 text."""
    hasher = _new_hasher(algorithm)
    hasher.update(text.encode("utf-8"))
    return hasher.hexdigest()


def hash_file(path: Path, algorithm: str = "sha256") -> str:
    """Hash a file incrementally without loading it fully into memory."""
    file_path = Path(path)
    if not file_path.exists():
        raise ValidationError("Tệp không tồn tại.")
    if not file_path.is_file():
        raise ValidationError("Đường dẫn đã chọn không phải là tệp.")
    hasher = _new_hasher(algorithm)
    try:
        with file_path.open("rb") as source:
            while chunk := source.read(CHUNK_SIZE):
                hasher.update(chunk)
    except PermissionError as exc:
        raise ValidationError("Không có quyền đọc tệp.") from exc
    except OSError as exc:
        raise ValidationError("Không thể đọc tệp để tính hash.") from exc
    return hasher.hexdigest()


def verify_hash(actual: str, expected: str) -> bool:
    """Compare hexadecimal digests after trimming whitespace and case."""
    actual_normalized = actual.strip().lower()
    expected_normalized = expected.strip().lower()
    if not actual_normalized or not expected_normalized:
        return False
    return hmac.compare_digest(actual_normalized, expected_normalized)

