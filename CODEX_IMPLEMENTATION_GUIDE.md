# CODEX IMPLEMENTATION GUIDE — CryptoDesk

> Tài liệu này là chỉ dẫn triển khai trực tiếp cho Codex.
> Mục tiêu: xây dựng ứng dụng desktop Python hỗ trợ mã hóa, giải mã, hash, kiểm tra toàn vẹn và quản lý khóa ở mức bài tập lớn 2 người.
> Không tự ý mở rộng scope ngoài tài liệu này nếu chưa có yêu cầu mới.

---

# 1. Mục tiêu dự án

Tên đề xuất: **CryptoDesk**

Mô tả ngắn:

> Ứng dụng desktop bằng Python cho phép người dùng mã hóa/giải mã văn bản và file, tạo/quản lý khóa, tính/kiểm tra hash, thực hiện encoding cơ bản và lưu lịch sử thao tác an toàn.

Mục tiêu kỹ thuật:

- Thể hiện rõ kỹ năng Python, OOP, GUI, xử lý file, exception handling, database local và unit test.
- Dùng thư viện crypto chuẩn cho thuật toán hiện đại; không tự hiện thực AES/RSA.
- Có giao diện đủ hoàn chỉnh để demo trực tiếp.
- Code phải tách lớp rõ ràng, tránh nhét logic crypto vào GUI.
- Có test cho các luồng cốt lõi.
- Có thể đóng gói thành file chạy độc lập bằng PyInstaller ở giai đoạn cuối.

Độ khó mục tiêu: **3.5–4/5**.

---

# 2. Phạm vi bắt buộc

## 2.1. Chức năng bắt buộc

Ứng dụng phải có đầy đủ các chức năng sau:

1. Mã hóa/giải mã văn bản bằng Caesar Cipher.
2. Mã hóa/giải mã văn bản bằng Vigenere Cipher.
3. Mã hóa/giải mã văn bản bằng AES-256-GCM.
4. Mã hóa/giải mã văn bản ngắn bằng RSA-OAEP.
5. Mã hóa/giải mã file bằng AES-256-GCM.
6. Tạo AES key ngẫu nhiên.
7. Tạo RSA key pair.
8. Import/export RSA public/private key dạng PEM.
9. Tính SHA-256 và SHA-512 cho text/file.
10. Verify hash của file/text.
11. Base64 encode/decode.
12. Hex encode/decode.
13. Lưu lịch sử thao tác vào SQLite.
14. Không lưu plaintext, password, AES key raw hoặc private key vào history.
15. Validation và thông báo lỗi thân thiện.
16. Unit test cho crypto core và file encryption.
17. Giao diện PySide6 với sidebar và các trang chức năng.

## 2.2. Chức năng nâng cao, chỉ làm sau MVP

Chỉ triển khai khi toàn bộ MVP đã pass test:

- Digital signature RSA-PSS + SHA-256.
- Verify signature.
- Hybrid encryption AES + RSA.
- Drag & drop file.
- Dark/light theme.
- Batch encrypt/decrypt nhiều file.
- Password strength meter.

Không làm các chức năng trên trước khi hoàn thành MVP.

---

# 3. Ngoài phạm vi

Không triển khai các nội dung sau trong phiên bản bài tập lớn:

- Web backend.
- FastAPI/Django/Flask.
- Mobile app.
- Cloud sync.
- User account online.
- Thanh toán.
- Multi-tenant.
- Gửi file qua mạng.
- Tự cài đặt AES, RSA hoặc SHA từ đầu.
- Lưu private key hoặc password dạng plaintext vào database.

---

# 4. Tech stack bắt buộc

| Thành phần | Công nghệ |
|---|---|
| Ngôn ngữ | Python 3.11+ |
| GUI | PySide6 |
| Crypto hiện đại | cryptography |
| Database local | sqlite3 chuẩn Python |
| Test | pytest |
| Packaging | PyInstaller |

Dependencies tối thiểu:

```txt
PySide6
cryptography
pytest
pyinstaller
```

Không thêm ORM nếu chưa thật sự cần thiết.

---

# 5. Kiến trúc tổng thể

Phải tách GUI khỏi logic nghiệp vụ.

```text
                 PySide6 GUI
                     |
              Controller/Page
                     |
             Service / Crypto API
                     |
      +--------------+--------------+
      |              |              |
 Classical        Modern          Utility
 Caesar           AES-GCM         Hash
 Vigenere         RSA-OAEP        Base64/Hex
                     |
                File Service
                     |
                 File System

                     +

               History Service
                     |
                   SQLite
```

Quy tắc bắt buộc:

- UI không trực tiếp gọi `cryptography` APIs.
- UI chỉ gọi service layer.
- Service layer không import widget PySide6.
- Crypto core phải test được độc lập không cần GUI.

---

# 6. Cấu trúc thư mục

Codex phải tạo project theo cấu trúc sau:

```text
cryptodesk/
|
|-- main.py
|-- requirements.txt
|-- README.md
|-- .gitignore
|
|-- app/
|   |-- __init__.py
|   |
|   |-- ui/
|   |   |-- __init__.py
|   |   |-- main_window.py
|   |   |-- home_page.py
|   |   |-- encrypt_page.py
|   |   |-- decrypt_page.py
|   |   |-- file_page.py
|   |   |-- hash_page.py
|   |   |-- key_page.py
|   |   |-- encoding_page.py
|   |   |-- history_page.py
|   |   `-- widgets.py
|   |
|   |-- crypto/
|   |   |-- __init__.py
|   |   |-- caesar.py
|   |   |-- vigenere.py
|   |   |-- aes_service.py
|   |   |-- rsa_service.py
|   |   |-- hash_service.py
|   |   `-- encoding_service.py
|   |
|   |-- services/
|   |   |-- __init__.py
|   |   |-- file_service.py
|   |   |-- key_service.py
|   |   `-- history_service.py
|   |
|   |-- database/
|   |   |-- __init__.py
|   |   `-- database.py
|   |
|   `-- utils/
|       |-- __init__.py
|       |-- validators.py
|       `-- exceptions.py
|
|-- data/
|   `-- .gitkeep
|
|-- tests/
|   |-- test_caesar.py
|   |-- test_vigenere.py
|   |-- test_aes.py
|   |-- test_rsa.py
|   |-- test_hash.py
|   |-- test_encoding.py
|   `-- test_file_crypto.py
|
`-- CODEX_IMPLEMENTATION_GUIDE.md
```

---

# 7. Coding conventions

## 7.1. General

- Tuân thủ PEP 8.
- Tên biến/hàm bằng tiếng Anh.
- UI label có thể dùng tiếng Việt.
- Mỗi module chỉ đảm nhận một nhóm trách nhiệm.
- Mỗi hàm public cần type hints.
- Không dùng `except Exception:` nếu có thể bắt exception cụ thể.
- Không nuốt exception âm thầm.
- Không `print()` để báo lỗi trong GUI; phải hiển thị message box/status message.
- Không hard-code path tuyệt đối.
- Dùng `pathlib.Path` cho đường dẫn file.
- Không ghi key/password ra log.

## 7.2. Public service API

Các service nên trả dữ liệu hoặc raise custom exception.

Ví dụ:

```python
class CryptoError(Exception):
    pass

class InvalidKeyError(CryptoError):
    pass

class DecryptionError(CryptoError):
    pass
```

UI chịu trách nhiệm chuyển exception thành thông báo thân thiện.

---

# 8. Thiết kế GUI

## 8.1. Main window

Sử dụng `QMainWindow`.

Layout chính:

```text
+--------------------------------------------------+
| CryptoDesk                                       |
+-------------+------------------------------------+
| Home        |                                    |
| Encrypt     |                                    |
| Decrypt     |             Main page              |
| File        |                                    |
| Keys        |                                    |
| Hash        |                                    |
| Encoding    |                                    |
| History     |                                    |
| About       |                                    |
+-------------+------------------------------------+
```

Có thể dùng `QStackedWidget` để chuyển trang.

## 8.2. Quy chuẩn UI

- Có title rõ trên mỗi page.
- Button chính đặt cuối form.
- Có nút Clear.
- Có nút Copy với kết quả text.
- Có trạng thái success/error.
- Không để app crash khi người dùng nhập sai.
- Các action xử lý file lớn phải có feedback tối thiểu.

---

# 9. Module Caesar Cipher

File: `app/crypto/caesar.py`

Public API tối thiểu:

```python
def encrypt(text: str, shift: int) -> str:
    ...

def decrypt(text: str, shift: int) -> str:
    ...
```

Yêu cầu:

- Hỗ trợ A-Z và a-z.
- Giữ nguyên ký tự không phải alphabet.
- Chuẩn hóa shift bằng modulo 26.
- Decrypt phải là phép đảo của encrypt.

Ví dụ acceptance:

```text
encrypt("ABC xyz", 3) == "DEF abc"
decrypt("DEF abc", 3) == "ABC xyz"
```

---

# 10. Module Vigenere Cipher

File: `app/crypto/vigenere.py`

Public API:

```python
def encrypt(text: str, key: str) -> str:
    ...

def decrypt(text: str, key: str) -> str:
    ...
```

Yêu cầu:

- Key chỉ chấp nhận alphabet A-Z/a-z.
- Giữ nguyên ký tự ngoài alphabet.
- Chỉ tăng vị trí key khi xử lý chữ cái.
- Giữ case của plaintext.
- Key rỗng hoặc chứa ký tự không hợp lệ phải raise validation error.

---

# 11. AES-256-GCM

File: `app/crypto/aes_service.py`

Dùng `cryptography.hazmat.primitives.ciphers.aead.AESGCM`.

Không tự implement AES.

## 11.1. Key mode

Public API đề xuất:

```python
def generate_key() -> bytes:
    ...

def encrypt_bytes(data: bytes, key: bytes) -> bytes:
    ...

def decrypt_bytes(blob: bytes, key: bytes) -> bytes:
    ...
```

Key bắt buộc 32 bytes.

## 11.2. Blob format

Output encrypted blob phải tự chứa metadata cần thiết để decrypt.

Format đơn giản:

```text
MAGIC(8 bytes)
VERSION(1 byte)
NONCE(12 bytes)
CIPHERTEXT+TAG(variable)
```

Magic đề xuất:

```text
CRYPTO01
```

Lưu ý AESGCM của `cryptography` trả ciphertext đã kèm tag.

## 11.3. Nonce

- 12 bytes ngẫu nhiên.
- Mỗi lần encrypt phải tạo nonce mới.
- Không reuse nonce với cùng key.

## 11.4. Text display

Khi mã hóa text:

- blob bytes -> Base64 string để hiển thị.
- decrypt text: Base64 decode -> decrypt bytes -> UTF-8 decode.

## 11.5. Error handling

- Key sai độ dài -> `InvalidKeyError`.
- Blob sai magic/version -> `InvalidEncryptedDataError`.
- Auth tag fail -> `DecryptionError`.

Không hiển thị raw traceback cho người dùng.

---

# 12. Password-based AES

Đây là chức năng bắt buộc vì thân thiện hơn việc nhập raw AES key.

Sử dụng PBKDF2-HMAC-SHA256.

Public API đề xuất:

```python
def encrypt_with_password(data: bytes, password: str) -> bytes:
    ...

def decrypt_with_password(blob: bytes, password: str) -> bytes:
    ...
```

Format blob password mode:

```text
MAGIC
VERSION
MODE
SALT(16 bytes)
NONCE(12 bytes)
CIPHERTEXT+TAG
```

Yêu cầu:

- Salt random 16 bytes.
- Derive key 32 bytes.
- Iteration count đặt thành constant rõ ràng trong code.
- Không lưu password.
- Sai password phải dẫn tới authentication failure.

Không cần cho người dùng cấu hình iteration count ở GUI.

---

# 13. RSA-OAEP

File: `app/crypto/rsa_service.py`

Dùng:

- RSA 2048-bit hoặc 3072-bit.
- Public exponent 65537.
- OAEP.
- MGF1(SHA-256).
- SHA-256.

Public API đề xuất:

```python
def generate_key_pair(key_size: int = 2048) -> tuple[bytes, bytes]:
    """Return private_pem, public_pem."""


def encrypt_text(text: str, public_key_pem: bytes) -> str:
    """Return Base64 ciphertext."""


def decrypt_text(ciphertext_b64: str, private_key_pem: bytes, password: bytes | None = None) -> str:
    ...
```

Yêu cầu:

- RSA chỉ dùng cho text ngắn trong MVP.
- Nếu dữ liệu quá dài, phải báo rằng RSA không phù hợp cho dữ liệu lớn.
- Không dùng RSA để mã hóa file trực tiếp.

---

# 14. Key Manager

File service: `app/services/key_service.py`

GUI page: `app/ui/key_page.py`

Chức năng:

- Generate AES-256 key.
- Hiển thị AES key ở Base64.
- Copy AES key.
- Generate RSA key pair.
- Export public key PEM.
- Export private key PEM.
- Import public key PEM.
- Import private key PEM.
- Hiển thị thông tin cơ bản của key.

Không tự động lưu private key vào database.

Nếu export private key:

- Cho phép user chọn passphrase bảo vệ PEM.
- Nếu user bỏ trống passphrase, có thể export unencrypted PEM nhưng UI cần cảnh báo nhẹ.

---

# 15. File Encryption

File: `app/services/file_service.py`

Chức năng bắt buộc:

```python
def encrypt_file(input_path: Path, output_path: Path, key: bytes) -> None:
    ...

def decrypt_file(input_path: Path, output_path: Path, key: bytes) -> None:
    ...
```

Và password mode tương ứng.

MVP cho phép đọc file toàn bộ vào memory nếu file dưới giới hạn hợp lý.

Đặt giới hạn an toàn cho MVP, ví dụ 100 MB.

Nếu file lớn hơn giới hạn:

- Không crash.
- Báo cho user rằng phiên bản hiện tại chưa hỗ trợ file lớn hơn giới hạn.

Đuôi file output đề xuất:

```text
<original>.cdesk
```

Ví dụ:

```text
report.pdf -> report.pdf.cdesk
```

Khi decrypt, người dùng tự chọn output filename.

---

# 16. Hash Service

File: `app/crypto/hash_service.py`

Public API:

```python
def hash_text(text: str, algorithm: str = "sha256") -> str:
    ...

def hash_file(path: Path, algorithm: str = "sha256") -> str:
    ...

def verify_hash(actual: str, expected: str) -> bool:
    ...
```

Hỗ trợ:

- SHA-256.
- SHA-512.

Hash file phải đọc theo chunk, không đọc toàn file vào RAM.

Ví dụ:

```python
while chunk := f.read(1024 * 1024):
    hasher.update(chunk)
```

Normalize expected hash:

- trim whitespace.
- lowercase trước khi compare.

---

# 17. Encoding Service

File: `app/crypto/encoding_service.py`

Hỗ trợ:

- Base64 encode/decode.
- Hex encode/decode.

Public API:

```python
def base64_encode(text: str) -> str:
    ...

def base64_decode(value: str) -> str:
    ...

def hex_encode(text: str) -> str:
    ...

def hex_decode(value: str) -> str:
    ...
```

GUI phải ghi rõ:

> Base64/Hex là encoding, không phải encryption.

---

# 18. SQLite History

File: `app/database/database.py`

Database path mặc định:

```text
data/cryptodesk.db
```

Khi app start:

- Tạo folder `data/` nếu chưa có.
- Tạo database/table nếu chưa có.

Schema tối thiểu:

```sql
CREATE TABLE IF NOT EXISTS operation_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    operation TEXT NOT NULL,
    algorithm TEXT NOT NULL,
    input_type TEXT NOT NULL,
    source_name TEXT,
    success INTEGER NOT NULL,
    message TEXT,
    created_at TEXT NOT NULL
);
```

Lịch sử chỉ được lưu metadata.

TUYỆT ĐỐI không lưu:

- plaintext.
- ciphertext đầy đủ nếu không cần.
- password.
- raw AES key.
- private key.
- nội dung file.

---

# 19. History Service

File: `app/services/history_service.py`

Public API đề xuất:

```python
def add_history(
    operation: str,
    algorithm: str,
    input_type: str,
    source_name: str | None,
    success: bool,
    message: str | None = None,
) -> None:
    ...


def list_history(limit: int = 100) -> list[dict]:
    ...


def clear_history() -> None:
    ...
```

GUI history:

- Bảng hiển thị 100 record gần nhất.
- Có refresh.
- Có clear history với confirmation.

---

# 20. Validation

File: `app/utils/validators.py`

Phải có helper tối thiểu:

```python
def validate_aes_key_b64(value: str) -> bytes:
    ...

def validate_vigenere_key(value: str) -> str:
    ...

def validate_non_empty_text(value: str, field_name: str) -> str:
    ...
```

Các lỗi phổ biến phải xử lý:

- Text trống.
- Shift không phải số.
- Vigenere key rỗng.
- AES key Base64 không hợp lệ.
- AES key sai độ dài.
- RSA key PEM sai format.
- Ciphertext Base64 lỗi.
- File không tồn tại.
- File không đọc được.
- Output path trùng input path nếu thao tác có nguy cơ ghi đè.
- Password trống ở password mode.

---

# 21. Error messages

Không để message kỹ thuật kiểu traceback lên GUI.

Ví dụ tốt:

```text
Không thể giải mã dữ liệu.
Khóa hoặc mật khẩu có thể không đúng, hoặc dữ liệu đã bị thay đổi.
```

Ví dụ xấu:

```text
cryptography.exceptions.InvalidTag
```

Traceback chỉ dành cho development console/log nếu cần.

---

# 22. Trang Encrypt

Trang này hỗ trợ text.

Controls:

- Algorithm combobox:
  - Caesar
  - Vigenere
  - AES-256-GCM (Key)
  - AES-256-GCM (Password)
  - RSA-OAEP
- Input text area.
- Dynamic key/password field.
- Encrypt button.
- Result text area read-only.
- Copy result.
- Save result to TXT.
- Clear.

Khi đổi algorithm, UI phải thay phần key input tương ứng.

---

# 23. Trang Decrypt

Tương tự Encrypt.

- Ciphertext input.
- Algorithm.
- Key/password/private key.
- Decrypt button.
- Plaintext output.
- Copy/save/clear.

RSA decrypt phải cho chọn/import private PEM.

---

# 24. Trang File

Controls:

- Mode: Encrypt / Decrypt.
- Input file picker.
- Algorithm:
  - AES-256-GCM Key
  - AES-256-GCM Password
- Key/password field.
- Output path picker.
- Run button.
- Progress/status.

Sau thành công:

- Hiển thị output path.
- Ghi history.

---

# 25. Trang Hash

Controls:

- Input type: Text / File.
- Algorithm: SHA-256 / SHA-512.
- Calculate button.
- Hash result.
- Copy.
- Expected hash input.
- Verify button.

Kết quả verify:

```text
MATCH
```

hoặc

```text
NOT MATCH
```

---

# 26. Trang Encoding

Hai nhóm:

1. Base64.
2. Hex.

Mỗi nhóm:

- Input text.
- Encode.
- Decode.
- Output.

Có note:

> Encoding không cung cấp tính bí mật như encryption.

---

# 27. Home page

Home page hiển thị ngắn gọn:

- Giới thiệu CryptoDesk.
- Các module hỗ trợ.
- Cảnh báo: không dùng Caesar/Vigenere để bảo vệ dữ liệu thực tế.
- AES-GCM là lựa chọn chính cho bảo vệ dữ liệu trong app.
- Base64/Hex không phải mã hóa bảo mật.

Không cần dashboard phức tạp.

---

# 28. Logging history rule

Mỗi operation nên log:

Ví dụ encrypt text AES:

```text
operation = encrypt
algorithm = AES-256-GCM
input_type = text
source_name = NULL
success = 1
```

Ví dụ decrypt file fail:

```text
operation = decrypt
algorithm = AES-256-GCM
input_type = file
source_name = report.pdf.cdesk
success = 0
message = authentication failed
```

Message không chứa secret.

---

# 29. Security requirements

Codex phải tuân thủ các điểm sau:

1. AES dùng GCM, không dùng ECB.
2. Nonce phải random cho mỗi lần encrypt.
3. Password phải qua KDF trước khi dùng làm AES key.
4. RSA dùng OAEP, không dùng raw RSA.
5. Private key không lưu trong SQLite.
6. Không ghi key/password ra log/history.
7. Dữ liệu encrypt file phải có format header/version để validate.
8. Sai authentication tag phải fail closed, không trả plaintext partial.
9. Không tự viết thuật toán crypto hiện đại.
10. Không gọi Base64 là encryption trong UI hoặc README.

---

# 30. Unit tests bắt buộc

## 30.1. Caesar

- encrypt/decrypt round trip.
- shift > 26.
- shift âm.
- giữ punctuation.

## 30.2. Vigenere

- round trip.
- preserve punctuation.
- invalid key.

## 30.3. AES

- generated key dài 32 bytes.
- encrypt/decrypt round trip text bytes.
- cùng plaintext + same key nhưng hai lần encrypt cho ciphertext khác nhau do nonce.
- key sai -> decrypt fail.
- sửa 1 byte ciphertext -> decrypt fail.
- blob magic sai -> fail.

## 30.4. Password AES

- correct password -> round trip.
- wrong password -> fail.
- cùng plaintext/password, hai lần encrypt cho blob khác do salt/nonce.

## 30.5. RSA

- generate key pair.
- public encrypt/private decrypt round trip.
- decrypt bằng private key khác -> fail.
- invalid PEM -> fail.

## 30.6. Hash

- SHA-256 text known value.
- SHA-512 text known value.
- hash file ổn định.
- file đổi 1 byte -> hash đổi.
- verify hash case-insensitive.

## 30.7. Encoding

- Base64 round trip UTF-8.
- Hex round trip UTF-8.
- invalid Base64 -> validation error.
- invalid Hex -> validation error.

## 30.8. File crypto

Acceptance quan trọng nhất:

```text
SHA256(original) == SHA256(decrypt(encrypt(original)))
```

Test ít nhất với:

- TXT.
- binary file nhỏ.

---

# 31. Acceptance tests toàn dự án

Dự án chỉ được xem là hoàn thành MVP khi tất cả test sau pass:

| ID | Test | Expected |
|---|---|---|
| AT-01 | Caesar encrypt -> decrypt | Khôi phục đúng text |
| AT-02 | Vigenere encrypt -> decrypt | Khôi phục đúng text |
| AT-03 | AES text encrypt -> decrypt | Khôi phục đúng UTF-8 |
| AT-04 | AES dùng sai key | Fail, không trả plaintext |
| AT-05 | AES ciphertext bị sửa | Authentication fail |
| AT-06 | AES password đúng | Decrypt thành công |
| AT-07 | AES password sai | Fail |
| AT-08 | RSA public encrypt/private decrypt | Khôi phục text |
| AT-09 | RSA private key khác | Fail |
| AT-10 | Encrypt/decrypt file | SHA256 trước/sau giống nhau |
| AT-11 | SHA-256 same file | Cùng hash |
| AT-12 | File sửa 1 byte | Hash khác |
| AT-13 | Base64 round trip | Khôi phục text |
| AT-14 | Hex round trip | Khôi phục text |
| AT-15 | File không tồn tại | UI báo lỗi, app không crash |
| AT-16 | Key sai format | UI báo lỗi |
| AT-17 | History | Không có secret data |
| AT-18 | Clear history | Cần xác nhận trước khi xóa |

---

# 32. Development phases

Codex phải làm theo đúng thứ tự dưới đây.

## Phase 1 — Bootstrap

1. Tạo cấu trúc thư mục.
2. Tạo `requirements.txt`.
3. Tạo `.gitignore`.
4. Tạo `main.py` chạy cửa sổ PySide6 tối thiểu.
5. Tạo main window + sidebar + QStackedWidget.
6. Tạo placeholder pages.

Definition of done:

- `python main.py` mở app.
- Chuyển được giữa các page.

## Phase 2 — Classical crypto

1. Caesar implementation.
2. Vigenere implementation.
3. Unit tests.
4. Tích hợp vào Encrypt/Decrypt page.

Definition of done:

- Test pass.
- GUI chạy round trip được.

## Phase 3 — Hash + Encoding

1. SHA-256/SHA-512.
2. Hash file chunked.
3. Base64/Hex.
4. Unit tests.
5. GUI pages.

Definition of done:

- Hash/verify text + file hoạt động.
- Encoding round trip hoạt động.

## Phase 4 — AES Core

1. AES key generation.
2. AES-GCM blob format.
3. Key mode encrypt/decrypt.
4. Password mode PBKDF2.
5. Unit tests.

Definition of done:

- Tất cả AES tests pass.
- Wrong key/password fail đúng.
- Tampered ciphertext fail.

## Phase 5 — AES GUI

1. Tích hợp AES text vào Encrypt/Decrypt.
2. Generate key button.
3. Base64 key input.
4. Password mode.
5. Copy/save/clear.

Definition of done:

- Demo AES text hoàn chỉnh.

## Phase 6 — File Encryption

1. File service.
2. File size validation.
3. AES file encrypt/decrypt.
4. File GUI.
5. Unit tests.

Definition of done:

- Encrypt/decrypt file.
- SHA256 original == restored.

## Phase 7 — RSA

1. Generate RSA pair.
2. Import/export PEM.
3. RSA-OAEP text encrypt/decrypt.
4. RSA tests.
5. Keys page.
6. Tích hợp RSA text GUI.

Definition of done:

- Public encrypt/private decrypt thành công.

## Phase 8 — History

1. SQLite init.
2. History service.
3. Log operations.
4. History page.
5. Clear history confirmation.

Definition of done:

- Lịch sử hoạt động.
- Không có secret data trong DB.

## Phase 9 — UX + Error Handling

1. Chuẩn hóa message.
2. Disable nút khi input không hợp lệ nếu dễ thực hiện.
3. Confirmation khi ghi đè file.
4. Copy feedback.
5. About page.

## Phase 10 — Test + Packaging

1. Chạy toàn bộ pytest.
2. Sửa lỗi.
3. Test manual.
4. Viết README.
5. PyInstaller build.

---

# 33. Manual demo script

Khi demo bài tập lớn, app phải hỗ trợ luồng sau mà không cần chỉnh code:

1. Mở CryptoDesk.
2. Caesar: encrypt/decrypt `Hello PTIT`.
3. Vigenere: encrypt/decrypt một câu.
4. AES key mode:
   - Generate key.
   - Encrypt text.
   - Decrypt text.
5. Thay key khác -> decrypt fail.
6. AES password mode:
   - Encrypt bằng password.
   - Decrypt bằng password đúng.
   - Password sai -> fail.
7. File:
   - chọn một PDF/TXT/image nhỏ.
   - encrypt thành `.cdesk`.
   - decrypt về file mới.
   - so sánh SHA-256 trước/sau.
8. RSA:
   - generate key pair.
   - encrypt text bằng public key.
   - decrypt bằng private key.
9. Hash:
   - tính SHA-256 file.
   - verify hash.
10. Encoding:
   - Base64 encode/decode.
11. History:
   - xem các thao tác đã log.

---

# 34. README phải có

Codex phải tạo README gồm:

1. Tên dự án.
2. Mô tả.
3. Feature list.
4. Tech stack.
5. Cách cài môi trường.
6. Cách chạy app.
7. Cách chạy test.
8. Kiến trúc thư mục.
9. Giải thích ngắn các thuật toán.
10. Security notes.
11. Limitations.
12. Hướng phát triển.

Lệnh ví dụ:

```bash
python -m venv .venv
```

Linux/macOS:

```bash
source .venv/bin/activate
```

Windows:

```powershell
.venv\Scripts\Activate.ps1
```

Cài dependency:

```bash
pip install -r requirements.txt
```

Run:

```bash
python main.py
```

Test:

```bash
pytest -q
```

---

# 35. .gitignore tối thiểu

```gitignore
.venv/
__pycache__/
*.pyc
.pytest_cache/
build/
dist/
*.spec
*.db
*.pem
*.key
.env
.DS_Store
```

Lưu ý: không commit private key hoặc database demo có dữ liệu nhạy cảm.

---

# 36. PyInstaller

Sau khi app hoàn thiện, tạo build command tương tự:

```bash
pyinstaller --noconfirm --windowed --name CryptoDesk main.py
```

Nếu PySide6 thiếu plugin/resource, điều chỉnh build spec ở phase cuối.

Không dành thời gian packaging trước khi test core pass.

---

# 37. Quy tắc khi Codex thực thi

Codex phải tuân thủ:

1. Không làm toàn bộ project trong một thay đổi khổng lồ.
2. Làm từng phase.
3. Sau mỗi phase, chạy test liên quan.
4. Không sửa API public đã có nếu không cần thiết.
5. Nếu thay đổi format encrypted blob, cập nhật test ngay.
6. Không thêm dependency mới khi chưa có lý do rõ ràng.
7. Không bỏ test để làm code pass.
8. Không dùng mock cho crypto core.
9. Không tự implement AES/RSA.
10. Không lưu secret vào database/log.
11. Không chuyển dự án sang web.
12. Không thêm networking.
13. Khi có ambiguity nhỏ, chọn phương án đơn giản hơn nhưng phải giữ đúng security requirement.
14. Nếu gặp thay đổi làm tăng đáng kể scope, dừng và ghi rõ blocker thay vì tự mở rộng.

---

# 38. Definition of Done toàn dự án

Project được xem là hoàn thành khi:

- [ ] `python main.py` chạy thành công.
- [ ] Giao diện có đầy đủ các page chính.
- [ ] Caesar hoạt động.
- [ ] Vigenere hoạt động.
- [ ] AES-256-GCM key mode hoạt động.
- [ ] AES-256-GCM password mode hoạt động.
- [ ] RSA-OAEP text hoạt động.
- [ ] File encrypt/decrypt hoạt động.
- [ ] SHA-256/SHA-512 hoạt động.
- [ ] Verify hash hoạt động.
- [ ] Base64/Hex hoạt động.
- [ ] Key Manager hoạt động.
- [ ] History hoạt động.
- [ ] Không lưu secret trong history.
- [ ] Error handling không làm app crash với input sai thông thường.
- [ ] Tất cả pytest pass.
- [ ] README hoàn chỉnh.
- [ ] Có thể build PyInstaller hoặc có hướng dẫn build rõ ràng.

---

# 39. Feature ưu tiên nếu thiếu thời gian

Nếu deadline gần, ưu tiên theo thứ tự:

```text
P0:
AES text
AES file
Hash
GUI cơ bản
Error handling
Tests

P1:
Caesar
Vigenere
RSA
Key Manager
History
Encoding

P2:
Digital Signature
Hybrid Encryption
Theme
Drag & Drop
Batch processing
```

Tuy nhiên mục tiêu bài nộp là hoàn thành cả P0 + P1.

---

# 40. Gợi ý commit theo phase

```text
chore: bootstrap cryptodesk project
feat: implement caesar and vigenere ciphers
feat: add hash and encoding utilities
feat: implement aes-gcm crypto service
feat: integrate aes text workflow
feat: add aes file encryption
feat: implement rsa key management and oaep
feat: add sqlite operation history
feat: improve validation and error handling
test: complete crypto and file test suite
docs: add readme and packaging guide
```

---

# 41. Lưu ý học thuật cho báo cáo

Phần báo cáo nên phân biệt rõ:

- Encryption: AES, RSA.
- Classical cipher: Caesar, Vigenere.
- Hash: SHA-256, SHA-512; một chiều, không decrypt.
- Encoding: Base64, Hex; không cung cấp confidentiality.
- Symmetric encryption: AES dùng cùng key để encrypt/decrypt.
- Asymmetric encryption: RSA dùng public/private key pair.
- AEAD: AES-GCM vừa mã hóa vừa xác thực tính toàn vẹn.
- KDF: PBKDF2 chuyển password thành key phù hợp.

Không quảng cáo Caesar/Vigenere là an toàn cho dữ liệu thực tế.

---

# 42. Yêu cầu cuối cùng cho Codex

Hãy xây dựng dự án theo từng phase ở mục 32.

Ở mỗi phase:

1. Kiểm tra các file hiện có trước khi sửa.
2. Chỉ thay đổi những file cần thiết.
3. Giữ kiến trúc module đã quy định.
4. Viết hoặc cập nhật test tương ứng.
5. Chạy test sau khi hoàn thành phase.
6. Báo ngắn gọn:
   - file nào đã tạo/sửa;
   - tính năng nào hoàn thành;
   - test nào đã chạy;
   - blocker còn lại nếu có.

Không tự ý triển khai tính năng nâng cao trước khi MVP hoàn chỉnh.
