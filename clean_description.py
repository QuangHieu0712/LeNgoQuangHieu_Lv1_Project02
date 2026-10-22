
import json
import re
from pathlib import Path
from bs4 import BeautifulSoup
from html import unescape

# Thư mục chứa các file JSON sản phẩm
data_dir = Path("data")

# Duyệt qua tất cả các file JSON trong thư mục
for file_path in data_dir.glob("products_*.json"):
    with open(file_path, "r", encoding="utf-8") as file:
        products = json.load(file)
# Chuẩn hóa description cho từng sản phẩm
    for product in products:
        description = product.get("description")

        if description:
            # Chuyển description từ HTML sang text
            description = BeautifulSoup(
                str(description), "html.parser"
            ).get_text(" ", strip=True)

            # Chuyển các ký tự HTML thành ký tự bình thường
            description = unescape(description)

            # Gộp các khoảng trắng liên tiếp thành một khoảng trắng và loại bỏ khoảng trắng đầu/cuối
            description = re.sub(r"\s+", " ", description).strip()

            product["description"] = description

    # Lưu các sản phẩm đã chuẩn hóa vào file JSON mới
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(products, file, ensure_ascii=False, indent=2)

    print(f"Đã chuẩn hóa description: {file_path}")

print("Hoàn thành chuẩn hóa  description!")
