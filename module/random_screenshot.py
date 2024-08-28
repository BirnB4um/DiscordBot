import requests
from bs4 import BeautifulSoup
import random
import time

abc = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

headers = {
    "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Sec-Fetch-Dest": "image",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
}


def get_random_id(len=6):
    return "".join(random.choices(abc, k=len))

def check_image(url):
    response = requests.get(url, headers=headers, allow_redirects=False)

    if response.status_code != 200:
        return False
    
    # if not image
    if "image" not in response.headers["Content-Type"]:
        return False
    
    # if default 'removed' image
    if response.headers["Content-Length"] == "503":
        return False
    
    return response.content

def get_random_screenshot():
    sleep_between_tries = 0.5
    max_tries = 20
    for tries in range(1, max_tries+1):
        id = get_random_id(5)
        url = "https://i.imgur.com/" + id + ".png"
        data = check_image(url)
        if not data:
            time.sleep(sleep_between_tries)
            continue

        return url, data, tries
    return None, None, max_tries

