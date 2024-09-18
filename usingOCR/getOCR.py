import os
import pytesseract
import cv2
import numpy as np
import json
import re
from unidecode import unidecode

def clean_text(text: str) -> str:
    text = unidecode(text)
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    text = re.sub(r'\s+', ' ', text)
    text = text.lower().strip()
    return text

def addWhiteBlock(img_path: str) -> np.ndarray:
    image = cv2.imread(img_path)
    
    # Kiểm tra nếu ảnh không thể tải
    if image is None:
        print(f"Could not load image: {img_path}")
        return None
    
    # Thêm khối trắng vào vị trí 1
    output_image = image
    output_image[646:690, 0:1280] = (255, 255, 255)  # Khối trắng đầu tiên
    output_image[50:112, 1047:1195] = (255, 255, 255)  # Khối trắng thứ hai

    return output_image

# Cấu hình Tesseract nếu cần (Windows)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Đường dẫn đến root folder
root_folder = 'data/images'
output_folder = 'data/OCR'

# Đảm bảo rằng thư mục OCR tồn tại
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Duyệt qua tất cả các thư mục con trong thư mục gốc
'''
subdir: Đường dẫn đến thư mục hiện tại.
dirs: Danh sách các thư mục con trong thư mục hiện tại.
files: Danh sách các tập tin trong thư mục hiện tại.
'''
for subdir, dirs, files in os.walk(root_folder):
    if files:
        # Dictionary để lưu trữ dữ liệu
        data = {}

        # Lấy tên thư mục con hiện tại
        folder_name = os.path.basename(subdir)

        # Duyệt qua tất cả các file trong thư mục con
        for file in files:
            if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                image_path = os.path.join(subdir, file)
                img = addWhiteBlock(image_path)
                if img is None:
                    print(f"Could not load image: {image_path}")
                    continue  # Bỏ qua ảnh này nếu không thể tải

                print(f"Processing image: {image_path}")

                # Xử lý ảnh (chuyển đổi sang grayscale, CLAHE, sharpening)
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
                enhanced_image = clahe.apply(gray)

                kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
                sharpened = cv2.filter2D(enhanced_image, -1, kernel)

                # Thực hiện OCR
                try:
                    text = pytesseract.image_to_string(sharpened, lang='eng')
                except Exception as e:
                    print(f"Error processing image {image_path}: {e}")
                    continue  # Bỏ qua nếu có lỗi OCR
                
                # Làm sạch văn bản
                cleaned_text = clean_text(text)
                if cleaned_text:
                    image_key = os.path.basename(image_path)
                    data[image_key] = cleaned_text

        # Kiểm tra nếu có dữ liệu để lưu
        if data:
            json_filename = os.path.join(output_folder, f'{folder_name}.json')
            with open(json_filename, 'w', encoding='utf-8') as json_file:
                json.dump(data, json_file, ensure_ascii=False, indent=4)

            print(f"Hoàn tất xử lý hình ảnh và lưu file JSON tại {json_filename}.")