from ultralytics import YOLO
import cv2

# Load the uploaded YOLOv8n model
model = YOLO('model/yolov8n.pt')  # Use the uploaded model path

def detect_dogs_from_frame(frame):
    results = model.predict(source=frame, save=False, verbose=False)
    detections = []

    for result in results:
        boxes = result.boxes
        names = model.names
        for box in boxes:
            label = names[int(box.cls)]
            if label.lower() == 'dog':
                detections.append({
                    'box': box.xyxy.tolist(),
                    'confidence': float(box.conf),
                    'label': label
                })

    # Render annotated frame with bounding boxes
    annotated_frame = results[0].plot()
    return detections, annotated_frame
