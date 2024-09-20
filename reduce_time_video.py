# import cv2
# import os

# # Đường dẫn tới video đầu vào và đầu ra
# input_path = r"D:\videos2signlangani\data\input-data\D0003.mp4"
# output_path = r"D:\videos2signlangani\folder_video_reduce\output_video_slow_D0003.mp4"

# # Đọc video đầu vào
# cap = cv2.VideoCapture(input_path)

# # Kiểm tra xem video có được mở thành công không
# if not cap.isOpened():
#     print("Không thể mở video.")
#     exit()

# # Lấy các thông số của video
# fps = cap.get(cv2.CAP_PROP_FPS)
# width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
# height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
# fourcc = cv2.VideoWriter_fourcc(*'mp4v')

# # Tạo đối tượng VideoWriter để lưu video đầu ra với tốc độ chậm hơn
# # fps / 2 có nghĩa là tốc độ video sẽ giảm đi một nửa
# out = cv2.VideoWriter(output_path, fourcc, fps / 2, (width, height))

# while cap.isOpened():
#     ret, frame = cap.read()
#     if not ret:
#         break
#     out.write(frame)

# cap.release()
# out.release()
# cv2.destroyAllWindows()

# print("Video đã được xử lý và lưu lại thành công.")


import subprocess
from video2animation.video_processing import to30fps
# Đường dẫn đến video đầu vào và đầu ra
input_video_path = "D:\\videos2signlangani\\data\\input-data\\D0072B.mp4"
video_path = to30fps(input_video_path)
output_video_path = "D0072B.mp4"

# Lệnh FFmpeg để giảm tốc độ video xuống một nửa
command = [
    "ffmpeg",
    "-i", video_path,
    "-filter:v", "setpts=2*PTS",
    output_video_path
]

# Chạy lệnh FFmpeg
try:
    subprocess.run(command, check=True)
    print("Video speed reduction successful.")
except subprocess.CalledProcessError as e:
    print(f"Error occurred: {e}")

