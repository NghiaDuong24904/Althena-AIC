import os
import clip
import torch
from PIL import Image
import numpy as np
from sklearn.preprocessing import normalize

# Load model CLIP
device = "cuda" if torch.cuda.is_available() else "cpu"
model, preprocess = clip.load("ViT-B/32", device=device)

# Đường dẫn tới folder chứa frame ảnh
root_folder = r'data/images'

# Tên file .npy để lưu kết quả
output_folder = r'data/newFeatures'
os.makedirs(output_folder, exist_ok=True)

# Lấy danh sách tất cả các sub-folder chứa ảnh
sub_folders = [f for f in os.listdir(root_folder) if os.path.isdir(os.path.join(root_folder, f))]

# Hàm xử lý trích xuất features từ folder ảnh và lưu file .npy
def process_folder(folder_path, output_file_path):
    # Danh sách file ảnh trong folder
    image_files = [f for f in os.listdir(folder_path) if f.endswith('.jpg')]

    # Khởi tạo danh sách chứa features
    features_list = []

    # Loop qua từng ảnh và trích xuất features
    for image_file in image_files:
        image_path = os.path.join(folder_path, image_file)
        image = Image.open(image_path)

        # Tiền xử lý ảnh và chuyển ảnh sang tensor
        image_input = preprocess(image).unsqueeze(0).to(device)

        # Trích xuất features từ model CLIP
        with torch.no_grad():
            image_features = model.encode_image(image_input)

        # Đưa tensor về dạng numpy array
        image_features_np = image_features.cpu().numpy()
        features_list.append(image_features_np)

    # Chuyển list features thành numpy array
    if features_list:
        features_array = np.concatenate(features_list, axis=0)

        # Chuẩn hóa L2 cho các vector features
        features_array_normalized = normalize(features_array, norm='l2').astype(np.float16)

        # Lưu array đã chuẩn hóa thành file .npy
        np.save(output_file_path, features_array_normalized)
        print(f"Đã lưu file '{output_file_path}' với shape: {features_array_normalized.shape}")
    else:
        print(f"Không có ảnh .jpg trong folder: {folder_path}")

# Xử lý từng sub-folder
for sub_folder in sub_folders:
    folder_path = os.path.join(root_folder, sub_folder)
    
    # Tên file .npy dựa trên tên sub-folder
    output_file_path = os.path.join(output_folder, f"{sub_folder}.npy")

    # Xử lý từng folder và lưu file .npy
    process_folder(folder_path, output_file_path)

print(f"Tất cả các file .npy đã được lưu trong folder: {output_folder}")