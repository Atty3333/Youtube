# core/download_video.py

from yt_dlp import YoutubeDL

import yt_dlp
import os
import random

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
        return download_video(video_url, output_path)
    print("❌ No suitable video found.")
    return None

def download_video(url, output_path):
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
                'cookies': '../youtube.com_cookies.txt',
        
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
