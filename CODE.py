import streamlit as st
import cv2
import numpy as np
from moviepy.editor import VideoFileClip, ImageClip, concatenate_videoclips
import tempfile
import os

# Function to apply a simple edit (sepia filter) to an image
def apply_edit(image):
    # Convert to sepia (example edit)
    sepia_filter = np.array([[0.272, 0.534, 0.131],
                             [0.349, 0.686, 0.168],
                             [0.393, 0.769, 0.189]])
    sepia_image = cv2.transform(image, sepia_filter)
    sepia_image = np.clip(sepia_image, 0, 255).astype(np.uint8)
    return sepia_image

# Function to process video: apply edit to each frame
def process_video(video_path, output_path):
    cap = cv2.VideoCapture(video_path)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, 30.0, (int(cap.get(3)), int(cap.get(4))))
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        edited_frame = apply_edit(frame)
        out.write(edited_frame)
    
    cap.release()
    out.release()

# Function to create a video from edited photo (repeat for video duration)
def create_video_from_photo(photo_path, video_duration, output_path):
    image = cv2.imread(photo_path)
    edited_image = apply_edit(image)
    
    # Create a clip from the edited image
    clip = ImageClip(edited_image).set_duration(video_duration)
    clip.write_videofile(output_path, fps=30)

# Streamlit App
st.title("Video Edit App")
st.write("Upload a demo video and a photo. Apply a sepia edit to the video, then create a similar video from the edited photo.")

uploaded_video = st.file_uploader("Upload Demo Video (MP4)", type=["mp4"])
uploaded_photo = st.file_uploader("Upload Photo (JPG/PNG)", type=["jpg", "png"])

if uploaded_video and uploaded_photo:
    # Save uploads to temp files
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video:
        temp_video.write(uploaded_video.read())
        video_path = temp_video.name
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_photo:
        temp_photo.write(uploaded_photo.read())
        photo_path = temp_photo.name
    
    # Get video duration
    clip = VideoFileClip(video_path)
    duration = clip.duration
    clip.close()
    
    # Process demo video
    edited_video_path = tempfile.mktemp(suffix=".mp4")
    process_video(video_path, edited_video_path)
    
    # Create new video from edited photo
    new_video_path = tempfile.mktemp(suffix=".mp4")
    create_video_from_photo(photo_path, duration, new_video_path)
    
    # Display results
    st.video(edited_video_path)
    st.write("Edited Demo Video")
    
    st.video(new_video_path)
    st.write("New Video from Edited Photo")
    
    # Download buttons
    with open(edited_video_path, "rb") as f:
        st.download_button("Download Edited Demo Video", f, file_name="edited_demo.mp4")
    
    with open(new_video_path, "rb") as f:
        st.download_button("Download New Video", f, file_name="new_video.mp4")
    
    # Cleanup
    os.unlink(video_path)
    os.unlink(photo_path)
    os.unlink(edited_video_path)
    os.unlink(new_video_path)