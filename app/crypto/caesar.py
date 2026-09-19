"""Educational Caesar cipher implementation for ASCII letters."""

from __future__ import annotations


def _transform(text: str, shift: int) -> str:
    normalized_shift = shift % 26
    result: list[str] = []
    for character in text:
        if "A" <= character <= "Z":
            result.append(chr((ord(character) - ord("A") + normalized_shift) % 26 + ord("A")))
        elif "a" <= character <= "z":
            result.append(chr((ord(character) - ord("a") + normalized_shift) % 26 + ord("a")))
        else:
            result.append(character)
    return "".join(result)


def encrypt(text: str, shift: int) -> str:
    """Encrypt text by rotating ASCII letters by ``shift`` positions."""
    return _transform(text, shift)


def decrypt(text: str, shift: int) -> str:
    """Decrypt Caesar ciphertext using the supplied shift."""
    return _transform(text, -shift)

