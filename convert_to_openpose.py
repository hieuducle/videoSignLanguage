import os
import json

# Đường dẫn đến thư mục chứa các file JSON
folder_path = 'data\\temp\\openpose-keypoints\\D0138'

# Lặp qua tất cả các file trong thư mục
for filename in os.listdir(folder_path):
    if filename.endswith('.json'):
        file_path = os.path.join(folder_path, filename)
        # Đọc dữ liệu từ file JSON
        with open(file_path, 'r') as f:
            data = json.load(f)

        # Tạo dữ liệu mới cho file
        new_data = {"version": "AlphaPose v0.3", "people": []}

        # Chuyển đổi dữ liệu keypoint
        for person in data['people']:
            new_person = {
                "person_id": [-1],
                "pose_keypoints_2d": person['pose_keypoints_2d'][:75],    
                "hand_left_keypoints_2d": person['hand_left_keypoints_2d'][:63],  
                "hand_right_keypoints_2d": person['hand_right_keypoints_2d'][:63]  
            }
            new_data['people'].append(new_person)

        # Ghi đè dữ liệu đã chuyển đổi vào cùng file
        with open(file_path, 'w') as f:
            json.dump(new_data, f, indent=4)

        print(f"Đã chuyển đổi và lưu file: {file_path}")