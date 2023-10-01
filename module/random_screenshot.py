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

def save_image(name, image_data):
    with open(name, 'wb') as file:
        file.write(image_data)
