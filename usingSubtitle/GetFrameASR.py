import json
import csv
import os
import math

def get_frame_ASR(pagefile,global_pagefile, keywords: str):
    # Lấy danh sách các đường dẫn hình ảnh
    img_paths = [entry['imgpath'] for entry in pagefile]
    subtitle_paths = ["data\\subtitle\\" + path.split('\\')[-2] + ".json" for path in img_paths]

    # Tách keywords thành list
    keywords = keywords.split(',')
    keywords = [k.lower().strip() for k in keywords]
    image_path = "data/images"

    list_frames = []

    # Duyệt qua từng file subtitle JSON
    for path in subtitle_paths:
        #print(path)
        # Đường dẫn đến file csv map frame
        csv_path = "data\\map-keyframes\\" + path.split('\\')[-1].split('.')[0] + ".csv"

        if not os.path.exists(path):
            #print(f"File JSON không tồn tại: {path}")
            continue  # Bỏ qua nếu file không tồn tại

        # Mở và đọc file JSON (chứa thông tin text)
        try:
            with open(path, 'r', encoding='utf-8') as f:
                subtitle_data = json.load(f)

        except json.JSONDecodeError:
            print(f"Lỗi khi đọc file JSON: {path}")
            continue  # Bỏ qua nếu file không đọc được
        
        # Duyệt qua từng entry trong file JSON
        for entry in subtitle_data:
            text = entry['text'].lower()

            # Kiểm tra nếu có keyword nào xuất hiện trong 'text'
            if any(keyword in text for keyword in keywords):
                # Làm tròn và tính toán start_time, end_time
                start_time = math.floor(entry['start'])
                end_time = math.ceil(entry['end'])

                # Quy đổi ra giây và chuyển thành frame index
                frame_idx_start = start_time * 60 * 25
                frame_idx_end = end_time * 60 * 25

                # Đọc file CSV để ánh xạ frame index về image path
                with open(csv_path, mode='r', encoding='utf-8') as csvfile:
                    csv_reader = csv.reader(csvfile)
                    next(csv_reader)  # Bỏ qua dòng tiêu đề

                    # Duyệt qua các frame index từ frame_idx_start đến frame_idx_end
                    for frame_idx in range(frame_idx_start, frame_idx_end + 1):
                        for row in csv_reader:
                            csv_frame_idx = int(row[3])  # Cột 4 là frame index

                            # Nếu trùng frame index thì ánh xạ về index tương ứng
                            if frame_idx == csv_frame_idx:
                                index = row[0]  # Cột 1 là index
                                image = os.path.join(os.path.join(folder_image, folder) + path.split('\\')[-2] + "\\" + index + ".jpg"
                                list_frames.append(image)

    filtered_pagefile = [item for item in global_pagefile if any(frame in item['imgpath'] for frame in list_frames)]
    return filtered_pagefile
