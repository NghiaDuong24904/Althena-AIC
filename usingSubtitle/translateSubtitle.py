import os
import re
from utils.query_processing import Translation

# Đọc nội dung của một file .txt
def read_file(file):
    with open(file, 'r', encoding='utf-8') as f:
        return f.read()
    
# Lưu nội dung đã chỉnh sửa trở lại file
def save_file(file, content):
    with open(file, 'w', encoding='utf-8') as f:
        f.write(content)

# Hàm chia văn bản thành các cụm 500 từ
def split_into_chunks(text, chunk_size=500):
    words = text.split()
    return [' '.join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]

# Sửa đổi nội dung: loại bỏ text trong ngoặc [] và dịch các cụm 500 từ
def modify_content(content):
    # Bước 1: Loại bỏ đoạn văn bản trong ngoặc []
    cleaned_text = re.sub(r'\[.*?\]', '', content)

    # Bước 2: Chia nội dung thành các cụm 100 từ
    chunks = split_into_chunks(cleaned_text, chunk_size=100)
    
    # Bước 3: Khởi tạo đối tượng dịch
    translator = Translation(from_lang='vi', to_lang='en')

    # Bước 4: Dịch từng cụm văn bản và gộp lại
    translated_chunks = [translator(chunk) for chunk in chunks]
    translated_text = ' '.join(translated_chunks)  # Gộp lại thành văn bản hoàn chỉnh

    print("Đã dịch nội dung")
    return translated_text

def main():
    subtitle_folder = 'data/subtitle/txt'

    # Lặp qua từng file trong thư mục và xử lý chúng
    for file_name in os.listdir(subtitle_folder):
        file_path = os.path.join(subtitle_folder, file_name)
        
        # Chỉ xử lý các file .txt và bỏ qua các file _errors.txt
        if file_name.endswith(".txt") and not file_name.endswith("_errors.txt") and not file_name.endswith("_translated.txt") and not file_name.endswith("_noSub.txt"):
            print(f"Đang xử lý file: {file_name}")

            # Bước 1: Đọc file
            content = read_file(file_path)

            # Bước 2: Sửa đổi nội dung
            modified_content = modify_content(content)

            file_path = file_path.replace('.txt', '_translated.txt')

            # Bước 3: Lưu lại nội dung đã sửa
            save_file(file_path, modified_content)

            print(f"Đã lưu file: {file_name}")

if __name__ == "__main__":
    main()