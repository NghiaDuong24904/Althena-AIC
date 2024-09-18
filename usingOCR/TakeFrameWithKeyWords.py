# -------------------------------------------------------
import json, os
import re
import unidecode


def findListKeyFrame(pagefile, global_pagefile , keyword: str, k: int = 100) -> list:
    img_path = [entry['imgpath'] for entry in pagefile]
    folders = {}.fromkeys(re.split(r'[/\\]', path)[-2] for path in img_path)
    print(folders)
    frames = []
    keyword = keyword.split(',')
    keyword = [k.lower().strip() for k in keyword]
    folder_image = "data/images"
    
    for folder in folders:
        json_path = f'data/OCR/{folder}.json'
        #print(json_path)
        if os.path.exists(json_path):
            try:
                with open(json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                # Tạo danh sách các frames phù hợp với từ khóa
                lst_frame = [os.path.join(os.path.join(folder_image, folder), name) for name in data.keys() if any(phrase in data[name] for phrase in keyword)] #sai
                frames.extend(lst_frame)
            except json.JSONDecodeError:
                print(f'Cannot open file JSON {json_path}')
        else:
            print(f'File {json_path} is not existed!')

    # Lọc pagefile dựa trên frames tìm được
    # print(global_pagefile)
    # print(pagefile)
    # print(frames)
    print(frames)
    
    filtered_pagefile = [item for item in global_pagefile if any(frame in item['imgpath'] for frame in frames)]
    

    return filtered_pagefile

# -------------------------------------------------------

# How to use code?

