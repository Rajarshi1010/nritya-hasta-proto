import cv2, mediapipe as mp
print("OpenCV:", cv2.__version__)
hands = mp.solutions.hands.Hands(static_image_mode=True, max_num_hands=1)
print("MediaPipe Hands ready")
hands.close()
print("OK")
