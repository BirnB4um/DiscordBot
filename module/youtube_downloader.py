from pytube import YouTube
from pytube.exceptions import VideoUnavailable


def download_yt_audio(url=""):
    try:
        yt = YouTube(url)
        audio_stream = yt.streams.filter(only_audio=True).first()
        return audio_stream.download(output_path="temp/")
    except VideoUnavailable:
        return "unavailable"
    except:
        return "error"

def download_yt_video(url=""):
    try:
        yt = YouTube(url)
        video_stream = yt.streams.get_highest_resolution()
        return video_stream.download(output_path="temp/")
    except VideoUnavailable:
        return "unavailable"
    except:
        return "error"

download_yt_audio("https://youtu.be/7UubKYqEy3s?si=8H1uxqC28tGgrLVe")