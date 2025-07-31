
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import pickle
import os

from google_auth_oauthlib.flow import InstalledAppFlow


class Uploader:
    def __init__(self, account):
        self.service = self.authenticate(account)

    def authenticate(self, account):
        """
        Authenticates a YouTube account. If token is missing, creates one from client_secret.json.

        :param account: A dictionary with 'token_path' and 'secret_path'
        :return: Authenticated YouTube API service object
        """
        scopes = ["https://www.googleapis.com/auth/youtube.upload"]
        token_path = account['token_path']
        secret_path = account['secret_path']

        # Load token if it exists
        if os.path.exists(token_path):
            with open(token_path, 'rb') as f:
                creds = pickle.load(f)
        else:
            # If token doesn't exist, create one using the client secret
            flow = InstalledAppFlow.from_client_secrets_file(secret_path, scopes)
            creds = flow.run_local_server(port=0)

            # Save the new token
            with open(token_path, 'wb') as f:
                pickle.dump(creds, f)

        return build('youtube', 'v3', credentials=creds)

    def upload_video(self, video_path, title, description, tags, thumbnail_path):
        request_body = {
            'snippet': {
                'title': title,
                'description': description,
                'tags': tags
            },
            'status': {
                'privacyStatus': 'public'
            }
        }

        media = MediaFileUpload(video_path, chunksize=-1, resumable=True)
        request = self.service.videos().insert(
            part='snippet,status',
            body=request_body,
            media_body=media
        )
        response = request.execute()

        self.service.thumbnails().set(
            videoId=response['id'],
            media_body=MediaFileUpload(thumbnail_path)
        ).execute()
