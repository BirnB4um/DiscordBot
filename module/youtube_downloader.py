from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError, RegexNotFoundError
import googleapiclient.discovery
from googleapiclient.errors import HttpError
import os
from datetime import datetime
import time
import random
import traceback

youtube_api = None
MAX_SIZE_MB = 10

def load_youtube_api():
    global youtube_api
    api_key = os.getenv('YOUTUBE_API_KEY')
    youtube_api = googleapiclient.discovery.build("youtube", "v3", developerKey=api_key)


def get_yt_thumbnail(url=""):

    try:
        ydl_opts = {
            'noplaylist': True,
            'no_warnings': True,
            'quiet': True,
        }

        with YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            thumbnail_url = info_dict.get('thumbnail', None)
            if thumbnail_url:
                return thumbnail_url, None
            else:
                return "error", "Thumbnail not found"

    except Exception as e:
        print("Thumbnail Error:", traceback.format_exc())
        return "error", str(e)



def get_search_result(query, category_id=10, max_results=20, shuffle=False):
    if youtube_api is None:
        return None
    try:
        search_response = youtube_api.search().list(
            q=query,
            type="video",
            part="id,snippet",
            order="relevance",
            videoDuration="any",
            safeSearch="none",
            maxResults=max_results,
            videoCategoryId=category_id, # default = 10 (Music)
        ).execute()
    except HttpError as e:
        error_message = e.content.decode("utf-8")
        if "quotaExceeded" in error_message:
            print("ERROR: Youtube API Quota exceeded.")
        else:
            print(f"ERROR: An HTTP error occurred: {error_message}")
        return None
    except Exception as e:
        print("ERROR: Youtube API", e)
        return None

    if len(search_response["items"]) == 0:
        return None

    video_ids = ["https://www.youtube.com/watch?v=" + id["id"]["videoId"] for id in search_response["items"] if id["snippet"]["liveBroadcastContent"] == "none"]
    
    if(shuffle):
        random.shuffle(video_ids)

    return video_ids


def download_yt_video(url="", folder="temp/", extension="mp4", size_limit=MAX_SIZE_MB):
    """
    size_limit in MB
    """

    try:
        size_limit_bytes = size_limit * 1024 * 1024

        ydl_opts = {
            'format': f'bestvideo[filesize<{size_limit_bytes}]+bestaudio[filesize<{size_limit_bytes}]/best[filesize<{size_limit_bytes}]',
            'outtmpl': os.path.join(folder, '%(title)s.%(ext)s'),
            'merge_output_format': extension,
            'postprocessors': [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': extension,
            }],
            'noplaylist': True,
            'restrictfilenames': True,
            'no_warnings': True,
            'quiet': True,
        }

        with YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            file_name = ydl.prepare_filename(info_dict).replace("\\", "/").rsplit('.', 1)[0] + f'.{extension}'
            return file_name, None

    except Exception as e:
        print(traceback.format_exc())
        return "error", str(e)


def download_yt_audio(url="", folder="temp/", extension="mp3", size_limit=MAX_SIZE_MB):
    """
    size_limit in MB
    """

    try:

        size_limit_bytes = size_limit * 1024 * 1024
        ydl_opts = {
            'format': f'bestaudio[filesize<{size_limit_bytes}]',
            'outtmpl': os.path.join(folder, '%(title)s.%(ext)s'),
            'merge_output_format': extension,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': extension,
                'preferredquality': '192',
            }],
            'noplaylist': True,
            'restrictfilenames': True,
            'no_warnings': True,
            'quiet': True,
        }
        
        with YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            file_name = ydl.prepare_filename(info_dict).replace("\\", "/").rsplit('.', 1)[0] + f'.{extension}'
            return file_name, None

    except Exception as e:
        print(traceback.format_exc())
        return "error", str(e)
