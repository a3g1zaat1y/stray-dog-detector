import streamlit as st
import cv2
from PIL import Image
import numpy as np
from dog_detector import detect_dogs_from_frame
import matplotlib.pyplot as plt
import os
import warnings
import smtplib
from email.message import EmailMessage
from email.utils import formataddr
from collections import defaultdict

# ----------------------------
# 📤 Email Sending Function (Summary)
# ----------------------------
def send_summary_email(alert_timestamps, frame_path, log_path, location, duration):
    sender_email = "izzatiasmui99@gmail.com"
    sender_name = "Stray Dog Alert System"
    receiver_email = "212119@student.upm.edu.my"
    app_password = "mimmuppymotkrixi"  # Gmail App Password (no spaces)

    msg = EmailMessage()
    msg['Subject'] = f"📊 Summary Alert – Stray Dog Detection at {location}"
    msg['From'] = formataddr((sender_name, sender_email))
    msg['To'] = receiver_email

    body = f"""
Summary of stray dog detections from your video.

📍 Location: {location}
⏱️ Duration: {duration}
🚨 Alert frames: {len(alert_timestamps)}
🕒 Times: {', '.join(alert_timestamps) if alert_timestamps else 'None'}

See attached log and sample screenshot.
"""

    msg.set_content(body)

    if frame_path and os.path.exists(frame_path):
        with open(frame_path, 'rb') as f:
            msg.add_attachment(f.read(), maintype='image', subtype='jpeg', filename=os.path.basename(frame_path))

    if os.path.exists(log_path):
        with open(log_path, 'rb') as f:
            msg.add_attachment(f.read(), maintype='text', subtype='csv', filename='alert_log.csv')

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(sender_email, app_password)
            smtp.send_message(msg)
        print("✅ Summary email sent.")
    except Exception as e:
        print(f"❌ Email failed: {e}")

# ----------------------------
# 🛠️ App Setup
# ----------------------------
warnings.filterwarnings("ignore", category=DeprecationWarning)
st.set_page_config(page_title="Stray Dog Detector", layout="wide")
st.title("🐶 Stray Dog Detection System")

location = st.text_input("📍 Enter video location", placeholder="e.g., Taman Seri Mewah, Kajang")
uploaded_file = st.file_uploader("Upload a video", type=["mp4", "avi", "mov"])

if os.path.exists("alert_log.csv"):
    os.remove("alert_log.csv")
with open("alert_log.csv", "w") as log:
    log.write("Frame,DogCount,Timestamp,Location\n")

if not os.path.exists("alerts"):
    os.makedirs("alerts")

detection_counts = []
frame_numbers = []
interval_counts = defaultdict(int)
alert_timestamps = []
first_alert_screenshot = None

if uploaded_file:
    st.video(uploaded_file)

    with open("temp_video.mp4", "wb") as tfile:
        tfile.write(uploaded_file.read())

    cap = cv2.VideoCapture("temp_video.mp4")
    frame_count = 0
    total_dog_count = 0
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    video_duration = f"{int((total_frames/fps)//60):02}:{int((total_frames/fps)%60):02}"

    stframe = st.empty()

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        detections, annotated_frame = detect_dogs_from_frame(frame)
        dog_count = len(detections)
        total_dog_count += dog_count

        timestamp_sec = frame_count / fps
        timestamp_str = f"{int(timestamp_sec//60):02}:{int(timestamp_sec%60):02}"
        interval_key = int(timestamp_sec) // 10
        interval_counts[interval_key] += dog_count

        stframe.image(annotated_frame, channels="BGR", use_container_width=True)

        detection_counts.append(dog_count)
        frame_numbers.append(frame_count)

        if dog_count >= 3:
            alert_timestamps.append(timestamp_str)
            frame_path = f"alerts/alert_frame_{frame_count}.jpg"
            cv2.imwrite(frame_path, annotated_frame)

            with open("alert_log.csv", "a") as log:
                log.write(f"{frame_count},{dog_count},{timestamp_str},{location}\n")

            if not first_alert_screenshot:
                first_alert_screenshot = frame_path

        frame_count += 1

    cap.release()

    st.success(f"✅ Detection Complete!\n\nTotal Frames: {frame_count}, Total Dogs Detected: {total_dog_count}")

    # 📤 Send summary email after video
    send_summary_email(
        alert_timestamps=alert_timestamps,
        frame_path=first_alert_screenshot,
        log_path="alert_log.csv",
        location=location,
        duration=video_duration
    )

    # 📊 Summary Chart
st.subheader("📊 Dogs Detected per 10-Second Interval")
