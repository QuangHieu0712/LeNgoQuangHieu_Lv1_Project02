import urllib.request
import urllib.error
import json
import pandas as pd
import time
from pathlib import Path

# Đoc dữ liệu từ file Excel
df = pd.read_excel("products-0-200000.xlsx")
product_ids = df["id"].dropna()

#  Tạo thư mục lưu kết quả nếu chưa tồn tại
output_dir = Path("data")
output_dir.mkdir(exist_ok=True)

 # Tạo danh sách để lưu trữ sản phẩm và sản phẩm lỗi
products = []
errors = []

# Thiết lập batch size và số file
batch_size = 1000
file_number = 1

# Hàm để lưu sản phẩm vào file JSON
def save_products(products, file_number):
    file_path = output_dir / f"products_{file_number:2d}.json"

    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(products, file, ensure_ascii=False, indent=2)

    print(f"Đã lưu {len(products)} sản phẩm vào {file_path}")


# Duyệt qua tất cả các product_id và lấy dữ liệu từ API
for product_id in product_ids:
    product_id = int(product_id)

    url = f"https://api.tiki.vn/product-detail/api/v1/products/{product_id}"

    request = urllib.request.Request(
        url,
        headers={"User-Agent": "Google"}
    )

    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            data = json.loads(response.read().decode("utf-8"))

        # Kiểm tra phản hồi có phải là dữ liệu sản phẩm không
        if not isinstance(data, dict) or not data.get("id"):
            raise ValueError("Phản hồi không có id sản phẩm")

        # Chỉ lấy các trường cần thiết từ dữ liệu sản phẩm
        images = data.get("images", [])

        if not isinstance(images, list):
            images = []

        product = {
            "id": data.get("id"),
            "name": data.get("name"),
            "url_key": data.get("url_key"),
            "price": data.get("price"),
            "description": data.get("description"),
            "images": [
                image.get("base_url")
                for image in images
                if isinstance(image, dict) and image.get("base_url")
            ]
        }

        products.append(product)
        print(f"Đã lấy dữ liệu sản phẩm: {product_id}")

        # Đủ 1000 sản phẩm, lưu vào file JSON và reset danh sách
        if len(products) == batch_size:
            save_products(products, file_number)
            file_number += 1
            products = []
    # Thêm loại xử lý lỗi để ghi lại các sản phẩm bị lỗi vào danh sách errors
    except urllib.error.HTTPError as e:
        errors.append({
            "product_id": product_id,
            "error": f"HTTP {e.code}"
        })
        print(f"Lỗi HTTP {e.code}: {product_id}")
    
    except Exception as e:
        errors.append({
            "product_id": product_id,
            "error": str(e)[:200]
        })
        print(f"Lỗi: {product_id} - {e}")

    # Chờ 1 giây giữa các yêu cầu để tránh bị chặn bởi server
    time.sleep(1)

# Lưu các sản phẩm còn lại nếu có
if products:
    save_products(products, file_number)

# Lưu danh sách sản phẩm lỗi vào file JSON
with open(output_dir / "errors.json", "w", encoding="utf-8") as file:
    json.dump(errors, file, ensure_ascii=False, indent=2)

print("\nKẾT QUẢ ")
print(f"Tổng mã đầu vào: {len(product_ids)}")
print(f"Sản phẩm thành công: {len(product_ids) - len(errors)}")
print(f"Số mã bị lỗi: {len(errors)}")
print(f"Thư mục kết quả: {output_dir}")
