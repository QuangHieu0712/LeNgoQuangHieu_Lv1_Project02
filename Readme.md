# Tiki Product Data Collection & Cleaning

## 1. Giới thiệu

Project sử dụng Python để thu thập dữ liệu sản phẩm từ Tiki Product Detail API và làm sạch trường `description` trước khi sử dụng cho các bước xử lý dữ liệu tiếp theo.

Quy trình gồm hai bước chính:

1. **Data Collection:** Đọc danh sách ID từ file Excel, gọi API Tiki và lưu thông tin sản phẩm vào các file JSON.
2. **Description Cleaning:** Đọc các file JSON, loại bỏ HTML tags, giải mã HTML entities và chuẩn hóa khoảng trắng trong trường `description`.

## 2. Công nghệ sử dụng

- Python: ngôn ngữ lập trình chính.
- Pandas: đọc danh sách ID từ Excel.
- urllib: gửi HTTP request đến API.
- JSON: đọc và ghi dữ liệu JSON.
- BeautifulSoup: loại bỏ HTML tags trong description.
- `html.unescape`: giải mã HTML entities.
- `re`: chuẩn hóa khoảng trắng bằng regular expressions.
- pathlib: quản lý đường dẫn file và thư mục.
- time: tạo khoảng nghỉ giữa các request.

## 3. Cấu trúc project

```text
project02/
├── crawl_data.py
├── clean_description.py
├── products-0-200000.xlsx
└── data/
    ├── products.json
    └── errors.json
```

Trong đó:

- `crawl_data.py`: thu thập dữ liệu sản phẩm từ API Tiki.
- `clean_description.py`: làm sạch trường description trong các file JSON.
- `products-0-200000.xlsx`: file Excel chứa danh sách ID sản phẩm, cần có cột `id`.
- `data/`: thư mục lưu dữ liệu sản phẩm và danh sách lỗi.
- `products_XXXX.json`: dữ liệu sản phẩm đã thu thập và sẽ được làm sạch.
- `errors.json`: thông tin về các ID gặp lỗi trong quá trình thu thập.

## 4. Cài đặt môi trường

Yêu cầu Python 3.9 trở lên và kết nối Internet để thu thập dữ liệu.

Cài đặt các thư viện cần thiết:

```bash
pip install pandas openpyxl beautifulsoup4
```

Các module `urllib`, `json`, `time`, `pathlib`, `html` và `re` thuộc thư viện chuẩn của Python nên không cần cài đặt riêng.

## 5. Bước 1: Thu thập dữ liệu sản phẩm

Chạy lệnh:

```bash
python crawl_data.py
```

Quy trình xử lý:

1. Đọc danh sách ID từ file Excel.
2. Loại bỏ các ID bị thiếu.
3. Tạo URL tương ứng với từng ID.
4. Gửi HTTP request đến Tiki Product Detail API.
5. Đọc và kiểm tra dữ liệu JSON trả về.
6. Lấy các trường `id`, `name`, `url_key`, `price`, `description` và `images`.
7. Lưu tối đa 1.000 sản phẩm thành công vào mỗi file JSON.
8. Ghi nhận lỗi vào `data/errors.json`.
9. In báo cáo tổng kết.

Chương trình tạm dừng 1 giây sau mỗi lượt xử lý ID để hạn chế việc gửi request liên tục.

### Các trường dữ liệu thu thập

| Trường | Mô tả |
|---|---|
| `id` | Mã sản phẩm |
| `name` | Tên sản phẩm |
| `url_key` | Khóa URL sản phẩm |
| `price` | Giá sản phẩm |
| `description` | Mô tả sản phẩm từ API |
| `images` | Danh sách URL hình ảnh lấy từ trường `base_url` |

Ở bước này, description được lưu theo dữ liệu API trả về, chưa qua bước làm sạch HTML.

## 6. Bước 2: Làm sạch description

Chạy lệnh:

```bash
python clean_description.py
```

Script duyệt qua các file có tên khớp với mẫu `products_*.json` trong thư mục `data/`.

Các thao tác làm sạch bao gồm:

1. Đọc nội dung JSON từ file.
2. Trích xuất văn bản từ description bằng BeautifulSoup.
3. Giải mã HTML entities bằng `html.unescape`.
4. Chuẩn hóa khoảng trắng bằng regular expressions.
5. Ghi dữ liệu đã làm sạch trở lại file JSON tương ứng.

### Các kỹ thuật làm sạch

**Loại bỏ HTML tags**

```python
BeautifulSoup(str(description), "html.parser").get_text(" ", strip=True)
```

Trích xuất văn bản từ HTML và loại bỏ các thẻ như `<p>`, `<div>`, `<br>`.

**Giải mã HTML entities**

```python
unescape(description)
```

Chuyển các ký tự được mã hóa HTML về dạng dễ đọc, ví dụ `&amp;` thành `&`.

**Chuẩn hóa khoảng trắng**

```python
re.sub(r"\s+", " ", description).strip()
```

- `\s+`: tìm một hoặc nhiều ký tự khoảng trắng liên tiếp.
- Thay chúng bằng một dấu cách.
- `strip()`: loại bỏ khoảng trắng ở đầu và cuối chuỗi.

### Ví dụ

Trước khi làm sạch:

```html
<p>Sản phẩm&nbsp;chính hãng</p>
<div>Chất liệu cao cấp</div>
```

Sau khi làm sạch:

```text
Sản phẩm chính hãng Chất liệu cao cấp
```

### Lưu ý về file đầu ra

Script `clean_description.py` hiện tại ghi dữ liệu trở lại chính các file `products_*.json` ban đầu, không tạo thư mục đầu ra riêng.

Vì vậy, nên chạy bước thu thập dữ liệu trước rồi mới chạy bước làm sạch description.

## 7. Xử lý lỗi

Trong bước thu thập dữ liệu, các lỗi HTTP và các lỗi xử lý khác được ghi vào `data/errors.json`.

Ví dụ:

```json
[
  {
    "product_id": 1003,
    "error": "HTTP 404"
  }
]
```

Script làm sạch chỉ xử lý các file khớp mẫu `products_*.json`, không xử lý `errors.json`.

Chương trình hiện chưa có cơ chế tự động thử lại các ID thất bại.

## 8. Kết quả đầu ra

Sau khi hoàn thành cả hai bước, project có:

- Các file JSON chứa thông tin sản phẩm đã thu thập.
- Trường `description` đã được làm sạch HTML và chuẩn hóa khoảng trắng.
- File `errors.json` lưu thông tin các ID gặp lỗi khi thu thập.

Các file sản phẩm được cập nhật trực tiếp trong thư mục `data/`.

## 9. Lưu ý

- Đảm bảo file Excel có cột `id` và nằm đúng đường dẫn.
- Chạy `crawl_data.py` trước `clean_description.py`.
- Script làm sạch ghi đè file JSON hiện tại, vì vậy dữ liệu description gốc có thể không còn nguyên vẹn sau khi làm sạch.
- Thời gian thu thập phụ thuộc vào số lượng ID, tốc độ phản hồi API và lỗi phát sinh.
- Cần tuân thủ điều khoản sử dụng và chính sách truy cập dữ liệu của Tiki.
