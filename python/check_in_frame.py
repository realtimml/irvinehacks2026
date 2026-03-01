import cv2
from ultralytics import YOLO
from typing import Generator

def check_in_frame(capture, model) -> Generator[bool, None, None]:
    while True:
        ret, frame = capture.read()
        # frame = cv2.resize(frame, (512, 288))  # Resize frame for faster processing

        if not ret:
            print("Error: Can't receive frame.")
            return False

        results = model(frame)
        # annotated_frame = results[0].plot()
        # cv2.imshow('Webcam Feed', annotated_frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        yield len(results[0].boxes) > 0  # Yield True if at least one person is detected, otherwise False

def camera_loop():
    model = YOLO('models/yolo26n-pose.onnx')  # Load a pretrained YOLOv8 model (you can choose different versions)

    # 1. Initialize the webcam (0 is usually the default built-in camera)
    cap = cv2.VideoCapture(0)


    if not cap.isOpened():
        print("Error: Could not open webcam.")
        exit()

    print("Press 'q' to quit.")

    for b in check_in_frame(cap, model):
        print(f"Person in frame: {b}")

        if not b:
            break
    
    cap.release()
    cv2.destroyAllWindows()
