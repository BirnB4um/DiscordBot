import youtube_dl
import time

download_path = "pathhhh"
download_duration = 1
download_error = "no error"

def download_audio(path = "", link="", type="wav"):
    global download_error, download_duration, download_path
    
    try:
        video_info = youtube_dl.YoutubeDL().extract_info(url = link,download=False)
    except:
        download_error = "Error: youtube url is not valid!"
        return False

    filename = video_info['title'].replace("/", "").replace("\\", "").replace(" ", "_")
    filepath = f"{path}{filename}.{type}"
    download_path = filepath
    options={
        'format':'bestaudio/best',
        'keepvideo':False,
        'outtmpl':filepath,
    }
    start_time = time.time()
    try:
        with youtube_dl.YoutubeDL(options) as ydl:
            ydl.download([video_info['webpage_url']])
    except:
        download_error = "Error: Downloading failed!"
        return False
    download_duration = time.time() - start_time

    return True