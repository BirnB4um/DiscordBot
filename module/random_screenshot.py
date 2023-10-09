import requests
from bs4 import BeautifulSoup
import random
from time import sleep

abc = "abcdefghijklmnopqrstuvwxyz0123456789"#"abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
#headers = {'User-Agent': 'Chrome'}

not_working_links = [ "//st.prntscr.com/2022/09/11/1722/img/0_173a7b_211be8ff.png", 
                    "https://i.imgur.com/TpcUYdH.jpg", 
                    "https://i.imgur.com/Uuh3Nj4.jpg", 
                    "https://i.imgur.com/OqQcO7h.jpg"]

def get_random_id(len=6):
    return "".join(random.choice(abc) for i in range(len))

def get_image_url(id):
    url = "https://prnt.sc/" + id
    try:
        page = requests.get(url, headers=headers)
    except:
        return -1
    soup = BeautifulSoup(page.content, "html.parser")

    src = soup.find_all(class_="no-click screenshot-image")
    if len(src) == 0:
        return -1

    if src[0]["src"] in not_working_links :#check if image was removed
        return -1
    
    return src[0]["src"]


def get_image_data(src_url):
    try:
        img = requests.get(src_url, headers=headers)
    except:
        return -1
    if not img.status_code == 200:#check if image is available
        return -1
    return img.content

def get_random_screenshot():
    sleep_between_tries = 2
    max_tries = 10
    tries = 0
    while True:
        tries += 1
        if tries > max_tries:
            sleep(sleep_between_tries)
            return None, None, None, tries

        id = get_random_id(6)
        url = get_image_url(id)
        if url == -1:
            sleep(sleep_between_tries)
            continue

        data = get_image_data(url)
        if data == -1:
            sleep(sleep_between_tries)
            continue   
        if len(data) == 503:
            sleep(sleep_between_tries)
            continue

        return id, url, data, tries

def save_image(name, image_data):
    with open(name, 'wb') as file:
        file.write(image_data)
