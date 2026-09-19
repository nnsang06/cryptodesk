"""Educational Vigenère cipher implementation for ASCII letters."""

from __future__ import annotations

from app.utils.validators import validate_vigenere_key


def _transform(text: str, key: str, decrypting: bool = False) -> str:
    valid_key = validate_vigenere_key(key).lower()
    shifts = [ord(character) - ord("a") for character in valid_key]
    result: list[str] = []
    key_index = 0

    for character in text:
        if "A" <= character <= "Z" or "a" <= character <= "z":
            base = ord("A") if character.isupper() else ord("a")
            shift = shifts[key_index % len(shifts)]
            if decrypting:
                shift = -shift
            result.append(chr((ord(character) - base + shift) % 26 + base))
            key_index += 1
        else:
            result.append(character)
    return "".join(result)


def encrypt(text: str, key: str) -> str:
    """Encrypt text with a Vigenère key, preserving case and punctuation."""
    return _transform(text, key)


def decrypt(text: str, key: str) -> str:
    """Decrypt text with a Vigenère key."""
    return _transform(text, key, decrypting=True)

