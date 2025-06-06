# app.py
import streamlit as st
import cv2
from PIL import Image
import numpy as np
from dog_detector import detect_dogs_from_frame

st.set_page_config(page_title="Stray Dog Detector", layout="wide")
st.title("🐶 Stray Dog Detection System")

uploaded_file = st.file_uploader("Upload a video", type=["mp4", "avi", "mov"])
if uploaded_file:
    st.video(uploaded_file)

    tfile = open("temp_video.mp4", "wb")
    tfile.write(uploaded_file.read())
    tfile.close()

    cap = cv2.VideoCapture("temp_video.mp4")
    frame_count = 0
    dog_count = 0

    stframe = st.empty()

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        detections, results = detect_dogs_from_frame(frame)
        dog_count += len(detections)

        # Render bounding boxes
        annotated_frame = np.squeeze(results.render())
        stframe.image(annotated_frame, channels="BGR")

        frame_count += 1

    st.success(f"Detection Complete ✅\n\nTotal Frames: {frame_count}, Dogs Detected: {dog_count}")
