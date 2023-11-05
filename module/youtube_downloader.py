from pytube import YouTube
from pytube.exceptions import VideoUnavailable
import os

MAX_SIZE_MB = 100

def download_yt_audio(url="", folder="temp/", extension=".mp3"):
    try:
        yt = YouTube(url)
        audio_stream = yt.streams.filter(only_audio=True).first()
        if audio_stream.filesize_mb > MAX_SIZE_MB:
            return "too_large"
        path = audio_stream.download(output_path=folder)
        base, ext = os.path.splitext(path)
        new_file = base + extension
        os.rename(path, new_file)
        return new_file
    except VideoUnavailable:
        return "unavailable"
    except:
        return "error"

def download_yt_video(url="", folder="temp/"):
    try:
        yt = YouTube(url)
        video_stream = yt.streams.filter(only_video=True).get_highest_resolution()
        if video_stream.filesize_mb > MAX_SIZE_MB:
            return "too_large"
        return video_stream.download(output_path=folder)
    except VideoUnavailable:
        return "unavailable"
    except:
        return "error"
