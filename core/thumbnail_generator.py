import cv2
import os
import numpy as np
import random
import requests
from youtubesearchpython import VideosSearch
import traceback
import re

# Remove or replace invalid characters for Windows
def sanitize_filename(title):
    title = title[:50]  # Limit to 50 characters
    title = re.sub(r'[<>:"/\\|?*]', '', title)  # Remove invalid characters
    title = title.replace(' ', '_')  # Optional: replace spaces with _
    return title






def variance_of_laplacian(image):
    """Sharpness score"""
    return cv2.Laplacian(image, cv2.CV_64F).var()

def is_face_present(image, face_cascade):
    """Detects if at least one face is present"""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.1, 4)
    return len(faces) > 0

def score_frame(frame, face_cascade):
    """Returns a combined score for selecting best thumbnail frame"""
    score = 0
    sharpness = variance_of_laplacian(frame)
    brightness = np.mean(frame)
    has_face = is_face_present(frame, face_cascade)

    score += sharpness * 0.5  # prioritize sharpness
    score += brightness * 0.3  # moderately value brightness
    score += 1000 if has_face else 0  # big bonus for faces
    return score

def create_thumbnail(video_path, thumbnail_path="thumbnails/final_thumbnail.jpg", num_samples=25):
    try:
        """
        Picks the best frame from random points in the video using sharpness, brightness, and face detection.
        """
        if not os.path.exists(video_path):
            print(f"❌ Video not found: {video_path}")
            return None

        os.makedirs(os.path.dirname(thumbnail_path), exist_ok=True)

        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print("❌ Cannot open video")
            return None

        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = total_frames / fps
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

        best_frame = None
        best_score = -1

        # Pick random timestamps across the entire video
        random_times = sorted(random.sample(range(1, int(duration) - 1), num_samples))

        for t in random_times:
            cap.set(cv2.CAP_PROP_POS_MSEC, t * 1000)
            success, frame = cap.read()
            if not success:
                continue

            score = score_frame(frame, face_cascade)
            if score > best_score:
                best_score = score
                best_frame = frame

        cap.release()

        if best_frame is not None:
            cv2.imwrite(thumbnail_path, best_frame, [int(cv2.IMWRITE_JPEG_QUALITY), 95])
            print(f"✅ Best thumbnail saved at {thumbnail_path}")
            return thumbnail_path
        else:
            print("⚠️ Failed to extract any good frame.")
            return None
    except Exception as e:

            traceback.print_exc()

def download_thumbnail(keyword, thumbnail_path="thumbnails/final_thumbnail.jpg"):
    try:
        # Search YouTube using the keyword
        search = VideosSearch(keyword, limit=20)
        results = search.result().get("result", [])

        if not results:
            print(f"❌ No videos found for keyword: {keyword}")
            return None

        # Pick a random video
        video = random.choice(results)
        thumbnail_url = video['thumbnails'][-1]['url']
        title = video['title']

        # Ensure directory exists
        os.makedirs(os.path.dirname(thumbnail_path), exist_ok=True)

        # Generate file name
        safe_title = sanitize_filename(title)
        file_path = os.path.join(os.path.dirname(thumbnail_path), f"{safe_title}.jpg")

        try:
            response = requests.get(thumbnail_url, stream=True)
            if response.status_code == 200:
                with open(file_path, 'wb') as f:
                    for chunk in response.iter_content(1024):
                        f.write(chunk)
                print(f"✅ Downloaded thumbnail for: {title}")
                return file_path  # ✅ Correct path
            else:
                print("❌ Failed to download thumbnail.")
                return None
        except Exception as e:
            print(f"❌ Error while downloading: {e}")
            traceback.print_exc()
            return None
    except Exception as e:
        traceback.print_exc()
        return None



def get_or_generate_thumbnail(video_keyword, video_path):
    try:
        """
        Randomly decides whether to download or generate a thumbnail,
        saves it to thumbnail_path.
        """
        choice = random.choice(["download", "generate"])
        
        if choice == "download":
            print("Trying to download thumbnail...")
            thumbnail_path = download_thumbnail(video_keyword)
            
            if thumbnail_path is None:
                print("Download failed, generating placeholder instead.")
                thumbnail_path = create_thumbnail(video_path)
                return thumbnail_path
        else:
            print("Generating  thumbnail...")
            thumbnail_path = create_thumbnail(video_path)
            return thumbnail_path
        
        # Save the thumbnail image

        print(f"Thumbnail saved to: {thumbnail_path}")    
    except Exception as e:

            traceback.print_exc()    