from flask import Flask, render_template, Response, request, send_file, jsonify
import cv2
import os
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
import numpy as np
import pandas as pd
import glob 
import json 
import os
import webbrowser
import mapping as mp
import pyperclip
from usingOCR import TakeFrameWithKeyWords as ocr
import copy
from usingSubtitle import GetFrameASR as sub

from filterobj import filterobj as fob

from utils.query_processing import Translation
from utils.faiss import Myfaiss

# http://0.0.0.0:5001/home?index=0

# app = Flask(__name__, template_folder='templates', static_folder='static')

app = Flask(__name__, template_folder='templates')

DictImagePath = {}
i = 0
main_path = 'data/images'

for folder in os.listdir(main_path):
    folder_path = os.path.join(main_path, folder)
    if os.path.isdir(folder_path):
        
        for keyframe in os.listdir(folder_path):
            keyframe_path = os.path.join(folder_path, keyframe)
            
            if keyframe_path.lower().endswith(('.jpg')):

                DictImagePath[i] = keyframe_path
                i += 1


preQueryPageFile = []

global_pagefile = [{'imgpath': path, 'id': id} for id, path in DictImagePath.items()]



LenDictPath = len(DictImagePath)
bin_file='faiss_normal_ViT.bin' 
MyFaiss = Myfaiss(bin_file, DictImagePath, 'cpu', Translation(), "ViT-B/32")
########################

@app.route('/home')
@app.route('/')
def thumbnailimg():
    print("load_iddoc")

    pagefile = []
    # Get the 'index' parameter from the request, defaulting to 0 if not provided | Chỗ này có sửa
    index = request.args.get('index', default=0, type=int)

    imgperindex = 100

    page_filelist = []
    list_idx = []

    if LenDictPath - 1 > index + imgperindex:
        first_index = index * imgperindex
        last_index = index * imgperindex + imgperindex

        tmp_index = first_index
        while tmp_index < last_index:
            page_filelist.append(DictImagePath[tmp_index])
            list_idx.append(tmp_index)
            tmp_index += 1
    else:
        first_index = index * imgperindex
        last_index = LenDictPath

        tmp_index = first_index
        while tmp_index < last_index:
            page_filelist.append(DictImagePath[tmp_index])
            list_idx.append(tmp_index)
            tmp_index += 1

    for imgpath, id in zip(page_filelist, list_idx):
        pagefile.append({'imgpath': imgpath, 'id': id})

    data = {'num_page': int(LenDictPath / imgperindex) + 1, 'pagefile': pagefile}

    return render_template('home.html', data=data)


@app.route('/imgsearch')
def image_search():
    print("image search")
    pagefile = []
    id_query = int(request.args.get('imgid'))
    _, list_ids, _, list_image_paths = MyFaiss.image_search(id_query, k=50)

    imgperindex = 317

    for imgpath, id in zip(list_image_paths, list_ids):
        pagefile.append({'imgpath': imgpath, 'id': int(id)})
    

    data = {'num_page': int(LenDictPath/imgperindex)+1, 'pagefile': pagefile}
    
    return render_template('home.html', data=data)


# @app.route('/textsearch')
# def text_search():
#     print("text search  ")

#     pagefile = []
#     text_query = request.args.get('textquery')
#     _, list_ids, _, list_image_paths = MyFaiss.text_search(text_query, k=100)

#     imgperindex = 317  
    
#     for imgpath, id in zip(list_image_paths, list_ids):
#         pagefile.append({'imgpath': imgpath, 'id': int(id)})

#     data = {'num_page': int(LenDictPath/imgperindex)+1, 'pagefile': pagefile}
    
#     return render_template('home.html', data=data)


@app.route('/textsearch')
def text_search():  

    print("text search")
    global preQueryPageFile

    # Retrieve query parameters from the request
    text_query = request.args.get('text_query')
    faiss_checked = request.args.get('faiss', 'false').lower() == 'true'
    ocr_checked = request.args.get('ocr', 'false').lower() == 'true'
    subtitle_checked = request.args.get('subtitle', 'false').lower() == 'true'
    keywords = request.args.get('keywords')  # Keywords may be empty

    num_images = int(request.args.get('num_images', 0)) if request.args.get('num_images') else None

    # Default to Faiss if no other checkbox is selected
    if not faiss_checked and not ocr_checked and not subtitle_checked:
        faiss_checked = True

    pagefile = []
    videofile = []

    # Faiss Search
    if faiss_checked:
        _, list_ids, _, list_image_paths = MyFaiss.text_search(text_query, k=num_images or 100)

        #Append results from Faiss
        for imgpath, id in zip(list_image_paths, list_ids):
            pagefile.append({'imgpath': imgpath, 'id': int(id)})

        # OCR Processing if OCR is checked
        if ocr_checked:
            pagefile = ocr.findListKeyFrame(pagefile, global_pagefile, keywords)
        

        if subtitle_checked:
            pagefile = sub.get_frame_ASR(pagefile,global_pagefile, keywords)

    # # OCR Search only
    elif ocr_checked:
        pagefile = ocr.findListKeyFrame(global_pagefile, global_pagefile ,  keywords)

    # # Subtitle Search only
    elif subtitle_checked:
        pagefile = sub.get_frame_ASR(global_pagefile,global_pagefile, keywords)

    # Prepare the data for rendering
    imgperindex = 317
    
    preQueryPageFile = copy.deepcopy(pagefile)  #Lấy pagefile trước đó, nếu không lấy được thì dùng deep copy
    data = {'num_page': int(LenDictPath/imgperindex)+1, 'pagefile': pagefile}   

    # if subtitle_checked:
    #     video_data = [{'video_name': video[0], 'url': video[1], 'score': video[2]} for video in videofile]
    #     return render_template('video_results.html', data=video_data)
    
    return render_template('home.html', data=data)


@app.route('/get_img')
def get_img():
    # print("get_img")
    fpath = request.args.get('fpath')
    # fpath = fpath
    list_image_name = fpath.split("/")
    image_name = "/".join(list_image_name[-2:])

    if os.path.exists(fpath):
        img = cv2.imread(fpath)
    else:
        print("load 404.jpg")
        img = cv2.imread("./static/images/404.jpg")

    img = cv2.resize(img, (1280,720))

    # print(img.shape)
    img = cv2.putText(img, image_name, (30, 80), cv2.FONT_HERSHEY_SIMPLEX, 
                   3, (255, 0, 0), 4, cv2.LINE_AA)

    ret, jpeg = cv2.imencode('.jpg', img)
    return  Response((b'--frame\r\n'
                     b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n'),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/submit_item', methods=['POST'])
def submit_item():
    data = request.get_json()  
    img_path = data.get('imgpath')  
    print(img_path)
    obj = mp.mapping(img_path)
    time = obj.getTime()
    yt_url = obj.generateURL()
    webbrowser.open(yt_url)
    return 0

@app.route('/get_Answer', methods=['POST'])
def get_Answer():
    data = request.get_json()  
    img_path = data.get('imgpath')  
    obj = mp.mapping(img_path)
    frame_idx = obj.getFrame_idx()
    answer = img_path.split('/')[2] + ", " + str(frame_idx)
    pyperclip.copy(answer)
    return 0

# @app.route('/ocr_search')
# def text_search():
#     print("OCR search")

#     pagefile = []
#     text_query = request.args.get('textquery')
#     _, list_ids, _, list_image_paths = MyFaiss.text_search(text_query, k=100)

#     imgperindex = 317  
    
#     for imgpath, id in zip(list_image_paths, list_ids):
#         pagefile.append({'imgpath': imgpath, 'id': int(id)})

#     data = {'num_page': int(LenDictPath/imgperindex)+1, 'pagefile': pagefile}
    
#     return render_template('home.html', data=data)

@app.route('/filter', methods=['POST'])
def obj_filter():
    selected_items = request.form.get('selected_items')
    selected_items_list = [item.strip() for item in selected_items.split(',')]

    pagefile = fob.get_objectFilter(preQueryPageFile, selected_items_list)

    imgperindex = 100

    data = {'num_page': int(LenDictPath/imgperindex)+1, 'pagefile': pagefile}   
    return render_template('home.html', data=data)

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5001)
