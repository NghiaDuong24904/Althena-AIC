<h1><center>AIthena team <br> Event Retrieval from Visual Data System</center></h1>

## Quy chuẩn
```
CLIP-features chứa 363 file feature .npy được generate ra từ model Vit B/32 của CLIP
map-keyframes chứa 363 file .csv của từng video để ánh xạ ra frame_idx 
images chứa các keyframes theo video với format folder có thể là: L01_V005/145.jpg, L12_V011/100.jpg,...
metadata: chứa thông tin về video đó - dùng để lấy link youtube

```


## Setup 
```
pip install git+https://github.com/openai/CLIP.git
pip install -r requirements.txt

Tải môi trường chạy OCR: https://www.miai.vn/2019/08/22/ocr-nhan-dang-van-ban-tieng-viet-voi-tesseract-ocr/
-> Install và lưu file chương trình ở thư mục mặc định là: "C:\Program Files\Tesseract-OCR"
```

## Run 
```
python app.py
```

URL: http://0.0.0.0:5001/home?index=0


