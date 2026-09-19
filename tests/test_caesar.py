"""Tests for the Caesar cipher."""

from app.crypto import caesar


def test_known_value_and_round_trip() -> None:
    encrypted = caesar.encrypt("ABC xyz", 3)
    assert encrypted == "DEF abc"
    assert caesar.decrypt(encrypted, 3) == "ABC xyz"


def test_large_and_negative_shifts() -> None:
    assert caesar.encrypt("Az", 29) == "Dc"
    assert caesar.encrypt("Def", -3) == "Abc"


def test_preserves_punctuation_and_unicode() -> None:
    text = "Hello, Việt Nam! 123"
    assert caesar.decrypt(caesar.encrypt(text, 11), 11) == text

