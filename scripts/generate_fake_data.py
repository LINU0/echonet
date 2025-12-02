import os
import cv2
import numpy as np
import pandas as pd

# 設定資料夾結構
base_dir = "a4c-video-dir"
video_dir = os.path.join(base_dir, "Videos")
os.makedirs(video_dir, exist_ok=True)

# 定義要生成的影片資訊
# 關鍵：VAL 和 TEST 都必須至少包含 "一個高於 50" 和 "一個低於 35" 的案例
videos = [
    # 訓練集 (只要有就好)
    {"name": "train_video_1", "split": "TRAIN", "ef": 55.0},
    
    # 驗證集 (混合數據以通過 AUC 計算)
    {"name": "val_video_low",  "split": "VAL",   "ef": 30.0}, # 低於所有門檻
    {"name": "val_video_high", "split": "VAL",   "ef": 60.0}, # 高於所有門檻
    
    # 測試集 (混合數據以通過 AUC 計算)
    {"name": "test_video_low", "split": "TEST",  "ef": 30.0},
    {"name": "test_video_high","split": "TEST",  "ef": 60.0}
]

file_list_data = []
tracing_data = []

# 規格設定
width, height = 112, 112
fps = 30
frames = 32

print("開始生成多樣化測試資料 (v3)...")

for v in videos:
    video_name = v["name"]
    video_filename = f"{video_name}.avi"
    video_path = os.path.join(video_dir, video_filename)
    ef_value = v["ef"]
    
    # 1. 生成影片
    # 為了節省時間，只有當檔案不存在時才生成
    if not os.path.exists(video_path):
        print(f"生成影片: {video_filename} (EF={ef_value})")
        fourcc = cv2.VideoWriter_fourcc(*'MJPG')
        out = cv2.VideoWriter(video_path, fourcc, fps, (width, height))
        
        for i in range(frames):
            frame = np.zeros((height, width, 3), dtype=np.uint8)
            # 根據 EF 大小改變圓圈脈動幅度 (純視覺效果)
            pulse = 10 if ef_value > 50 else 2
            radius = 30 + int(pulse * np.sin(i / 5))
            
            # 繪製模擬心臟
            cv2.circle(frame, (56, 56), radius, (0, 0, 255), -1)
            # 加雜訊
            noise = np.random.randint(0, 50, (height, width, 3), dtype=np.uint8)
            frame = cv2.add(frame, noise)
            out.write(frame)
        out.release()
    else:
        print(f"影片已存在，跳過生成: {video_filename}")
    
    # 2. 準備 FileList 資料
    file_list_data.append({
        "FileName": video_name,
        "EF": ef_value,
        "EDV": 100.0,
        "ESV": 100.0 * (1 - ef_value/100), # 簡單算一下 ESV 讓數據合理一點
        "Split": v["split"]
    })
    
    # 3. 準備 VolumeTracings 資料
    # 每個影片給兩幀標註
    tracing_data.append({"FileName": video_filename, "X1": 50, "Y1": 50, "X2": 60, "Y2": 60, "Frame": 0})
    tracing_data.append({"FileName": video_filename, "X1": 50, "Y1": 50, "X2": 60, "Y2": 60, "Frame": 15})

# 存檔 FileList.csv
df_filelist = pd.DataFrame(file_list_data)
df_filelist.to_csv(os.path.join(base_dir, "FileList.csv"), index=False)
print("FileList.csv 更新完成 (包含混合 EF 數據)。")

# 存檔 VolumeTracings.csv
df_tracings = pd.DataFrame(tracing_data)
df_tracings.to_csv(os.path.join(base_dir, "VolumeTracings.csv"), index=False)
print("VolumeTracings.csv 更新完成。")

