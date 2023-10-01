import requests
from bs4 import BeautifulSoup


def get_list_of_gifs(search):

    URL = "https://tenor.com/de/search/" + search + "-gifs"
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    page = requests.get(URL, headers=headers)
    soup = BeautifulSoup(page.content, "html.parser")
    columns = soup.find_all(class_="column")
    list = []

    for column in columns:
        gifs = column.find_all(class_="Gif")
        for gif in gifs:
            list.append(gif.img["src"])

    return list