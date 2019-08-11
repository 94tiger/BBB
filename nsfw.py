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
import os

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
    nsfw = []
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

        count = 0

        # DB의 게시글 번호와 크롤링한 게시글 번호 비교
        if db_post_num < bs_post_num:
            print("Different. 저장번호: " + str(db_post_num) + ", 획득번호: " + str(bs_post_num) + " - 마지막 게시글 번호와 다름")
            # 게시글의 링크 획득
            post_links = soup.select("#list-body > li:not(.bg-light) > div.wr-subject > a")
            for post_link in post_links:
                link.append(post_link['href'])

            # 게시글 수 설정

            for _num in range(1):
                # 첫게시글 접속
                post_one = s.post(link[_num], headers=header, data=login_info, cookies=cookies)
                soup = BeautifulSoup(post_one.text, 'html.parser')
                # print(soup)

                images = soup.select(
                    "#thema_wrapper > * div.view-padding:not(.view-icon) > *  img")

                nsfw_post = []
                # if images:

                nsfw_post_images = []
                for image in images:

                    img_src = image.get("src")
                    img_name = img_src.split('/')[-1]

                    with open("./gezip/" + img_name, "wb") as file:
                        response = get(img_src, headers=header, data=login_info, cookies=cookies)
                        # response = get(url)
                        file.write(response.content)

                    # print("이미지이름 : " + img_name)
                    if img_src:
                        nsfw_post_images.append(img_name)
                        nsfw_rand = random.choice(nsfw_post_images)
                nsfw_file_limit = False
                try:
                    n = os.path.getsize("./gezip/"+nsfw_rand)
                    if (n / 1024) < 100:
                        nsfw_file_limit = False
                    else:
                        nsfw_file_limit = True
                    print("파일 크기 : ", n / 1024, "KB")  # 킬로바이트 단위로
                except os.error:
                    print("파일이 없거나 에러입니다.")
                except UnboundLocalError:
                    print("nsfw_rand가 지정되지 않음")
                count = count + 1
                # 게시글 번호 저장
                nsfw_post.append(bs_post_num - _num)

                # 게시글 링크 저장
                nsfw_post.append(link[_num])

                # 게시글 제목 저장
                post_names = soup.select("#thema_wrapper * > div.view-wrap > section > article > h1")
                for post_name in post_names:
                    nsfw_post.append(post_name['content'])

                gfycats = soup.select("#thema_wrapper * > div.view-content > embed")
                insta = soup.select("blockquote.instagram-media")
                if images:
                    # 게시글 파일명 저장
                    nsfw_post.append(nsfw_rand)
                    nsfw_type = "image"
                    nsfw_post.append(nsfw_type)
                else:
                    print("이미지없음")
                    if gfycats:
                        gfycat_rand = []
                        for gfycat in gfycats:
                            gfycat_rand.append(gfycat['src'])
                        nsfw_post.append(random.choice(gfycat_rand))
                        nsfw_type = "gfycats"
                        nsfw_post.append(nsfw_type)
                        nsfw_file_limit = True
                    if insta:
                        nsfw_post.append(insta[0]['data-instgrm-permalink'])
                        nsfw_type = "instagram"
                        nsfw_post.append(nsfw_type)
                        nsfw_file_limit = True


                nsfw_post.append(nsfw_file_limit)
                # DB에 게시글번호 저장
                db_update("gezip", str(bs_post_num))

                print(nsfw_post)
                nsfw.append(nsfw_post)
            print(nsfw)

            # config.set_gezip_post_num(post_num[0].text)
        else:
            print("Equal.\n저장번호: " + str(db_post_num) + ", 획득번호: " + str(bs_post_num) + " - 마지막 게시글 번호와 같음")
            nsfw_post = [0, 0, 0, 0, 0, 0]
            nsfw.append(nsfw_post)
        nsfw.insert(0, count)

        '''
        nsfw_post = [게시글번호, 게시글URL, 게시글제목, 파일이름, 파일형식, 파일크기제한]
        nsfw = [게시글수, [nsfw_post], [nsfw_post]]
        '''
        return nsfw


def manpeace():
    nsfw = []
    login_page = "http://manpeace.net/bbs/login.php?url=http://manpeace.net/"
    first_page = "http://manpeace.net/"
    second_page = "http://manpeace.net/bbs/board.php?bo_table=ggolit"
    third_page = "http://manpeace.net/bbs/board.php?bo_table=jap"

    # 로그인할 유저정보를 넣어주자 (모두 문자열)
    header = {
        'Accept-Language': 'ko',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36',
        'referer': login_page
    }
    cookies = {
        'PHPSESSID': '9gjugqcs47s5c3ovs6t1kvl5k3',
        '_ga': 'GA1.2.1956966126.1564925351',
        '_gid': 'GA1.2.2008563687.1564925351',
        '2a0d2363701f23f8a75028924a3af643': 'MjE4LjE0OC4xOTYuMTcw',
        'e1192aefb64683cc97abb83c71057733': 'amFnZQ%3D%3D'
    }
    login_info = {
        'mb_id': config.gezip_id,
        'mb_password': config.gezip_pw,
        'url': 'http%3A%2F%2Fmanpeace.net%2F'
    }
    # LOGIN_INFO = {**LOGIN_INFO, **{''}}

    # Session 생성, with 구문 안에서 유지
    with requests.Session() as s:
        # HTTP POST request: 로그인을 위해 POST url와 함께 전송될 data를 넣어주자.
        login = s.post(login_page, headers=header, data=login_info, cookies=cookies)
        print("서버 상태 : " + str(login.status_code))
        # 여기서부터는 로그인 된 세션이 유지됨 (s.get()으로 다른 페이지로 이동해도 됨)
        # 찰카닥 게시판 접속
        # soup = BeautifulSoup(login.text, 'html.parser')
        # print(soup)
        # print("==============================================================================================")
        html = s.post(second_page, headers=header, data=login_info, cookies=cookies)
        soup = BeautifulSoup(html.text, 'html.parser')
        print(soup)

        # # 게시글의 게시글번호 획득
        # post_num = soup.select("#list-body > li:not(.bg-light) > div.wr-num.hidden-xs")
        #
        # link = []
        #
        # db_post_num = db_select("gezip")[0]
        # bs_post_num = int(post_num[0].text)

        # if db_post_num < bs_post_num:
        #         #     print("Different. 저장번호: " + str(db_post_num) + ", 획득번호: " + str(bs_post_num) + " - 마지막 게시글 번호와 다름")
        #         #     # 게시글의 링크 획득
        #         #     post_links = soup.select("#list-body > li:not(.bg-light) > div.wr-subject > a")
        #         #     for post_link in post_links:
        #         #         link.append(post_link['href'])
        #         #
        #         #     # 게시글 수 설정
        #         #     for _num in range(1):
        #         #         # 첫게시글 접속
        #         #         post_one = s.post(link[_num], headers=header, data=login_info, cookies=cookies)
        #         #         soup = BeautifulSoup(post_one.text, 'html.parser')
        #         #         # print(soup)
        #         #
        #         #         images = soup.select(
        #         #             "#thema_wrapper > * div.view-padding:not(.view-icon) > *  img")
        #         #         img_src = ""
        #         #         nsfw_post = []
        #         #         # if images:
        #         #
        #         #         nsfw_post_images = []
        #         #         for image in images:
        #         #
        #         #             img_src = image.get("src")
        #         #             img_name = img_src.split('/')[-1]
        #         #             with open("./gezip/" + img_name, "wb") as file:
        #         #                 response = get(img_src, headers=header, data=login_info, cookies=cookies)
        #         #                 # response = get(url)
        #         #                 file.write(response.content)
        #         #
        #         #             # print("이미지이름 : " + img_name)
        #         #             if img_src:
        #         #                 nsfw_post_images.append(img_name)
        #         #                 nsfw_rand = random.choice(nsfw_post_images)
        #         #         # 게시글 번호 저장
        #         #         nsfw_post.append(bs_post_num - _num)
        #         #
        #         #         # 게시글 링크 저장
        #         #         nsfw_post.append(link[_num])
        #         #
        #         #         # 게시글 제목 저장
        #         #         post_names = soup.select("#thema_wrapper * > div.view-wrap > section > article > h1")
        #         #         for post_name in post_names:
        #         #             nsfw_post.append(post_name['content'])
        #         #
        #         #         gfycats = soup.select("#thema_wrapper * > div.view-content > embed")
        #         #         if images:
        #         #             # 게시글 파일명 저장
        #         #             nsfw_post.append(nsfw_rand)
        #         #             nsfw_type = 0
        #         #             nsfw_post.append(nsfw_type)
        #         #         else:
        #         #             print("이미지없음")
        #         #             if gfycats:
        #         #                 gfycat_rand = []
        #         #                 for gfycat in gfycats:
        #         #                     gfycat_rand.append(gfycat['src'])
        #         #                 nsfw_post.append(random.choice(gfycat_rand))
        #         #                 nsfw_type = 1
        #         #                 nsfw_post.append(nsfw_type)
        #         #
        #         #         # DB에 게시글번호 저장
        #         #         db_update("gezip", str(bs_post_num))
        #         #
        #         #         # else:
        #         #         #     print("이미지 없음")
        #         #         print(nsfw_post)
        #         #         nsfw.append(nsfw_post)
        #         #     print(nsfw)
        #         #
        #         #     # config.set_gezip_post_num(post_num[0].text)
        #         # else:
        #         #     print("Equal.\n저장번호: " + str(db_post_num) + ", 획득번호: " + str(bs_post_num) + " - 마지막 게시글 번호와 같음")
        #         #     nsfw_post = [0, 0, 0, 0, 0]
        #         #     nsfw.append(nsfw_post)
        #         #
        # return nsfw


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
    conn = pymysql.connect(host="fuksoh.iptime.org", port=3307, user=config.db_id, password=config.db_pass, db="BBB",
                           charset="utf8")
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

# gezip()
# manpeace()
'''
아래 부터 디스코드 관련 코드
'''


client = discord.Client()
prefix = "$"


@client.event
async def on_ready():
    print("login")
    print(client.user.name)
    print(client.user.id)
    print("-------------------------")
    await client.change_presence(game=discord.Game(name='디스코드 봇', type='1'))
    client.loop.create_task(gezip_post())


@client.event
async def on_message(message):
    img_hosting_channel = client.get_channel('607136999035502592')
    nsfw_sexy_channel = client.get_channel('607138047015780352')

    if message.content.startswith(prefix + "은꼴"):
        if message.channel == nsfw_sexy_channel:
            return
        img_hosting_channel = client.get_channel('607136999035502592')
        nsfw_sexy_channel = client.get_channel('607138047015780352')

        gezip = []
        async for m in client.logs_from(img_hosting_channel, limit=30):
            gezip.append(m)
        nsfw_rand = random.randint(0, 12)
        m = gezip[nsfw_rand]
        _gezip = m.clean_content.split(" |?")
        if _gezip[0] == "image":
            embed_gezip = discord.Embed(title=_gezip[0], url=m.attachments[0]['proxy_url'], color=0x1895a7)
            embed_gezip.set_image(url=m.attachments[0]['proxy_url'])
            await client.send_message(nsfw_sexy_channel, embed=embed_gezip)
        elif _gezip[2] == "gfycats" or _gezip[2] == "instagram":
            await client.send_message(nsfw_sexy_channel, _gezip[0] + "\n" + _gezip[1])

    # #이미지-호스팅 채널에 올라온 글 #은꼴봇 채널로 보내기
    if message.channel == img_hosting_channel:
        async for m in client.logs_from(img_hosting_channel, limit=1):
            print('호스팅 된 이미지 확인')
        _gezip = m.clean_content.split(" |?")

        # embed_dogdrip = discord.Embed(title=_gezip[1], url=_gezip[0], color=0x1895a7)
        print(_gezip)
        if _gezip[0] == "image":
            embed_gezip = discord.Embed(title=_gezip[0], url=m.attachments[0]['proxy_url'], color=0x1895a7)
            embed_gezip.set_image(url=m.attachments[0]['proxy_url'])
            await client.send_message(nsfw_sexy_channel, embed=embed_gezip)
        elif _gezip[2] == "gfycats" or _gezip[2] == "instagram":
            await client.send_message(nsfw_sexy_channel, _gezip[0] + "\n" + _gezip[1])


async def gezip_post():
    while True:
        _gezip = gezip()
        gezip_channel = client.get_channel('607136999035502592')

        for i in range(1, _gezip[0]+1):
            if _gezip[i][5] == True:
                if _gezip[i][4] == "image":
                    try:
                        await client.send_file(destination=gezip_channel, fp='./gezip/' + str(_gezip[i][3]),
                                               content="{} |?{} |?{}".format(_gezip[i][2], _gezip[i][3], _gezip[i][4]))
                        print("파일 전송 성공")
                    except discord.errors.HTTPException:
                        print("파일 전송 실패 - 파일이 8메가 이상입니다.")
                if _gezip[i][4] == "gfycats":
                    await client.send_message(destination=gezip_channel,
                                              content="{} |?{} |?{}".format(_gezip[i][2], _gezip[i][3],
                                                                            _gezip[i][4]))
                if _gezip[i][4] == "instagram":
                    await client.send_message(destination=gezip_channel,
                                              content="{} |?{} |?{}".format(_gezip[i][2], _gezip[i][3],
                                                                            _gezip[i][4]))
            else:
                print("파일 크기가 100KB미만 입니다.")

        await asyncio.sleep(30)


client.run(config.TOKEN1)

# gezip()