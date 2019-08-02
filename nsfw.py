# coding: utf-8

from bs4 import BeautifulSoup
import requests
from requests import get
from requests import post
import config
import pymysql
import discord
import asyncio
import random


def get_html(url, referer):
    headers = {
        'Accept-Language': 'ko',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36',
        'referer': referer
    }
    _html = ""
    resp = requests.get(url, headers = headers)
    # status_code가 정상이면
    if resp.status_code == 200:
        _html = resp.text
    return _html


def post_html(url, referer, data, cookies):
    headers = {
        'Accept-Language': 'ko',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36',
        'referer': referer
    }
    _html = ""
    resp = requests.post(url, headers=headers, data=data, cookies=cookies)
    # status_code가 정상이면
    if resp.status_code == 200:
        _html = resp.text
    return _html


def gezip():
    first_page = "http://gezip.net/"
    second_page = "http://gezip.net/bbs/board.php?bo_table=sexy"
    # 로그인할 유저정보를 넣어주자 (모두 문자열)
    header = {
        'Accept-Language': 'ko',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36',
        'referer': first_page
    }
    cookies = {
        'PHPSESSID': 'ee1917788fec2eeb9c3663b67760fd4f',
        '2a0d2363701f23f8a75028924a3af643': 'MjE4LjE0OC4xOTYuMTcw;',
        'e1192aefb64683cc97abb83c71057733': 'c2V4eQ%3D%3D'
    }
    login_info = {
        'mb_id': config.gezip_id,
        'mb_password': config.gezip_pw,
        'url': '%2F'
    }
    # LOGIN_INFO = {**LOGIN_INFO, **{''}}

    # Session 생성, with 구문 안에서 유지
    with requests.Session() as s:
        # HTTP POST request: 로그인을 위해 POST url와 함께 전송될 data를 넣어주자.
        login = s.post(first_page, headers=header, data=login_info, cookies=cookies)
        print("서버 상태 : " + str(login.status_code))
        # 여기서부터는 로그인 된 세션이 유지됨 (s.get()으로 다른 페이지로 이동해도 됨)
        # 찰카닥 게시판 접속
        # soup = BeautifulSoup(login.text, 'html.parser')
        # print(soup)
        html = s.post(second_page, headers=header, data=login_info, cookies=cookies)
        soup = BeautifulSoup(html.text, 'html.parser')
        # print("==============================================================================================")
        # print(soup)

        # 게시글의 게시글번호 획득
        post_num = soup.select("#list-body > li:not(.bg-light) > div.wr-num.hidden-xs")
        link = []

        db_post_num = db_select("gezip")[0]
        bs_post_num = int(post_num[0].text)
        print("저장번호: " + str(db_post_num) + ", 획득번호: " + str(bs_post_num))
        if db_post_num < bs_post_num:
            print("Different.\n저장번호: " + str(db_post_num) + ", 획득번호: " + str(bs_post_num) + " - 마지막 게시글 번호와 다름")
            # 게시글의 링크 획득
            post_links = soup.select("#list-body > li:not(.bg-light) > div.wr-subject > a")
            for post_link in post_links:
                link.append(post_link['href'])
            nsfw_rand = []
            # 게시글 수 설정
            for _num in range(4, 5):
                nsfw_post = []
                # 첫게시글 접속
                post_one = s.post(link[_num], headers=header, data=login_info, cookies=cookies)
                soup = BeautifulSoup(post_one.text, 'html.parser')
                # print(soup)
                images = soup.select(
                    "#thema_wrapper > div.at-body > div > div > div > div.view-wrap > section > article > div.view-padding > div.view-content > * img")
                img_name = ""
                img_src = ""
                if images:

                    for image in images:
                        img_src = image.get("src")
                        print("이미지링크 : " + img_src)
                        # img_name = download_gezip(img_src)

                        img_name = img_src.split('/')[-1]
                        with open("./gezip/" + img_name, "wb") as file:
                            response = get(img_src, headers=header, data=login_info, cookies=cookies)
                            # response = get(url)
                            file.write(response.content)

                        print("이미지이름 : " + img_name)
                        if img_src:
                            nsfw_post.append(img_src)
                            nsfw_post.append(img_name)
                if img_src:
                    nsfw_rand.append(nsfw_post)
                    nsfw = random.choice(nsfw_rand)
                    print(nsfw_rand)
                    print("\n")
                    print(nsfw)
                    return nsfw
                else:
                    print("이미지 없음")
            db_update("gezip", str(bs_post_num))

            # config.set_gezip_post_num(post_num[0].text)
        else:
            print("Equal.\n저장번호: " + str(db_post_num) + ", 획득번호: " + str(bs_post_num) + " - 마지막 게시글 번호와 같음")
            return 0

def db_select(site):
    sql = "SELECT recent_post_num FROM `website` WHERE name='" + site + "'"
    conn = pymysql.connect(host="fuksoh.iptime.org", port=3307, user=config.db_id, password=config.db_pass, db="BBB", charset="utf8")
    curs = conn.cursor()
    curs.execute(sql)
    rows = curs.fetchone()
    conn.close()

    return rows


def db_update(site, post_num):
    sql = "UPDATE website SET recent_post_num = %s WHERE name='%s'" % (post_num, site)
    print(sql)
    conn = pymysql.connect(host="fuksoh.iptime.org", port=3307, user=config.db_id, password=config.db_pass, db="BBB", charset="utf8")
    curs = conn.cursor()
    curs.execute(sql)
    conn.commit()
    # print(db_select("gezip"))
    conn.close()


def download_gezip(url, file_name=None):
    header = {
        'Accept-Language': 'ko',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36',
        'referer': "http://gezip.net/"
    }
    cookies = {
        'PHPSESSID': 'ee1917788fec2eeb9c3663b67760fd4f',
        '2a0d2363701f23f8a75028924a3af643': 'MjE4LjE0OC4xOTYuMTcw;',
        'e1192aefb64683cc97abb83c71057733': 'c2V4eQ%3D%3D'
    }
    LOGIN_INFO = {
        'mb_id': config.gezip_id,
        'mb_password': config.gezip_pw,
        'url': '%2F'
    }

    if not file_name:
        file_name = url.split('/')[-1]
    with open("./gezip/" + file_name, "wb") as file:
        response = post(url, headers=header, data=LOGIN_INFO, cookies=cookies)
        # response = get(url)
        file.write(response.content)

    return file_name


# client = discord.Client()

# client = commands.Bot(command_prefix = '$')

# @client.event
# async def on_ready():
#     print("login")
#     print(client.user.name)
#     print(client.user.id)
#     print("-------------------------")
#     await client.change_presence(game=discord.Game(name='디스코드 봇', type='1'))
#     # client.loop.create_task(gezip_post())
#
#
# async def gezip_post():
#     while True:
#         dogdrip = gezip()
#         print("{} {} {}".format(dogdrip[0], dogdrip[1], dogdrip[2]))
#
#         # await client.send_message('573904343703748638', dogdrip[0])
#         dogdrip_channel = client.get_channel('573904343703748638')
#         await client.send_file(destination=dogdrip_channel, fp='./gezip/dogdrip.png', content="{} ||{} ||{}".format(dogdrip[0], dogdrip[1], dogdrip[2]))
#         await asyncio.sleep(60)
# client.run(config.TOKEN1)

gezip()
# gezib()