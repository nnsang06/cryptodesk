"""Tests for Base64 and hexadecimal encoding."""

import pytest

from app.crypto import encoding_service
from app.utils.exceptions import ValidationError


@pytest.mark.parametrize("text", ["Hello", "Xin chào Việt Nam 🔐", ""])
def test_base64_round_trip(text: str) -> None:
    assert encoding_service.base64_decode(encoding_service.base64_encode(text)) == text


@pytest.mark.parametrize("text", ["Hello", "Xin chào Việt Nam 🔐", ""])
def test_hex_round_trip(text: str) -> None:
    assert encoding_service.hex_decode(encoding_service.hex_encode(text)) == text


def test_invalid_base64_and_hex() -> None:
    with pytest.raises(ValidationError, match="Base64"):
        encoding_service.base64_decode("%%%")
    with pytest.raises(ValidationError, match="Hex"):
        encoding_service.hex_decode("not-hex")

