import requests
from bs4 import BeautifulSoup

def get_ihtml(url):
    _ihtml = ""
    iresp = requests.get(url)
    #status_code가 정상이면
    if iresp.status_code == 200:
        _ihtml = iresp.text
    return _ihtml

def get_image(code):
    schCode = code
    URL = ("https://search.naver.com/search.naver?&where=image&query=" + schCode)
    ihtml = get_ihtml(URL)
    isoup = BeautifulSoup(ihtml, 'html.parser')
    ielement = isoup.find_all('div', class_='img_area _item')
    ielement = ielement[0]
    ielement = str(ielement)[str(ielement).find('ce="')+4:str(ielement).find(';type=b400"')]
    return ielement