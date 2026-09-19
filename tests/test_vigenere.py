"""Tests for the Vigenère cipher."""

import pytest

from app.crypto import vigenere
from app.utils.exceptions import ValidationError


def test_known_value_and_round_trip() -> None:
    encrypted = vigenere.encrypt("Attack at Dawn!", "LEMON")
    assert encrypted == "Lxfopv ef Rnhr!"
    assert vigenere.decrypt(encrypted, "LEMON") == "Attack at Dawn!"


def test_key_advances_only_for_ascii_letters() -> None:
    assert vigenere.encrypt("A-BC", "BC") == "B-DD"


@pytest.mark.parametrize("key", ["", "   ", "abc123", "khóa", "A-B"])
def test_invalid_key(key: str) -> None:
    with pytest.raises(ValidationError):
        vigenere.encrypt("hello", key)
