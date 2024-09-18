import pandas as pd
import json

class mapping:
    def __init__(self, img_path: str) -> None:
        # img_path = data/images/L01_V001/145.jpg
        self.folder, self.file = tuple(img_path.split('/')[-2:])
    
    def getFrame_idx(self):
        csv_path = 'data/map-keyframes/' + self.folder + '.csv'
        df = pd.read_csv(csv_path)
        return df.loc[df['n'] == int(self.file.split('.')[0]), 'frame_idx'].values[0]
    
    def getTime(self):
        csv_path = 'data/map-keyframes/' + self.folder + '.csv'
        df = pd.read_csv(csv_path)
        return df.loc[df['n'] == int(self.file.split('.')[0]), 'pts_time'].values[0]
    
    def generateURL(self):
        json_path = 'data/metadata/' + self.folder + '.json'
        with open(json_path, 'r', encoding='utf-8') as file: 
            url = json.load(file)['watch_url']
        new_url = f"{url}&t={self.getTime()}s"
        return new_url
    
if __name__ == '__main__':
    obj = mapping("data/images/L01_V001/145.jpg")
    time = obj.getTime()
    yt_url = obj.generateURL()
    print(yt_url)