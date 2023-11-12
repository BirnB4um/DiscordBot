from pytube import YouTube
from pytube.exceptions import VideoUnavailable, RegexMatchError
import googleapiclient.discovery
import os
from datetime import datetime

youtube_api = None
MAX_SIZE_MB = 25

def load_youtube_api():
    global youtube_api
    api_key = os.getenv('YOUTUBE_API_KEY')
    youtube_api = googleapiclient.discovery.build("youtube", "v3", developerKey=api_key)

def get_yt_thumbnail(url=""):
    try:
        yt = YouTube(url)
        return yt.thumbnail_url.split("?")[0]
    except VideoUnavailable:
        return "unavailable"
    except:
        return "error"


def get_search_result(query, category_id=10, max_results=1):
    if youtube_api is None:
        return None
    try:
        search_response = youtube_api.search().list(
            q=query,
            type="video",
            part="id",
            order="relevance",
            videoDuration="any",
            safeSearch="none",
            maxResults=max_results,
            videoCategoryId=category_id, # default = 10 (Music)
        ).execute()
    except:
        print("ERROR: Youtube API")
        return None

    if len(search_response["items"]) == 0:
        return None

    video_id = search_response["items"][0]["id"]["videoId"]
    return "https://www.youtube.com/watch?v=" + video_id


def download_yt_audio(url="", folder="temp/", extension="mp4"):
    try:
        yt = YouTube(url)
        audio_stream = yt.streams.filter(mime_type="audio/"+extension).order_by('abr').desc()

        if len(audio_stream) == 0:
            return "no_stream"

        chosen_stream = None
        for stream in audio_stream:
            if stream.filesize_mb < MAX_SIZE_MB:
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
    
    except VideoUnavailable:
        return "unavailable"
    except RegexMatchError:
        return "unavailable"
    except:
        return "error"



def download_yt_video(url="", folder="temp/", extension="mp4", include_audio=True):
    try:
        yt = YouTube(url)
        video_stream = yt.streams.filter(mime_type="video/"+extension).order_by('resolution').desc()

        chosen_stream = None
        streams_exist = False
        for stream in video_stream:
            if stream.includes_audio_track != include_audio:
                continue
            streams_exist = True
            if stream.filesize_mb < MAX_SIZE_MB:
                chosen_stream = stream
                break

        if streams_exist == False:
            return "no_stream"
        
        if chosen_stream is None:
            return "too_large"
        
        name = "".join([c for c in chosen_stream.default_filename if c.isalpha() or c.isdigit() or c in [" ", "_", "-"]]).rstrip()
        return chosen_stream.download(output_path=folder, filename=name)
    
    except VideoUnavailable:
        return "unavailable"
    except RegexMatchError:
        return "unavailable"
    except:
        return "error"



if __name__ == "__main__":
    url = "https://www.youtube.com/watch?v=ZRtdQ81jPUQ"
    print(download_yt_audio(url))