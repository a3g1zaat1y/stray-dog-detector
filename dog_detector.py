# dog_detector.py
import torch
import cv2
import pandas as pd

model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)
model.eval()

def detect_dogs_from_frame(frame):
    results = model(frame)
    detections = []
    
    for *box, conf, cls in results.xyxy[0]:
        label = results.names[int(cls)]
        if label.lower() == 'dog':
            detections.append({
                'box': box,
                'confidence': float(conf),
                'label': label
            })
    return detections, results
