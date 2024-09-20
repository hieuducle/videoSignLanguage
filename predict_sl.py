import json
import numpy as np
import os

# Đường dẫn tới thư mục chứa kết quả AlphaPose
result_dir = 'D:\\videos2signlangani\\data\\temp\\openpose-keypoints\\D0001B'
# result_dir ='D:\\videos2signlangani\\out_mediapipe_full'
result_files = sorted([os.path.join(result_dir, f) for f in os.listdir(result_dir) if f.endswith('_keypoints.json')])

def load_keypoints(file):
    with open(file, 'r') as f:
        data = json.load(f)
    if len(data['people']) > 0:
        keypoints = np.array(data['people'][0]['pose_keypoints_2d']).reshape((-1, 3))
        return keypoints
    return None

def is_sign_language_starting(previous_keypoints, current_keypoints, threshold=1000):
    if previous_keypoints is None or current_keypoints is None:
        return False
    
    # Chỉ lấy tọa độ x và y
    previous_xy = previous_keypoints[:, :2]
    current_xy = current_keypoints[:, :2]
    
    # Tính tổng khoảng cách Euclidean giữa các điểm keypoints
    diff = np.linalg.norm(previous_xy - current_xy, axis=1).sum()
    return diff > threshold

previous_keypoints = None
for result_file in result_files:
    current_keypoints = load_keypoints(result_file)
    
    if current_keypoints is not None and is_sign_language_starting(previous_keypoints, current_keypoints):
        print(f"Sign language starts at frame: {result_file}")
        break
    
    previous_keypoints = current_keypoints
