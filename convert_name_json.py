import os

# Đường dẫn tới thư mục chứa các tệp JSON
folder_path = 'D:\\videos2signlangani\\out_mediapipe'

# Tên của video
video_name = 'D0206B'

# Liệt kê tất cả các tệp trong thư mục
files = os.listdir(folder_path)

# Sắp xếp các tệp theo thứ tự số
files = sorted(files, key=lambda x: int(os.path.splitext(x)[0]))

# Đổi tên các tệp
for i, filename in enumerate(files):
    # Định dạng tên mới
    new_filename = f"{video_name}_{str(i).zfill(12)}_keypoints.json"
    
    # Đường dẫn tệp hiện tại
    old_file_path = os.path.join(folder_path, filename)
    
    # Đường dẫn tệp mới
    new_file_path = os.path.join(folder_path, new_filename)
    
    # Đổi tên tệp
    os.rename(old_file_path, new_file_path)

print("Đổi tên tệp hoàn thành.")
