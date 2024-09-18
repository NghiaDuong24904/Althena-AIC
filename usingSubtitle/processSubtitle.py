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

###############################################################################################################

# Hàm trích xuất video ID từ link YouTube
def extract_video_id(youtube_url):
    # Do ID video YouTube có độ dài cố định là 11 ký tự và nằm sau ký tự 'v='
    match = re.search(r'v=([a-zA-Z0-9_-]{11})', youtube_url)
    if match:
        return match.group(1)
    return None

###############################################################################################################

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

###############################################################################################################

def norm_and_translate_subtitle(subtitles):
    # Xóa các phần trong ngoặc vuông
    sub = re.sub(r'\[.*?\]', '', subtitles)

    # Chuyển tất cả ký tự hoa thành ký tự thường
    sub = sub.lower()

    return sub

###############################################################################################################

# Hàm lưu lỗi vào file _errors.txt với thông báo lỗi và URL video (nếu có)
def save_error_to_file(error_message, output_file, video_url=None):
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write(error_message)
        if video_url:
            file.write(f"\nURL video: {video_url}")

###############################################################################################################

# Hàm chính
def main():
    # Đường dẫn đến thư mục metadata chứa các file JSON
    metadata_folder = 'data/metadata'
    
    # Tạo thư mục subtitle nếu chưa tồn tại
    subtitle_folder = 'data/subtitle'
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
                try:
                    # Lấy phụ đề của video
                    transcript = get_subtitle(video_id)
                    
                    # Gộp các phần phụ đề theo các mốc thời gian
                    combined_transcript = []
                    current_text = ""
                    start_time = None

                    for entry in transcript:
                        if start_time is None:
                            start_time = entry['start']
                        
                        # Gộp các đoạn phụ đề nếu chúng gần nhau
                        if start_time and entry['start'] - start_time <= 6:  # Giả sử khoảng cách giữa các mốc thời gian là 5 giây
                            current_text += " " + entry['text']
                        else:
                            if current_text:
                                current_text = norm_and_translate_subtitle(current_text)
                                combined_transcript.append({
                                    "start": start_time,
                                    "end": entry['start'],
                                    "text": current_text.strip()
                                })
                            start_time = entry['start']
                            current_text = entry['text']

                    # Thêm phần phụ đề cuối cùng vào danh sách
                    if current_text:
                        current_text = norm_and_translate_subtitle(current_text)
                        combined_transcript.append({
                            "start": start_time,
                            "end": transcript[-1]['start'] + transcript[-1]['duration'],
                            "text": current_text.strip()
                        })

                    file_name = os.path.join(subtitle_folder, json_file)
                    
                    # Lưu phụ đề đã gộp vào file JSON với mã hóa UTF-8
                    with open(file_name, 'w', encoding='utf-8') as f:
                        json.dump(combined_transcript, f, ensure_ascii=False, indent=4)
                    
                    print(f"Đã lưu phụ đề vào file {file_name}")
                    
                except Exception as e:
                    file_name = os.path.join(subtitle_folder, json_file)
                    file_name = file_name.replace('.json', '_errors.json')
                    
                    # Lưu lỗi và link youtube vào file JSON với mã hóa UTF-8
                    with open(file_name, 'w', encoding='utf-8') as f:
                        json.dump({"error": str(e), "video_url": video_url}, f, ensure_ascii=False, indent=4)

                    print(f"Đã xảy ra lỗi: {e}")

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
        #save_subtitles_to_file(full_text, output_file_path)

if __name__ == "__main__":
    main()
