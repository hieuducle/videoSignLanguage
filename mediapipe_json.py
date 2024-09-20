import os
import mediapipe as mp
import cv2
import json

# Khởi tạo MediaPipe Hands.
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, min_detection_confidence=0.5, min_tracking_confidence=0.5)

# Mở video.
video_path = 'D:\\videos2signlangani\\data\\input-data\\D0206B.mp4'
cap = cv2.VideoCapture(video_path)

if not cap.isOpened():
    print(f"Error: Cannot open video file {video_path}")
else:
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    frame_rate = int(cap.get(cv2.CAP_PROP_FPS))

    # Tạo thư mục để lưu các tệp JSON.
    output_folder = 'D:\\videos2signlangani\\output_folder'
    os.makedirs(output_folder, exist_ok=True)

    frame_count = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Chuyển đổi hình ảnh sang RGB.
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Xử lý khung hình để xác định hai tay.
        hands_results = hands.process(image_rgb)

        # Duyệt qua các landmarks của hai tay.
        left_keypoints = []
        right_keypoints = []
        if hands_results.multi_hand_landmarks:
            for hand_landmarks, handedness in zip(hands_results.multi_hand_landmarks, hands_results.multi_handedness):
                hand_label = handedness.classification[0].label
                keypoints = []
                for landmark in hand_landmarks.landmark:
                    x = landmark.x * frame_width
                    y = landmark.y * frame_height
                    z = landmark.z
                    # visibility không luôn có sẵn trong các bản build của MediaPipe
                    visibility = getattr(landmark, 'visibility', 1)
                    if x == 0 and y == 0 and z == 0:  # Bỏ qua các điểm không xác định
                        continue
                    keypoints.extend([x, y, visibility])

                if hand_label == 'Left':
                    left_keypoints = keypoints
                elif hand_label == 'Right':
                    right_keypoints = keypoints

        # Nếu không phát hiện được tay trái hoặc tay phải, đặt giá trị mặc định
        if not left_keypoints:
            left_keypoints = [0] * 21 * 3  # 21 điểm keypoint, mỗi điểm có (x, y, visibility)
        if not right_keypoints:
            right_keypoints = [0] * 21 * 3  # 21 điểm keypoint, mỗi điểm có (x, y, visibility)

        # Tạo cấu trúc JSON.
        json_data = {
            "version": 1.1,
            "people": [
                {
                    "hand_left_keypoints_2d": left_keypoints,
                    "hand_right_keypoints_2d": right_keypoints
                }
            ]
        }

        # Lưu tệp JSON.
        output_path = os.path.join(output_folder, f'frame_{frame_count:04d}.json')
        with open(output_path, 'w') as f:
            json.dump(json_data, f)

        frame_count += 1

    cap.release()
    hands.close()
