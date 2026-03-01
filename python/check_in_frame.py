import cv2
from ultralytics import YOLO
from typing import Generator

model = YOLO('python/yolo26n-pose.pt')  # Load a pretrained YOLOv8 model (you can choose different versions)

# 1. Initialize the webcam (0 is usually the default built-in camera)
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 854)  # Set width
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)  # Set height

if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

print("Press 'q' to quit.")


def check_in_frame(capture, model) -> Generator[bool, None, None]:
    while True:
        ret, frame = capture.read()

        if not ret:
            print("Error: Can't receive frame.")
            return False

        results = model(frame)
        # annotated_frame = results[0].plot()
        # cv2.imshow('Webcam Feed', annotated_frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        yield len(results[0].boxes) > 0  # Yield True if at least one person is detected, otherwise False

for b in check_in_frame(cap, model):
    print(f"Person in frame: {b}")

    if not b:
        break

cap.release()
cv2.destroyAllWindows()
