# import mediapipe as mp
# import cv2
# import json
# import os

# # Khởi tạo MediaPipe Pose.
# mp_pose = mp.solutions.pose
# pose = mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.5, min_tracking_confidence=0.5)

# # Mở video.
# cap = cv2.VideoCapture('D:\\videos2signlangani\\data\\input-data\\D0206B.mp4')

# # Tạo thư mục để lưu các tệp JSON.
# output_folder = 'D:\\videos2signlangani\\out_mediapipe'
# os.makedirs(output_folder, exist_ok=True)

# frame_count = 0
# while cap.isOpened():
#     ret, frame = cap.read()
#     if not ret:
#         break

#     # Chuyển đổi hình ảnh sang RGB.
#     image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

#     # Xử lý khung hình để trích xuất keypoints.
#     results = pose.process(image_rgb)

#     if results.pose_landmarks:
#         keypoints = []
#         for landmark in results.pose_landmarks.landmark:
#             keypoints.extend([landmark.x, landmark.y, landmark.visibility])

#         # Tạo cấu trúc JSON theo định dạng của OpenPose.
#         openpose_format = {
#             "version": 1.3,
#             "people": [
#                 {
#                     "pose_keypoints_2d": keypoints
#                 }
#             ]
#         }

#         # Lưu tệp JSON.
#         json_path = os.path.join(output_folder, f'frame_{frame_count:04d}.json')
#         with open(json_path, 'w') as f:
#             json.dump(openpose_format, f)

#     frame_count += 1

# cap.release()


import mediapipe as mp
import cv2
import json
import os

# Khởi tạo MediaPipe Pose.
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.5, min_tracking_confidence=0.5)

# Mở video.
cap = cv2.VideoCapture('D:\\videos2signlangani\\data\\input-data\\D0206B.mp4')
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
frame_rate = int(cap.get(cv2.CAP_PROP_FPS))

# Tạo thư mục để lưu các tệp JSON.
output_folder = 'D:\\videos2signlangani\\out_mediapipe'
os.makedirs(output_folder, exist_ok=True)

# Tạo video writer để lưu video đã pose estimate.
out_video = cv2.VideoWriter('mediapipe_D0206B.mp4', cv2.VideoWriter_fourcc(*'mp4v'), frame_rate, (frame_width, frame_height))

frame_count = 0
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Chuyển đổi hình ảnh sang RGB.
    image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Xử lý khung hình để trích xuất keypoints.
    results = pose.process(image_rgb)

    if results.pose_landmarks:
        keypoints = []
        for landmark in results.pose_landmarks.landmark:
            keypoints.extend([landmark.x, landmark.y, landmark.visibility])

        # Tạo cấu trúc JSON theo định dạng của OpenPose.
        openpose_format = {
            "version": 1.3,
            "people": [
                {
                    "pose_keypoints_2d": keypoints
                }
            ]
        }

        # Lưu tệp JSON.
        json_path = os.path.join(output_folder, f'frame_{frame_count:04d}.json')
        with open(json_path, 'w') as f:
            json.dump(openpose_format, f)

        # Vẽ các keypoints lên khung hình.
        for idx, landmark in enumerate(results.pose_landmarks.landmark):
            x = int(landmark.x * frame_width)
            y = int(landmark.y * frame_height)
            cv2.circle(frame, (x, y), 5, (0, 255, 0), -1)

    # Ghi khung hình đã vẽ keypoints vào video output.
    out_video.write(frame)
    frame_count += 1

cap.release()
out_video.release()
