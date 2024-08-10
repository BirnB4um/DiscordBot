from pytube import YouTube, innertube
from pytube.exceptions import VideoUnavailable, RegexMatchError, AgeRestrictedError
import googleapiclient.discovery
from googleapiclient.errors import HttpError
import os
from datetime import datetime
import time


it = innertube.InnerTube(use_oauth=True)
use_oauth = True
token_start_time = 0
token_response = None
youtube_api = None
MAX_SIZE_MB = 25

def load_youtube_api():
    global youtube_api
    api_key = os.getenv('YOUTUBE_API_KEY')
    youtube_api = googleapiclient.discovery.build("youtube", "v3", developerKey=api_key)


def get_token_refresh_url():
    global it, token_start_time, token_response
    it = innertube.InnerTube(use_oauth=True)
    token_start_time = int(time.time() - 30)
    data = {
        'client_id': innertube._client_id,
        'scope': 'https://www.googleapis.com/auth/youtube'
    }
    response = innertube.request._execute_request(
        'https://oauth2.googleapis.com/device/code',
        'POST',
        headers={
            'Content-Type': 'application/json'
        },
        data=data
    )
    token_response = innertube.json.loads(response.read())
    verification_url = token_response['verification_url']
    user_code = token_response['user_code']
    return verification_url, user_code


def refresh_token():
    global it
    data = {
        'client_id': innertube._client_id,
        'client_secret': innertube._client_secret,
        'device_code': token_response['device_code'],
        'grant_type': 'urn:ietf:params:oauth:grant-type:device_code'
    }
    response = innertube.request._execute_request(
        'https://oauth2.googleapis.com/token',
        'POST',
        headers={
            'Content-Type': 'application/json'
        },
        data=data
    )
    response_data = innertube.json.loads(response.read())

    it.access_token = response_data['access_token']
    it.refresh_token = response_data['refresh_token']
    it.expires = token_start_time + response_data['expires_in']
    it.cache_tokens()


def token_expired():
    global use_oauth
    _it = innertube.InnerTube(use_oauth=True)
    if _it.expires == None:
        use_oauth = False
        return True
    if time.time() > _it.expires:
        use_oauth = False
        return True
    use_oauth = True
    return False


def get_token_expiration():
    _it = innertube.InnerTube(use_oauth=True)
    return _it.expires


def get_yt_thumbnail(url=""):
    try:
        yt = YouTube(url, use_oauth=use_oauth and not token_expired())
        return yt.thumbnail_url.split("?")[0]
    except AgeRestrictedError:
        return "age_restricted"
    except VideoUnavailable:
        return "unavailable"
    except RegexMatchError:
        return "regex_error"
    except:
        return "error"


def check_video(url, max_duration=60*10):
    try:
        yt = YouTube(url, use_oauth=use_oauth and not token_expired())
        if yt.length > max_duration:
            return False

        try:
            yt.streams
        except:
            return False

        return True
    except:
        return False


def get_search_result(query, category_id=10, max_results=50):
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
    return video_ids


def download_yt_audio(url="", folder="temp/", extension="mp4", size_limit=MAX_SIZE_MB):
    try:
        yt = YouTube(url, use_oauth=use_oauth and not token_expired())

        audio_stream = yt.streams.filter(mime_type="audio/"+extension).order_by('abr').desc()

        if len(audio_stream) == 0:
            return "no_stream"

        chosen_stream = None
        for stream in audio_stream:
            if stream.filesize_mb < size_limit:
                chosen_stream = stream
                break

        if chosen_stream is None:
            return "too_large"
        
        path = chosen_stream.download(output_path=folder)
        
        if extension == "mp4":
            base, ext = os.path.splitext(path)
            new_file = base + ".mp3"
            if os.path.isfile(new_file):
                os.remove(new_file)
            os.rename(path, new_file)
            path = new_file

        return path
    
    except AgeRestrictedError:
        return "age_restricted"
    except VideoUnavailable:
        return "unavailable"
    except RegexMatchError:
        return "regex_error"
    except:
        return "error"


def download_yt_video(url="", folder="temp/", extension="mp4", include_audio=True, size_limit=MAX_SIZE_MB):
    try:
        yt = YouTube(url, use_oauth=use_oauth and not token_expired())
        video_stream = yt.streams.filter(mime_type="video/"+extension).order_by('resolution').desc()

        chosen_stream = None
        streams_exist = False
        for stream in video_stream:
            if stream.includes_audio_track != include_audio:
                continue
            streams_exist = True
            if stream.filesize_mb < size_limit:
                chosen_stream = stream
                break

        if streams_exist == False:
            return "no_stream"
        
        if chosen_stream is None:
            return "too_large"
        
        return chosen_stream.download(output_path=folder)
    
    except AgeRestrictedError:
        return "age_restricted"
    except VideoUnavailable:
        return "unavailable"
    except RegexMatchError:
        return "regex_error"
    except:
        return "error"
    
