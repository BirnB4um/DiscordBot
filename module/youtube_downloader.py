from pytube import YouTube
from pytube.exceptions import VideoUnavailable
import os

MAX_SIZE_MB = 25

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
            os.rename(path, new_file)
            path = new_file

        return path
    
    except VideoUnavailable:
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
        
        return chosen_stream.download(output_path=folder)
    
    except VideoUnavailable:
        return "unavailable"
    except:
        return "error"
