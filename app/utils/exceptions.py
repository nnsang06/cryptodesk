"""Application-specific exceptions exposed by the service layer."""


class CryptoDeskError(Exception):
    """Base class for errors that can be shown safely in the UI."""


class ValidationError(CryptoDeskError):
    """Raised when user-provided input is invalid."""


class CryptoError(CryptoDeskError):
    """Base class for cryptographic operation failures."""


class InvalidKeyError(CryptoError):
    """Raised when a cryptographic key is invalid or unsupported."""


class InvalidEncryptedDataError(CryptoError):
    """Raised when encrypted data has an invalid format."""


class DecryptionError(CryptoError):
    """Raised when authenticated decryption fails."""


class FileServiceError(CryptoDeskError):
    """Raised for safe, user-facing file operation failures."""


class DatabaseError(CryptoDeskError):
    """Raised when the local history database cannot be accessed."""

