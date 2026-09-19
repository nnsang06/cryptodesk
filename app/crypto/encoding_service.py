"""UTF-8 Base64 and hexadecimal encoding helpers."""

from __future__ import annotations

import base64
import binascii

from app.utils.exceptions import ValidationError


def base64_encode(text: str) -> str:
    """Encode UTF-8 text as Base64."""
    return base64.b64encode(text.encode("utf-8")).decode("ascii")


def base64_decode(value: str) -> str:
    """Decode validated Base64 into UTF-8 text."""
    try:
        decoded = base64.b64decode(value.strip(), validate=True)
        return decoded.decode("utf-8")
    except (binascii.Error, ValueError) as exc:
        raise ValidationError("Dữ liệu đầu vào không phải Base64 hợp lệ.") from exc
    except UnicodeDecodeError as exc:
        raise ValidationError("Base64 không chứa văn bản UTF-8 hợp lệ.") from exc


def hex_encode(text: str) -> str:
    """Encode UTF-8 text as hexadecimal."""
    return text.encode("utf-8").hex()


def hex_decode(value: str) -> str:
    """Decode validated hexadecimal into UTF-8 text."""
    try:
        decoded = bytes.fromhex(value.strip())
        return decoded.decode("utf-8")
    except ValueError as exc:
        raise ValidationError("Dữ liệu đầu vào không phải Hex hợp lệ.") from exc
    except UnicodeDecodeError as exc:
        raise ValidationError("Hex không chứa văn bản UTF-8 hợp lệ.") from exc

