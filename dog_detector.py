# dog_detector.py
from ultralytics import YOLO

model = YOLO('yolov8n.pt')  # Automatically downloads YOLOv5s weights

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

    # Render bounding boxes
    annotated_frame = results[0].plot()
    return detections, annotated_frame
