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

# ----------------------------
# 📤 Email Sending Function
# ----------------------------
def send_email_alert(frame_path, log_path, location, timestamp, frame_number):
    sender_email = "izzatiasmui99@gmail.com"         # 🔁 REPLACE THIS
    sender_name = "Stray Dog Alert System"
    receiver_email = "212119@student.upm.edu.my"      # 🔁 REPLACE THIS
    app_password = "mimmuppymotkrixi"                 # 🔁 Use Gmail App Password (no spaces)

    msg = EmailMessage()
    msg['Subject'] = f"🚨 Stray Dog Alert – Frame {frame_number} at {location}"
    msg['From'] = formataddr((sender_name, sender_email))
    msg['To'] = receiver_email
    msg.set_content(f"""
High stray dog activity detected!

📍 Location: {location}
🕒 Time: {timestamp}
🖼 Frame: {frame_number}

See attached image and alert log for details.
""")

    with open(frame_path, 'rb') as f:
        msg.add_attachment(f.read(), maintype='image', subtype='jpeg', filename=os.path.basename(frame_path))

    with open(log_path, 'rb') as f:
        msg.add_attachment(f.read(), maintype='text', subtype='csv', filename='alert_log.csv')

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(sender_email, app_password)
            smtp.send_message(msg)
        print(f"✅ Email sent for frame {frame_number}")
    except Exception as e:
        print(f"❌ Error sending email: {e}")

# ----------------------------
# 🛠️ App Setup
# ----------------------------
warnings.filterwarnings("ignore", category=DeprecationWarning)
st.set_page_config(page_title="Stray Dog Detector", layout="wide")
st.title("🐶 Stray Dog Detection System")

# 📍 Location Input
location = st.text_input("📍 Enter video location (e.g., Taman Seri Mewah, Kajang)", placeholder="e.g., Jalan Bandar Kajang")

uploaded_file = st.file_uploader("Upload a video", type=["mp4", "avi", "mov"])

# Prepare alert log
if os.path.exists("alert_log.csv"):
    os.remove("alert_log.csv")
with open("alert_log.csv", "w") as log:
    log.write("Frame,DogCount,Timestamp,Location\n")

# Create folder for screenshots
if not os.path.exists("alerts"):
    os.makedirs("alerts")

# Initialize chart data
detection_counts = []
frame_numbers = []

# ----------------------------
# 📹 Video Processing
# ----------------------------
if uploaded_file:
    st.video(uploaded_file)

    tfile = open("temp_video.mp4", "wb")
    tfile.write(uploaded_file.read())
    tfile.close()

    cap = cv2.VideoCapture("temp_video.mp4")
    frame_count = 0
    total_dog_count = 0
    fps = cap.get(cv2.CAP_PROP_FPS) or 30  # fallback

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

        # Generate timestamp (MM:SS)
        timestamp_sec = frame_count / fps
        timestamp_str = f"{int(timestamp_sec//60):02}:{int(timestamp_sec%60):02}"

        # Display frame
        stframe.image(annotated_frame, channels="BGR", use_container_width=True)

        # Update chart data
        detection_counts.append(dog_count)
        frame_numbers.append(frame_count)

        if frame_count % 10 == 0:
            chart_placeholder.line_chart(data={"Dogs Detected": detection_counts})

        # 🚨 Alert block
        if dog_count >= 3:
            alert_placeholder.warning(f"🚨 High stray dog activity! Frame {frame_count} | Time {timestamp_str}")
            
            with open("alert_log.csv", "a") as log:
                log.write(f"{frame_count},{dog_count},{timestamp_str},{location}\n")
            
            frame_path = f"alerts/alert_frame_{frame_count}.jpg"
            cv2.imwrite(frame_path, annotated_frame)

            # 🔍 DEBUG LOGS
            print("📤 Attempting to send email alert now...")

            # 📤 Send email with attached frame + log
            send_email_alert(
                frame_path=frame_path,
                log_path="alert_log.csv",
                location=location,
                timestamp=timestamp_str,
                frame_number=frame_count
            )

            print("✅ Email function executed for frame:", frame_count)

        frame_count += 1

    cap.release()
    st.success(f"✅ Detection Complete!\n\nTotal Frames: {frame_count}, Total Dogs Detected: {total_dog_count}")
    st.download_button("📥 Download Alert Log (CSV)", data=open("alert_log.csv").read(), file_name="alert_log.csv")
