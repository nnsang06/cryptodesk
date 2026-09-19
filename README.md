# CryptoDesk

CryptoDesk là ứng dụng desktop Python phục vụ học tập và demo các thao tác mật
mã phổ biến. Ứng dụng chạy hoàn toàn cục bộ, tách giao diện PySide6 khỏi crypto
core và service layer để dễ kiểm thử, bảo trì.

## Chức năng

- Mã hóa/giải mã text bằng Caesar và Vigenère.
- Mã hóa/giải mã text bằng AES-256-GCM với khóa ngẫu nhiên hoặc mật khẩu.
- Mã hóa/giải mã text ngắn bằng RSA-OAEP.
- Mã hóa/giải mã mọi loại tệp (tối đa 100 MB) bằng AES-256-GCM.
- Tạo khóa AES-256 và RSA 2048/3072 bit.
- Import/export RSA public/private key dạng PEM; private key có thể được bảo vệ
  bằng passphrase khi export.
- Tính và kiểm tra SHA-256/SHA-512 cho text hoặc tệp.
- Base64 và Hex encode/decode UTF-8.
- Lưu metadata lịch sử thao tác vào SQLite, có làm mới và xóa có xác nhận.
- Validation và thông báo lỗi thân thiện, không hiển thị traceback trên GUI.

## Tech stack

- Python 3.11+
- PySide6
- `cryptography`
- SQLite (`sqlite3` trong standard library)
- pytest
- PyInstaller

## Cấu trúc project

```text
cryptodesk/
├── main.py
├── requirements.txt
├── README.md
├── app/
│   ├── crypto/       # Caesar, Vigenère, AES, RSA, hash, encoding
│   ├── services/     # File, key và history services
│   ├── database/     # SQLite initialization
│   ├── utils/        # Validation và custom exceptions
│   └── ui/           # Main window và 9 trang PySide6
├── data/             # SQLite runtime database (không commit)
└── tests/            # Unit, integration và UI smoke tests
```

## Cài đặt

Tạo virtual environment:

```bash
python -m venv .venv
```

Linux/macOS:

```bash
source .venv/bin/activate
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Cài dependency:

```bash
python -m pip install -r requirements.txt
```

Nếu hệ thống chỉ cung cấp lệnh `python3`, thay `python` bằng `python3` trong các
lệnh tương ứng.

## Chạy ứng dụng

Từ thư mục gốc project:

```bash
python main.py
```

Database `data/cryptodesk.db` và bảng history được tạo tự động ở lần chạy đầu.

## Hướng dẫn sử dụng nhanh

### Encrypt / Decrypt

1. Chọn cùng một thuật toán ở hai trang.
2. Nhập plaintext/ciphertext và tham số tương ứng:
   - Caesar: shift số nguyên.
   - Vigenère: khóa chỉ gồm A-Z/a-z.
   - AES key: khóa 32 byte dạng Base64; trang Encrypt có nút tạo khóa.
   - AES password: mật khẩu được dẫn xuất bằng PBKDF2, không dùng trực tiếp.
   - RSA: chọn public PEM để encrypt hoặc private PEM để decrypt.
3. Chọn **Mã hóa/Giải mã**; có thể sao chép hoặc lưu kết quả ra TXT.

### File

1. Chọn Mã hóa hoặc Giải mã và chế độ Khóa AES hoặc Mật khẩu.
2. Chọn tệp nguồn, tệp đích và nhập secret tương ứng.
3. Chạy thao tác. Tệp mã hóa mặc định có hậu tố `.cdesk`.

File mã hóa không phụ thuộc extension gốc. Khi giải mã, chọn tên output mong
muốn. Nếu output đã tồn tại, ứng dụng luôn hỏi xác nhận trước khi ghi đè.

### Keys

- Tạo và sao chép khóa AES Base64.
- Tạo RSA key pair 2048/3072 bit trong bộ nhớ.
- Import/export từng public/private PEM.
- Nên nhập passphrase ở ô export để bảo vệ private key trên đĩa.

### Hash

Chọn Text/Tệp và SHA-256/SHA-512, tính digest, sau đó dán digest mong đợi để
nhận kết quả `MATCH` hoặc `NOT MATCH`.

### Encoding

Hai panel Base64 và Hex cho phép encode/decode text UTF-8 độc lập.

### History

Hiển thị tối đa 100 thao tác mới nhất. History chỉ chứa metadata như thao tác,
thuật toán, loại input, tên tệp, trạng thái và thời gian.

## Thuật toán

- **Caesar:** dịch mỗi chữ cái một số vị trí cố định; chỉ phù hợp học thuật.
- **Vigenère:** sử dụng chuỗi dịch chuyển từ khóa; vẫn không an toàn cho dữ liệu
  thực tế.
- **AES-256-GCM:** mã hóa đối xứng có xác thực, phát hiện ciphertext bị sửa.
- **RSA-OAEP:** mã hóa bất đối xứng cho text ngắn bằng public/private key pair.
- **SHA-256/SHA-512:** hash một chiều để kiểm tra toàn vẹn, không thể decrypt.
- **Base64/Hex:** biểu diễn dữ liệu, không cung cấp confidentiality.

## Security notes

- AES luôn dùng khóa 256 bit, GCM và nonce ngẫu nhiên 12 byte cho mỗi lần mã hóa.
- Payload chứa magic, version, mode, nonce và salt khi cần để validate trước khi
  giải mã; header được xác thực bằng AAD.
- Password mode dùng PBKDF2-HMAC-SHA256 với salt ngẫu nhiên 16 byte và số vòng
  cố định trong code.
- RSA dùng OAEP + MGF1 + SHA-256; không dùng textbook RSA và không mã hóa file
  trực tiếp.
- Lỗi authentication fail closed, không ghi plaintext một phần ra output.
- History không lưu plaintext, ciphertext đầy đủ, password, AES key hay private
  key. Nội dung message tùy ý cũng bị thay bằng thông báo an toàn.
- Private key chỉ nằm trong bộ nhớ phiên làm việc và file do người dùng chủ động
  chọn; không được lưu trong SQLite.

## Chạy test

```bash
pytest -q
```

Trên Linux headless/CI:

```bash
QT_QPA_PLATFORM=offscreen pytest -q
```

Test bao phủ classical cipher, AES key/password, RSA, hash, encoding, file
round-trip/tampering, key import/export, history secret handling và UI smoke.

## Build executable

Kích hoạt virtual environment rồi chạy:

```bash
pyinstaller --noconfirm --clean --windowed --name CryptoDesk main.py
```

Executable được tạo trong `dist/CryptoDesk/` (hoặc `dist/CryptoDesk.exe` tùy hệ
điều hành). Nên chạy thử build trên chính hệ điều hành dùng để phân phối vì
PyInstaller không cross-compile giữa Windows, macOS và Linux.

## Giới hạn

- Mỗi lần xử lý tối đa 100 MB và file được đọc vào bộ nhớ trong MVP.
- RSA-OAEP chỉ dùng cho text ngắn; giới hạn phụ thuộc kích thước RSA key.
- Không có secure key vault; người dùng tự chịu trách nhiệm lưu khóa/passphrase.
- Không có cloud sync, tài khoản online, networking hay batch processing.
- Caesar và Vigenère chỉ dành cho minh họa học thuật.

## Hướng phát triển

Sau MVP có thể bổ sung chữ ký số RSA-PSS, hybrid encryption, xử lý file dạng
stream, drag-and-drop và batch processing. Các tính năng này hiện không thuộc
scope của phiên bản này.
