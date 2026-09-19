"""Bounded in-memory AES-GCM encryption for arbitrary files."""

from __future__ import annotations

import os
import tempfile
from collections.abc import Callable
from pathlib import Path

from app.crypto import aes_service
from app.utils.exceptions import CryptoDeskError, FileServiceError
from app.utils.validators import validate_distinct_paths, validate_existing_file

MAX_FILE_SIZE = 100 * 1024 * 1024


def _read_input(input_path: Path) -> bytes:
    path = validate_existing_file(input_path)
    try:
        if path.stat().st_size > MAX_FILE_SIZE:
            raise FileServiceError("Phiên bản hiện tại chỉ hỗ trợ tệp tối đa 100 MB.")
        return path.read_bytes()
    except PermissionError as exc:
        raise FileServiceError("Không có quyền đọc tệp đầu vào.") from exc
    except OSError as exc:
        raise FileServiceError("Không thể đọc tệp đầu vào.") from exc


def _write_output(output_path: Path, data: bytes) -> None:
    path = Path(output_path)
    parent = path.parent
    if not parent.exists() or not parent.is_dir():
        raise FileServiceError("Thư mục đầu ra không tồn tại.")
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb",
            dir=parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as temporary:
            temporary.write(data)
            temporary_path = Path(temporary.name)
        os.replace(temporary_path, path)
    except PermissionError as exc:
        raise FileServiceError("Không có quyền ghi tệp đầu ra.") from exc
    except OSError as exc:
        raise FileServiceError("Không thể ghi tệp đầu ra.") from exc
    finally:
        if temporary_path is not None and temporary_path.exists():
            try:
                temporary_path.unlink()
            except OSError:
                pass


def _process_file(
    input_path: Path,
    output_path: Path,
    processor: Callable[[bytes], bytes],
) -> None:
    validate_distinct_paths(input_path, output_path)
    data = _read_input(input_path)
    try:
        result = processor(data)
    except CryptoDeskError:
        raise
    _write_output(output_path, result)


def encrypt_file(input_path: Path, output_path: Path, key: bytes) -> None:
    """Encrypt a file with an AES-256 key."""
    _process_file(input_path, output_path, lambda data: aes_service.encrypt_bytes(data, key))


def decrypt_file(input_path: Path, output_path: Path, key: bytes) -> None:
    """Decrypt a key-mode CryptoDesk file."""
    _process_file(input_path, output_path, lambda data: aes_service.decrypt_bytes(data, key))


def encrypt_file_with_password(
    input_path: Path,
    output_path: Path,
    password: str,
) -> None:
    """Encrypt a file using a password-derived AES-256 key."""
    _process_file(
        input_path,
        output_path,
        lambda data: aes_service.encrypt_with_password(data, password),
    )


def decrypt_file_with_password(
    input_path: Path,
    output_path: Path,
    password: str,
) -> None:
    """Decrypt a password-mode CryptoDesk file."""
    _process_file(
        input_path,
        output_path,
        lambda data: aes_service.decrypt_with_password(data, password),
    )
