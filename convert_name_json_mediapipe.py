import os

# Đường dẫn đến thư mục chứa các tệp JSON
folder_path = 'D:\\videos2signlangani\\out_mediapipe_full'

# Lặp qua các file trong thư mục
for index, filename in enumerate(os.listdir(folder_path)):
    # Tạo tên mới cho file
    new_filename = f'D0532_{index:012d}_keypoints.json'
    # Đường dẫn tới file cũ_
    old_filepath = os.path.join(folder_path, filename)
    # Đường dẫn tới file mới
    new_filepath = os.path.join(folder_path, new_filename)
    # Đổi tên file
    os.rename(old_filepath, new_filepath)
