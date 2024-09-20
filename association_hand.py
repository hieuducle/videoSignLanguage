import os
import json

# Đường dẫn đến thư mục chứa các tệp JSON của folder alpha và folder media
folder_alpha_path = 'D:\\videos2signlangani\\data\\temp\\openpose-keypoints\\D0206B'
folder_media_path = 'D:\\videos2signlangani\\output_folder'

# Lấy danh sách tên file trong folder alpha (hoặc folder media)
alpha_filenames = os.listdir(folder_alpha_path)

# Lặp qua các tên file trong folder alpha (hoặc folder media)
for filename in alpha_filenames:
    alpha_filepath = os.path.join(folder_alpha_path, filename)
    media_filepath = os.path.join(folder_media_path, filename)

    # Đọc dữ liệu từ folder alpha
    with open(alpha_filepath, 'r') as f:
        alpha_json = json.load(f)

    # Đọc dữ liệu từ folder media
    with open(media_filepath, 'r') as f:
        media_json = json.load(f)

    # Cập nhật giá trị hand_left_keypoints_2d và hand_right_keypoints_2d từ folder media cho folder alpha
    for alpha_person, media_person in zip(alpha_json['people'], media_json['people']):
        alpha_person['hand_left_keypoints_2d'] = media_person.get('hand_left_keypoints_2d', [])
        alpha_person['hand_right_keypoints_2d'] = media_person.get('hand_right_keypoints_2d', [])

    # Ghi lại dữ liệu đã cập nhật vào folder alpha
    with open(alpha_filepath, 'w') as f:
        json.dump(alpha_json, f)
