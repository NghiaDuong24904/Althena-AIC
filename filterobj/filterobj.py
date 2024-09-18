import os
import json 
def get_objectFilter(preQuery, selected_item):
    list_imgpath = []
    
    imgpath_list = [item['imgpath'] for item in preQuery]

    for path in imgpath_list:
        video_name = os.path.join('data', 'object', path.split('\\')[-2] + ".json")
        
        # Lấy key là phần trước '.jpg' sau dấu '/' cuối cùng
        key = path.split('\\')[-1].split('.')[0]
        
        # Đọc nội dung JSON từ file
        with open(video_name, 'r') as file:
            data = json.load(file)

            if key in data:
                objects_in_frame = data[key]

                if all(item in objects_in_frame for item in selected_item):
                    list_imgpath.append(path)
    
    filtered_preQuery = [item for item in preQuery if item['imgpath'] in list_imgpath]
    return filtered_preQuery
