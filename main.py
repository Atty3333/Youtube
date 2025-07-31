import os
import logging
from core.video_editor import VideoEditor
from core.uploader import Uploader
from core.organizer import Organizer
from core.account_manager import AccountManager
from core.select_beat import select_beat
from core.select_beat import title_extract
from core.download_video import search_and_download

from core.thumbnail_generator import get_or_generate_thumbnail
import traceback
import smtplib
from email.mime.text import MIMEText



def send_email_error(subject, error_message):
    sender_email = "Mutemaletso@gmail.com"
    receiver_email = "Mutemaletso@gmail.com"
    app_password = "lscq ihxb wfmr mzyt"

    msg = MIMEText(error_message)
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = receiver_email

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, app_password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
        print("✅ Error email sent.")
    except Exception as e:
        print("❌ Failed to send error email:", str(e))


# Setup basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    manager = AccountManager()

    for channel_name, account in manager.get_all_accounts():
        try:
            Video_keyword="21 savage music video"
            thumbnail_keyword="21 savage type beat"
            logging.info(f"Uploading for {channel_name}...")

            beats_dir = "beats"
            beat_files = [f for f in os.listdir(beats_dir) if f.endswith(".mp3")]
            if not beat_files:
                logging.warning("No beat files found in the 'beats' folder. Skipping this account.")
                continue

            # Beat selection
            beat_file, _ = select_beat()
            beat_path = os.path.join(beats_dir, beat_file)

            title_file = beat_file
            description_file = os.path.join(beats_dir, "description.txt")
            tags_file = os.path.join(beats_dir, "tags.txt")

            # Download video
            print("Downliang")  
            try:
                download_video_path = search_and_download(Video_keyword)
                if not os.path.exists(download_video_path):
                    logging.error("Downloaded video not found. Skipping this account.")
                    continue
            except Exception as e:
                logging.error(f"Download failed: {e}")
                continue

            # Video creation
            print("editing")
            editor = VideoEditor()
            try:
                final_video_path,  title = editor.create_type_beat_video(
                    beat_path=beat_path,
                    download_video_path=download_video_path,  # ✅ Correct
                    title_file=title_file
                )
            except Exception as e:
                logging.error(f"Video creation failed: {e}")
                traceback.print_exc()
                continue
            
            # Thumbnail
            try:
                thumbnail_path = get_or_generate_thumbnail(thumbnail_keyword,final_video_path)
            except Exception as e:
                logging.warning(f"Thumbnail generation failed, using default thumbnail. Error: {e}")
                thumbnail_path="default_thumbnail.jpg"
               
            print("Upload")

            # Upload
            try:
                title,description,beat_number=title_extract(title)
                uploader = Uploader(account)
                
                tags = open(tags_file).read().split(",")
                uploader.upload_video(
                    video_path=final_video_path,
                    title=title,
                    description=description,
                    tags=tags,
                    thumbnail_path=thumbnail_path
                )
            except Exception as e:
                logging.error(f"Upload failed: {e}")
                traceback.print_exc()
                continue
            print("Organizing")           
            # Organize posted content
            Organizer.setup_beat_folder(channel_name,title,description,beat_number,thumbnail_path)
           
            Organizer.clear(thumbnail_path,final_video_path,download_video_path)
            

        except Exception as e:
            logging.exception(f"Unexpected error for {channel_name}: {e}")
            error=traceback.print_exc()
            send_email_error("Youtube bot error",error)

if __name__ == "__main__":
    main()
#video quality


#future update:
#save the bpm from the beat filename
#allow it to download thumbnails and use them and not always making thumbnail

