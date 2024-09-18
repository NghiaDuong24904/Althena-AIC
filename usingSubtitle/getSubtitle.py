import json
import os
import re
from youtube_transcript_api import YouTubeTranscriptApi

# Hàm lấy phụ đề Tiếng Việt từ video YouTube
def get_subtitle(video_id, languages=['vi']):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=languages)
        return transcript
    except Exception as e:
        return str(e)

# Hàm trích xuất video ID từ link YouTube
def extract_video_id(youtube_url):
    # Do ID video YouTube có độ dài cố định là 11 ký tự và nằm sau ký tự 'v='
    match = re.search(r'v=([a-zA-Z0-9_-]{11})', youtube_url)
    if match:
        return match.group(1)
    return None

# Hàm đọc file JSON và lấy URL video
def read_video_url_from_json(json_file):
    try:
        with open(json_file, 'r', encoding='utf-8') as file:  # Chỉ định encoding là 'utf-8'
            data = json.load(file)
            # Kiểm tra xem 'watch_url' có tồn tại trong dữ liệu không
            if 'watch_url' in data:
                return data['watch_url']
            else:
                return None  # Trả về None nếu không tìm thấy 'watch_url'
    except (json.JSONDecodeError, FileNotFoundError, KeyError) as e:
        return str(e)  # Trả về thông báo lỗi nếu gặp lỗi
    
# Hàm lưu phụ đề vào file .txt với văn bản hoàn chỉnh và chuyển tất cả ký tự hoa thành ký tự thường
def save_subtitles_to_file(subtitles, output_file):
    with open(output_file, 'w', encoding='utf-8') as file:
        # Gộp tất cả các dòng văn bản thành một chuỗi duy nhất và chuyển tất cả ký tự hoa thành ký tự thường
        full_text = " ".join(line['text'] for line in subtitles).lower()

        # Regular expression to remove content between brackets
        full_text = re.sub(r'\[.*?\]', '', full_text)

        file.write(full_text)

# Hàm lưu lỗi vào file _errors.txt với thông báo lỗi và URL video (nếu có)
def save_error_to_file(error_message, output_file, video_url=None):
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write(error_message)
        if video_url:
            file.write(f"\nURL video: {video_url}")

# Hàm chính
def main():
    # Đường dẫn đến thư mục metadata chứa các file JSON
    metadata_folder = 'data/metadata'
    
    # Tạo thư mục subtitle nếu chưa tồn tại
    subtitle_folder = 'data/subtitle/txt'
    if not os.path.exists(subtitle_folder):
        os.makedirs(subtitle_folder)

    # Lặp qua tất cả các file trong thư mục metadata
    for json_file in os.listdir(metadata_folder):
        if json_file.endswith('.json'):
            json_path = os.path.join(metadata_folder, json_file)

            # Đọc URL video từ file JSON
            video_url = read_video_url_from_json(json_path)
            video_id = extract_video_id(video_url)
            
            if video_id:
                # Lấy phụ đề từ video
                subtitles = get_subtitle(video_id)
                
                if isinstance(subtitles, list):
                    # Tạo tên file .txt tương ứng trong thư mục subtitle
                    txt_file = os.path.join(subtitle_folder, json_file.replace('.json', '.txt'))
                    
                    # Lưu phụ đề vào file .txt dưới dạng văn bản hoàn chỉnh
                    save_subtitles_to_file(subtitles, txt_file)
                else:
                    # Lưu lỗi vào file _errors.txt
                    error_file = os.path.join(subtitle_folder, json_file.replace('.json', '_errors.txt'))
                    save_error_to_file(subtitles, error_file, video_url)
            else:
                # Lưu lỗi nếu không tìm thấy video ID
                error_message = f"Không tìm thấy video ID cho URL: {video_url}"
                error_file = os.path.join(subtitle_folder, json_file.replace('.json', '_errors.txt'))
                save_error_to_file(error_message, error_file, video_url)

# Hàm này xử lý các file _errors.txt để gộp các dòng văn bản và loại bỏ các dòng chứa thời gian
def process_error_files(subtitle_folder):
    # Tạo danh sách chứa tất cả các file _errors.txt trong thư mục
    error_files = [f for f in os.listdir(subtitle_folder) if f.endswith('_errors.txt')]
    
    # Lặp qua từng file _errors.txt
    for error_file in error_files:
        error_file_path = os.path.join(subtitle_folder, error_file)
        
        # Đọc nội dung của file
        with open(error_file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        
        # Gộp các dòng văn bản và loại bỏ các dòng chứa thời gian
        text_lines = []
        for line in lines:
            # Loại bỏ các dòng chứa thời gian bằng cách kiểm tra định dạng thời gian
            if not re.match(r'^\d+:\d+', line):
                text_lines.append(line.strip())
        
        # Gộp tất cả các dòng văn bản thành một chuỗi duy nhất và chuyển tất cả ký tự hoa thành ký tự thường
        full_text = " ".join(text_lines).lower()
        
        # Lưu kết quả vào file mới
        output_file_path = os.path.join(subtitle_folder, error_file.replace('_errors.txt', '.txt'))
        # Lưu phụ đề vào file .txt dưới dạng văn bản hoàn chỉnh
        save_subtitles_to_file(full_text, output_file_path)

if __name__ == "__main__":
    # Dòng code bên dưới sẽ chạy nếu trong các file subtitle có file nào bị lỗi
    #process_error_files('subtitle')
    main()