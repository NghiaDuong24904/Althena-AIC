from underthesea import word_tokenize
from collections import Counter
from utils.query_processing import Translation
import os
import mapping as mp
import json

def calculate_similarity(text, query):
    text_tokens, query_tokens = word_tokenize(text), word_tokenize(query) 
    text_counter, query_counter = Counter(text_tokens), Counter(query_tokens)
    common_words = set(text_counter) & set(query_counter)
    common_count = sum(min(text_counter[word], query_counter[word]) for word in common_words)
    total_words = len(query_tokens)
    if total_words == 0:
        return 0
    similarity_percentage = (common_count / total_words) 
    return similarity_percentage


def get_video_list(pagefile, keyword):
    img_path = [entry['imgpath'] for entry in pagefile]
    video_paths = ["data\\subtitle\\" + path.split('\\')[-2] + ".json" for path in img_path]
    #print(video_paths)
    video_list = []

    for json_path in video_paths:
        #print(json_path)
        # Open the JSON file and load its content
        with open(json_path, 'r', encoding='utf-8') as file:
            json_data = json.load(file)
        #print(json_data)
        json_data = ' '.join(json_data)
        score = calculate_similarity(json_data, keyword)
        
        # Extract the video name and metadata path
        video_name = json_path.split('\\')[-1][:-5]
        metadata_path = "data\\metadata\\" + video_name + ".json"

        # Open the metadata JSON file and load its content
        with open(metadata_path, 'r', encoding='utf-8') as file:
            metadata = json.load(file)
        
        url = metadata['watch_url']

        video_list.append((video_name, url, score))

    return sorted(video_list, reverse=True, key=lambda x: x[-1])

    



        

    