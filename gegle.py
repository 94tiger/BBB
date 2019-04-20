import requests
from bs4 import BeautifulSoup
import re

pattern = re.compile((r'\s+'))

def get_html(url):
    _html = ""
    resp = requests.get(url)
    # status_code가 정상이면
    if resp.status_code == 200:
        _html = resp.text
    return _html

def get_gegle(gallery):
    URL = ("https://gall.dcinside.com/board/lists?id=" + str(gallery) + "&exception_mode=recommend")
    # URL = "https://gall.dcinside.com/board/lists?id=baseball_new7&exception_mode=recommend"
    html = get_html(URL)
    soup = BeautifulSoup(html, 'html.parser')

    element = soup.find('table', {'class': 'gall_list'})
    element = element.find_all('tr', {'class' : 'ub-content'})

    gegle = []
    i = 1
    j = 6
    while i < j:
        line = []
        link = element[i]
        gegle_number = str(link)[str(link).find('um">') + 4:str(link).find('</td>')]
        # 념글 번호로 공지여부 판별
        if gegle_number.isdigit():
            link = element[i].find('td', {'class': 'gall_tit ub-word'})

            gegle_link = link.find('a')['href']
            gegle_name = str(link)[str(link).find('/em>') + 4:str(link).find('</a>')]
            gegle_reply = str(link)[str(link).find('um">') + 4:str(link).find('</span')]

            line.append(gegle_name)
            line.append(gegle_reply)
            line.append('http://gall.dcinside.com' + gegle_link)

            gegle.append(line)
        else:
            j += 1
        i += 1
        # gegle = [index, [제목, 리플수, 링크]]

    return gegle

def get_mgegle(gallery):
    URL = ("https://gall.dcinside.com/mgallery/board/lists?id=" + str(gallery) + "&exception_mode=recommend")

    html = get_html(URL)
    soup = BeautifulSoup(html, 'html.parser')

    element = soup.find('table', {'class': 'gall_list'})
    element = element.find_all('tr', {'class': 'ub-content us-post'})
    gegle = []
    i = 1
    gegle_endNum = 6
    while i < gegle_endNum:
        line = []
        link = element[i]
        gegle_number = str(link)[str(link).find('um">') + 4:str(link).find('</td>')]
        # 념글 번호로 공지여부 판별
        if gegle_number.isdigit():
            link = element[i].find('td', {'class': 'gall_tit ub-word'})
            gegle_link = link.find('a')['href']
            gegle_name = str(link)[str(link).find('/em>') + 4:str(link).find('</a>')]
            gegle_reply = str(link)[str(link).find('um">') + 4:str(link).find('</span')]

            line.append(gegle_name)
            line.append(gegle_reply)
            line.append('http://gall.dcinside.com' + gegle_link)

            gegle.append(line)
        else:
            gegle_endNum += 1
        i += 1
    return gegle

def get_dogdrip():
    URL = ("https://www.dogdrip.net/dogdrip")
    # URL = "https://gall.dcinside.com/board/lists?id=baseball_new7&exception_mode=recommend"
    html = get_html(URL)
    soup = BeautifulSoup(html, 'html.parser')

    element = soup.find_all('td', {'class': 'title'})

    dogdrip = []
    for i in range(1, 6):
        line = []

        link = element[i]
        dogdrip_link = link.find('a')['href']
        dogdrip_name = link.find("span", {"class": "ed title-link"}).text
        dogdrip_reply = link.find("span", {"class": "ed text-primary"}).text

        line.append(dogdrip_name)
        line.append("[" + dogdrip_reply + "]")
        line.append(dogdrip_link)

        dogdrip.append(line)
        # gegle = [index, [제목, 리플수, 링크]]

    # 리스트 출력
    # for i in range(len(dogdrip)):
    #     for j in range(len(line)):
    #         print(dogdrip[i][j])
    #     print()
    return dogdrip

    # URL = "https://gall.dcinside.com/board/lists?id=baseball_new7&exception_mode=recommend"

