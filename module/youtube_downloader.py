from pytube import YouTube
from pytube.exceptions import VideoUnavailable

MAX_SIZE_MB = 100

def download_yt_audio(url=""):
    try:
        yt = YouTube(url)
        audio_stream = yt.streams.filter(only_audio=True).first()
        if audio_stream.filesize_mb > MAX_SIZE_MB:
            return "too_large"
        return audio_stream.download(output_path="temp/")
    except VideoUnavailable:
        return "unavailable"
    except:
        return "error"

def download_yt_video(url=""):
    try:
        yt = YouTube(url)
        video_stream = yt.streams.get_highest_resolution()
        if video_stream.filesize_mb > MAX_SIZE_MB:
            return "too_large"
        return video_stream.download(output_path="temp/")
    except VideoUnavailable:
        return "unavailable"
    except:
        return "error"
