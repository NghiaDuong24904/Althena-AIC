import numpy as np
import os

# Đường dẫn đến thư mục chứa tất cả các file .npy
npy_directory = r'data/CLIP-features'
all_features = []

# Duyệt qua từng file .npy trong thư mục
for file_name in os.listdir(npy_directory):
    if file_name.endswith('.npy'):
        file_path = os.path.join(npy_directory, file_name)
        # Load features và thêm vào danh sách
        features = np.load(file_path)
        all_features.append(features)


# Cái này xài để lấy theo từng video nè (Nếu )
# features = np.load(r"C:\Users\Vatuk\OneDrive - VNU-HCMUS\Desktop\clip-features-32-b1\clip-features-32\L01_V020.npy")
# all_features.append(features)


# Gộp tất cả features vào một mảng numpy
all_features = np.vstack(all_features)

import faiss

d = all_features.shape[1]  # Chiều của vector đặc trưng
index = faiss.IndexFlatL2(d)  # Sử dụng chỉ mục Flat L2
index.add(all_features)  # Thêm các đặc trưng vào chỉ mục

# Lưu chỉ mục vào file .bin
faiss.write_index(index, 'faiss_normal_ViT.bin')