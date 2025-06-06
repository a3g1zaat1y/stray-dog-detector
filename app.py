import streamlit as st
import cv2
from PIL import Image
import numpy as np
from dog_detector import detect_dogs_from_frame
import matplotlib.pyplot as plt
import os
import warnings

# Suppress deprecated warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

st.set_page_config(page_title="Stray Dog Detector", layout="wide")
st.title("🐶 Stray Dog Detection System")

uploaded_file = st.file_uploader("Upload a video", type=["mp4", "avi", "mov"])

# Prepare alert log
if os.path.exists("alert_log.csv"):
    os.remove("alert_log.csv")
with open("alert_log.csv", "w") as log:
    log.write("Frame,DogCount,Timestamp\n")

# Prepare output folder for alert screenshots
if not os.path.exists("alerts"):
    os.makedirs("alerts")

# Initialize graph data
detection_counts = []
frame_numbers = []

if uploaded_file:
    st.video(uploaded_file)

    tfile = open("temp_video.mp4", "wb")
    tfile.write(uploaded_file.read())
    tfile.close()

    cap = cv2.VideoCapture("temp_video.mp4")
    frame_count = 0
    total_dog_count = 0
    fps = cap.get(cv2.CAP_PROP_FPS) or 30  # fallback FPS if not found

    stframe = st.empty()
    chart_placeholder = st.empty()
    alert_placeholder = st.empty()

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        detections, annotated_frame = detect_dogs_from_frame(frame)
        dog_count = len(detections)
        total_dog_count += dog_count

        # Timestamp (MM:SS)
        timestamp_sec = frame_count / fps
        timestamp_str = f"{int(timestamp_sec//60):02}:{int(timestamp_sec%60):02}"

        # Display the frame
        stframe.image(annotated_frame, channels="BGR", use_container_width=True)

        # Add data for graph
        detection_counts.append(dog_count)
        frame_numbers.append(frame_count)

        # Live chart update every 10 frames
        if frame_count % 10 == 0:
            chart_placeholder.line_chart(data={"Dogs Detected": detection_counts})

        # Trigger alert if ≥ 3 dogs
        if dog_count >= 3:
            alert_placeholder.warning(f"🚨 High stray dog activity detected! Frame {frame_count} | Time {timestamp_str}")
            with open("alert_log.csv", "a") as log:
                log.write(f"{frame_count},{dog_count},{timestamp_str}\n")
            cv2.imwrite(f"alerts/alert_frame_{frame_count}.jpg", annotated_frame)

        frame_count += 1

    cap.release()
    st.success(f"✅ Detection Complete!\n\nTotal Frames: {frame_count}, Total Dogs Detected: {total_dog_count}")
    st.download_button("📥 Download Alert Log (CSV)", data=open("alert_log.csv").read(), file_name="alert_log.csv")
