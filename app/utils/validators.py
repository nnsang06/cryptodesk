"""Input validation shared by services and user-interface pages."""

from __future__ import annotations

import base64
import binascii
from pathlib import Path

from app.utils.exceptions import InvalidKeyError, ValidationError


def validate_aes_key_b64(value: str) -> bytes:
    """Decode and validate a Base64-encoded AES-256 key."""
    normalized = value.strip()
    if not normalized:
        raise InvalidKeyError("Vui lòng nhập khóa AES.")
    try:
        key = base64.b64decode(normalized, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise InvalidKeyError("Khóa AES phải là Base64 hợp lệ.") from exc
    if len(key) != 32:
        raise InvalidKeyError("Khóa AES-256 phải có đúng 32 byte.")
    return key


def validate_vigenere_key(value: str) -> str:
    """Return a normalized Vigenere key containing only ASCII letters."""
    key = value.strip()
    if not key:
        raise ValidationError("Vui lòng nhập khóa Vigenère.")
    if not key.isascii() or not key.isalpha():
        raise ValidationError("Khóa Vigenère chỉ được chứa chữ cái A-Z hoặc a-z.")
    return key


def validate_non_empty_text(value: str, field_name: str) -> str:
    """Ensure a text input contains at least one non-whitespace character."""
    if not value.strip():
        raise ValidationError(f"{field_name} không được để trống.")
    return value


def validate_password(value: str) -> str:
    """Ensure a password is not empty without otherwise constraining it."""
    if not value:
        raise ValidationError("Vui lòng nhập mật khẩu.")
    return value


def validate_existing_file(path: Path) -> Path:
    """Ensure a path identifies a readable regular file."""
    candidate = Path(path)
    if not candidate.exists():
        raise ValidationError("Tệp không tồn tại.")
    if not candidate.is_file():
        raise ValidationError("Đường dẫn đã chọn không phải là tệp.")
    try:
        with candidate.open("rb"):
            pass
    except PermissionError as exc:
        raise ValidationError("Không có quyền đọc tệp.") from exc
    except OSError as exc:
        raise ValidationError("Không thể đọc tệp đã chọn.") from exc
    return candidate


def validate_distinct_paths(input_path: Path, output_path: Path) -> None:
    """Reject an output path that points to the input file."""
    if Path(input_path).resolve() == Path(output_path).resolve():
        raise ValidationError("Tệp đầu ra phải khác tệp đầu vào.")

