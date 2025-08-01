# core/download_video.py

from yt_dlp import YoutubeDL
import traceback
import yt_dlp
import os
import random
from pytubefix import YouTube
from moviepy.editor import VideoFileClip, AudioFileClip

def search_and_download(keyword, output_path=os.path.normpath('clips/source_video.mp4'), duration_limit=300):
    
        # Get the directory one level above the current file (i.e., the project root)
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Construct the correct path to clips/source_video.mp4
    output_path = os.path.join(PROJECT_ROOT, 'clips', 'source_video.mp4')

    ydl_opts = {
        'quiet': True,
        'skip_download': True,
        'extract_flat': 'in_playlist',
        'force_generic_extractor': True,
        'default_search': 'ytsearch5',
    }

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"ytsearch10:{keyword}", download=False)  # search top 10 results
        entries = info.get('entries', [])

        # Filter by duration
        valid_videos = [entry for entry in entries if entry.get("duration", 0) <= duration_limit]

        if not valid_videos:
            print("❌ No videos found within the duration limit.")
            return None

        # Pick one at random
        selected = random.choice(valid_videos)
        video_url = selected["url"]  # use webpage_url not just "url" for full URL

        print(f"🎲 Randomly selected video: {selected['title']} ({selected['duration']}s)")
        return download_video(video_url, output_path,PROJECT_ROOT)
    print("❌ No suitable video found.")
    return None

def download_video(url, output_path,PROJECT_ROOT):#using ytdlp
    cookie=os.path.join(PROJECT_ROOT, 'youtube.com_cookies.txt')
    print(cookie)
    if not os.path.exists(cookie):
        raise FileNotFoundError(f"Cookies file not found: {cookie}")
    try:

            ydl_opts = {
                'format': 'bestvideo[height=360][ext=mp4]+bestaudio[ext=m4a]/mp4',  # 360p video with audio, fallback to mp4
                'outtmpl': output_path,
                'quiet': False,
                'merge_output_format': 'mp4',
                
                "retries": 10,  # ⬅️ retry up to 10 times
                "fragment_retries": 10,
                "socket_timeout": 30,
                "noplaylist": True,
                'cookies':cookie,

        
                'postprocessors': [
        
                    {
                        'key': 'FFmpegMetadata',
                    }
                ],
                'postprocessor_args': ['-an'],  # Mute audio by disabling it
            }
        
            with YoutubeDL(ydl_opts) as ydl:
                print(f"⬇️ Downloading: {url}")
                ydl.download([url])
            return output_path
    except Exception as e:
            traceback.print_exc()        


def download_video2(url, output_path,PROJECT_ROOT):#using pytube still developing
    try:
        print(f"⬇️ Downloading: {url}")
        
        yt = YouTube(url, use_po_token=True)

        # Get 360p video stream (video-only)
        video_stream = yt.streams.filter(progressive=False, file_extension='mp4', res="360p", only_video=True).first()
        # Get audio stream (audio-only)
        audio_stream = yt.streams.filter(only_audio=True, file_extension='mp4').first()

        if not video_stream or not audio_stream:
            print("❌ Could not find suitable video or audio streams.")
            return None

        # Temporary paths
        base, ext = os.path.splitext(output_path)
        video_temp = base + "_video.mp4"
        audio_temp = base + "_audio.mp4"

        # Download streams
        video_stream.download(filename=video_temp)
        audio_stream.download(filename=audio_temp)

        # Merge video + audio using moviepy
        video_clip = VideoFileClip(video_temp)
        audio_clip = AudioFileClip(audio_temp)

        final_clip = video_clip.set_audio(audio_clip)
        final_clip.write_videofile(output_path, codec="libx264", audio_codec="aac", remove_temp=True)

        # Cleanup
        video_clip.close()
        audio_clip.close()
        os.remove(video_temp)
        os.remove(audio_temp)

        print(f"✅ Saved to: {output_path}")
        return output_path

    except Exception as e:
        traceback.print_exc()
        return None
