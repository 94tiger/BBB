# coding: utf-8

import requests
from bs4 import BeautifulSoup
import re
from selenium import webdriver

pattern = re.compile((r'\s+'))

def get_html(url):
    _html = ""
    resp = requests.get(url)
    # status_code가 정상이면
    if resp.status_code == 200:
        _html = resp.text
    return _html

def get_gegle(gallery):
    """
    :param gallery : 갤러리 str ex)야구갤러리 baseball_new7
    :return: [index, [제목, 리플수, 링크]]
    """
    if str(gallery) == "issuezoom" or str(gallery) == "hit":
        URL = ("https://gall.dcinside.com/board/lists?id=" + str(gallery))
    else:
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

def get_dogdrip_post():
    URL = "https://www.dogdrip.net/dogdrip"
    dogdrip_post = []

    chrome_options = webdriver.ChromeOptions()
    # chrome_options.add_extension('Adblock-Plus-kostenloser-Adblocker_v3.5.2.crx')
    chrome_options.add_argument('headless')
    chrome_options.add_argument('disable-extensions')
    chrome_options.add_argument('disable-dev-shm-usage')
    chrome_options.add_argument('disable-gpu')
    chrome_options.add_argument('no-sandbox')
    chrome_options.add_argument("lang=ko_KR") # 한국어!
    # chrome_options.add_argument('window-size=1920x1080')
    # chrome_options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36")
    driver = webdriver.Chrome('./chromedriver', chrome_options=chrome_options)
    # driver.set_window_size(550, 1000)
    driver.set_window_size(700, 700)
    driver.implicitly_wait(3)

    # 개드립 접속
    driver.get(URL)
    driver.implicitly_wait(3)
    print("접속 성공")

    # 개드립 첫번째 글 검색
    post = driver.find_element_by_xpath("//td[@class='title']/a")
    post_link = post.get_attribute('href')
    dogdrip_post.append(post_link)

    # 게시글 정보 확인
    title = driver.find_element_by_xpath("//span[@class='ed title-link']")
    dogdrip_post.append(title.text)

    comment = driver.find_element_by_xpath("//span[@class='ed text-primary']")
    dogdrip_post.append(comment.text)

    # 게시글 이동
    driver.get(post_link)

    # 1페이지 버튼 클릭
    if int(dogdrip_post[2]) > 50:
        commentp1btn = driver.find_element_by_xpath("//div[@class='ed pagination-container']/ul[@class='ed pagination pagewide']/li/a[(contains(text(), '1'))]")
        commentp1btn.click()

    # 광고 가리기
    # driver.execute_script("window.scrollTo(0, 0)")
    driver.execute_script("window.scrollTo(0, 250)")

    # 캡처
    driver.save_screenshot('./result/dogdrip.png')
    print("캡처 성공\n")
    # post = driver.find_element_by_class_name('inner-container')
    # post.screenshot('./result/dogdrip.png')

    # 종료
    driver.quit()

    return dogdrip_post
