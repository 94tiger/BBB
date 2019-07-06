# -*- coding: utf-8 -*-

import discord
from discord.ext import commands
import os
import re
from pytz import timezone
from datetime import datetime
import asyncio
import random
import openpyxl
import time
import image
import game_stat
import gegle
import config

server_channels = {} # 서버 채널 캐시
client = discord.Client()

# client = commands.Bot(command_prefix = '$')

@client.event
async def on_ready():
    print("login")
    print(client.user.name)
    print(client.user.id)
    print("-------------------------")
    await client.change_presence(game=discord.Game(name='디스코드 봇', type='1'))
    client.loop.create_task(dogdrip_post())

@commands.has_role(name="전과자")
async def on_message(message):
    return

@client.event
async def on_message(message):
    if message.author.bot:
        return

    now = datetime.now(timezone('Asia/Seoul'))

    if message.server is not None:
        role_jungwaja = discord.utils.get(message.server.roles, name="전과자")
        role_nochat = discord.utils.get(message.server.roles, name="채팅금지(공지확인)")
        role_baebung = discord.utils.get(message.server.roles, name="배붕이")

    #건의함 기능 (채널 이용)
    """
    :var contact_channel : 건의함
    :var watch_channel : 건의함 확인용 채널   
    """
    contact_channel = client.get_channel('565011625325756416')
    watch_channel = client.get_channel('446335093254914050')
    if message.channel == contact_channel:
        embed_contactus = discord.Embed(title=str(message.author), description=message.content, color=0x1895a7)
        if message.attachments:
            embed_contactus.set_image(url=message.attachments[0]['proxy_url'])
        await client.send_message(watch_channel, embed=embed_contactus)
        await client.delete_message(message)

    # 배그 전적 확인
    if message.content.startswith("$전적"):
        stat_str = message.content.split(" ")
        pubgid = stat_str[1]
        pubgmode = stat_str[2]
        if pubgmode == "솔로":
            pubgmode_class = "solo modeItem"
        if pubgmode == "듀오":
            pubgmode_class = "duo modeItem"
        if pubgmode == "스쿼드":
            pubgmode_class = "squad modeItem"

        stat = game_stat.get_pubg_stat(pubgid, pubgmode_class)

        embed_stat = discord.Embed(color=0xdc6363)
        embed_stat.add_field(name="K/D", value=stat[0], inline=True)
        embed_stat.add_field(name="평균 딜량", value=stat[1], inline=True)
        embed_stat.add_field(name="게임 수", value=stat[2], inline=True)
        embed_stat.add_field(name="승률", value=stat[3], inline=True)
        embed_stat.set_thumbnail(url=stat[4])
        await client.send_message(message.channel, embed=embed_stat)

    if message.content.startswith("$배그"):
        stat_str = message.content.split(" ")
        pubgid = stat_str[1]
        pubgmode = stat_str[2]
        if pubgmode == "솔로":
            pubgmode_str = "solo"
        if pubgmode == "듀오":
            pubgmode_str = "duo"
        if pubgmode == "스쿼드":
            pubgmode_str = "squad"
        game_stat.get_pubg_stat_screenshot(pubgid, pubgmode_str)

        await client.send_file(message.channel, fp='./stat/' + pubgid + '_' + pubgmode_str + '.png' ,content="`" + pubgid + "`님의 __**" + pubgmode + "**__ 전적입니다.")

    if message.content.startswith("$롤"):
        stat_str = message.content.split(" ")
        lolid = stat_str[1]
        stat = game_stat.get_lol_stat(lolid)
        # stat = [랭크유무, 프로필이미지링크, 티어아이콘링크, 랭크타입, 현재티어, 점수, 승, 패, 승률]
        embed_stat = discord.Embed(color=0xdc6363, timestamp=now)
        embed_stat.set_author(name=lolid, url="https://www.op.gg/summoner/userName=" + lolid, icon_url=stat[1])
        embed_stat.set_footer(text="from OP.GG", icon_url="https://pbs.twimg.com/profile_images/928183232096432128/_rMzMIU4_400x400.jpg")
        # 대체 이미지 https://opgg-static.akamaized.net/images/site/about/img-logo-opgg.png
        embed_stat.set_thumbnail(url=stat[2])
        if stat[0] == True:
            embed_stat.add_field(name=stat[3] + " " + stat[4], value="**" + stat[5] + "** / `" + stat[6] + "` `"+ stat[7] + "` / `"+ stat[8] + "`")
        else:
            embed_stat.add_field(name="Unranked", value="랭크 전적이 존재하지 않는 유저입니다.")
        # embed_stat.add_field(name="Most 1", value="```\n트위스티드 페이트\t|3.54\t|50%\t|337게임```")
        await client.send_message(message.channel, content="`" + lolid + "`님의 전적", embed=embed_stat)

    if message.content.startswith("$념글"):
        gegle_str = message.content.split(" ")
        gallery_name = gegle_str[1]
        if gallery_name == "힛갤":
            gallery_str = "hit"
        if gallery_name == "이슈줌":
            gallery_str = "issuezoom"
        if gallery_name == "중갤":
            gallery_str = "aoegame"
        if gallery_name == "돌갤":
            gallery_str = "pebble"
        if gallery_name == "야갤":
            gallery_str = "baseball_new8"
        if gallery_name == "롤갤":
            gallery_str = "leagueoflegends2"
        gegl = gegle.get_gegle(gallery_str)
        gegl_value = ""
        for i in range(len(gegl)):
            gegl_value = gegl_value + "{}. [{} [{}]]({}) \n".format(i+1, gegl[i][0], gegl[i][1], gegl[i][2])
            # gegl_value = gegl_value + str(i+1) + ". [" + gegl[i][0] + " " + gegl[i][1] + "](" + gegl[i][2] + ") \n"
        embed_gegl = discord.Embed(color=0xdc6363)
        embed_gegl.add_field(name=gallery_name + " 개념글", value=gegl_value, inline=False)
        await client.send_message(message.channel, embed=embed_gegl)

    if message.content.startswith("$최신개드립"):
        dogdrip_channel = client.get_channel('573904343703748638')

        async for m in client.logs_from(dogdrip_channel, limit=1):
            print('dogdrip print Success')
        dogdrip = m.clean_content.split(" |?")
        dogdrip_value = "{} [{}]".format(dogdrip[1], dogdrip[2])

        embed_dogdrip = discord.Embed(title=dogdrip_value, url=dogdrip[0], color=0x1895a7)
        # if message.attachments:
        embed_dogdrip.set_image(url=m.attachments[0]['proxy_url'])
        await client.send_message(message.channel, embed=embed_dogdrip)

    if message.content.startswith("$개드립"):
        dogdrip = gegle.get_dogdrip()

        dogdrip_value = ""
        for i in range(len(dogdrip)):
            dogdrip_value = dogdrip_value + str(i + 1) + ". [" + dogdrip[i][0] + " " + dogdrip[i][1] + "](" + dogdrip[i][2] + ") \n"
        embed_dogdrip = discord.Embed(color=0xdc6363)
        embed_dogdrip.add_field(name="개드립", value=dogdrip_value, inline=False)

        await client.send_message(message.channel, embed=embed_dogdrip)

    if message.content.startswith('$명령어'):
        command_msg = "```md\n# 기본\n* $명령어 - 봇 명령어 안내\n* $주사위 [굴릴 주사위]\n# 선택 \n* $골라 [1 2 3 ...] - 1,2,3랜덤 선택\n* $뭐먹지 - 메뉴 랜덤 \n* $치킨뭐먹지 - 치킨 랜덤\n* $뭔겜할까 - 게임 랜덤 \n* $맵 - 맵 랜덤\n# 기능 \n* $전적 [배그아이디] [솔로|듀오|스쿼드] - 배그 전적 검색 (dak.gg 기준 / 갱신 x)\n* $배그 [배그아이디] [솔로|듀오|스쿼드] - 배그 전적 검색 (pubg.op.gg 기준 / 갱신 ok)\n* $롤 [롤아이디] - 롤 전적 검색 (op.gg 기준 / 갱신 x)\n# 커뮤니티\n* $념글 [힛갤|야갤|중갤|이슈줌] - 최신 개념글 목록\n* $개드립 - 최신 개드립 목록 \n# 서버 \n* $해제 - 지옥 탈출```"
        await client.send_message(message.author, command_msg)

    if message.content.startswith('$서버'):
        server_list = []
        for server in client.servers:
            server_list.append(server.name)
        await client.send_message(message.channel, "\n".join(server_list))

    if message.content.startswith('$주사위'):
        roll = message.content.split(" ")
        dice = random.randint(1, int(roll[1]))
        await client.send_message(message.channel, ":game_die: 나온 눈은 " + str(dice))

    if message.content.startswith('$골라'):
        choice = message.content.split(" ")
        choiceNum = random.randint(1, len(choice) - 1)
        choiceResult = choice[choiceNum]
        await client.send_message(message.channel,
                                  "`" + message.author.display_name + "`님의 선택은 __**" + choiceResult + "**__ 입니다.")

    if message.content.startswith('$뭐먹지'):
        # category = "중식, 일식, 분식, 치킨, 피자, 햄버거"
        food = "피자 햄버거 치킨 라면 백반 돈까스 제육 우동 김치찌개 된장찌개 순두부찌개 부대찌개 육개장 쫄면 콩국수 냉면 김밥 메밀소바 짜장면 짬뽕 볶음밥 짬뽕밥 오므라이스 잡채밥 삼겹살 곱창 족발 보쌈 찜닭 회 떡볶이 비빔밥 설렁탕 순대국 굶어"
        foodChoice = food.split(" ")
        foodNum = random.randint(0, len(foodChoice) - 1)
        foodResult = foodChoice[foodNum]
        await client.send_message(message.channel, foodResult)

    if message.content.startswith('$치킨뭐먹지'):
        # category = "중식, 일식, 분식, 치킨, 피자, 햄버거"
        chicken = "굽네-오리지널 굽네-고추바사삭 네네-스노윙 교촌-레드콤보 교촌-허니콤보 BBQ-황금올리브 BBQ-자메이카통다리 BHC-핫후라이드 BHC-뿌링클 또래오래-갈릭반핫양념반 또래오래-엔젤치킨 처갓집-슈프림양념치킨 처갓집-와락치킨 멕시카나-김치킨 멕시카나-치토스치킨"
        chickenChoice = chicken.split(" ")
        chickenNum = random.randint(0, len(chickenChoice) - 1)
        chickenResult = chickenChoice[chickenNum]
        await client.send_message(message.channel, chickenResult)

    if message.content.startswith('$뭔겜할까'):
        game = "배그 롤 하스 오버워치 메이플"
        gameChoice = game.split(" ")
        gameNum = random.randint(0, len(gameChoice) - 1)
        gameResult = gameChoice[gameNum]
        await client.send_message(message.channel, gameResult)

    if message.content.startswith('$맵'):
        map = "에란겔 미라마 사녹 비켄디 빠른참가"
        mapChoice = map.split(" ")
        mapNum = random.randint(0, len(mapChoice) - 1)
        mapResult = mapChoice[mapNum]
        await client.send_message(message.channel, mapResult)

    if message.content.startswith('$메모장쓰기'):
        file = open("디스코드봇메모장.txt", "w")
        file.write("안녕하세요")
        file.close()

    if message.content.startswith('$메모장읽기'):
        file = open("디스코드봇메모장.txt")
        await client.send_message(message.channel, file.read())
        file.close()

    #   $학습 A B
    if message.content.startswith('$학습'):
        file = openpyxl.load_workbook("기억.xlsx")
        sheet = file.active
        learn = message.content.split(" ")
        for i in range(1, 51):
            if sheet["A" + str(i)].value == "-" or sheet["A" + str(i)].value == learn[1]:
                sheet["A" + str(i)].value = learn[1]
                sheet["B" + str(i)].value = learn[2]
                await client.send_message(message.channel, "단어가 학습되었습니다.")
                break
        file.save("기억.xlsx")

    #   $기억 A     => B
    if message.content.startswith('$기억'):
        file = openpyxl.load_workbook("기억.xlsx")
        sheet = file.active
        memory = message.content.split(" ")
        for i in range(1, 51):
            if sheet["A" + str(i)].value == memory[1]:
                await client.send_message(message.channel, sheet["B" + str(i)].value)
                break

    if message.content.startswith('$확인'):
        await client.send_message(message.channel, str(now.month) + str(now.day) + str(now.hour) + str(now.minute))
        # await  client.send_message(message.channel, "<@" + message.author.id + ">")
        # if "502065016393039873" in [role.id for role in message.author.roles]:
        #     await client.send_message(message.channel, "전과 있음")
        # else:
        #     await client.send_message(message.channel, "전과 없음")
        # await client.send_message(message.channel, message.author.avatar_url)

    # 처벌
    bypass_list = ['415535047203094541']
    contents = message.content.split(" ")

    if message.server is None:
        return
    elif message.server.id == config.server:
        for word in contents:
            if "502065016393039873" in [role.id for role in message.author.roles]:
                out_d = now.day + 1
                out_h = now.hour
            else:
                if now.hour >= 12:
                    out_d = now.day + 1
                    out_h = now.hour - 12
                else:
                    out_d = now.day
                    out_h = now.hour + 12
            if "309912507257061388" in [role.id for role in message.author.roles]:
                split_name = message.author.display_name.split(" ")
                out_d_chk = split_name[1].split("일")
                if out_d_chk[0].isdigit():
                    out_d = int(out_d_chk[0]) + 1

                # if now.month in [1, 3, 5, 7, 8, 10, 12]:
                #     if int(out_d_chk[0]) > 31:
                #         out_d = 1
                # elif now.month in [4, 6, 9, 11]:
                #     if int(out_d_chk[0]) > 30:
                #         out_d = 1
                # elif now.month == 2:
                #     if int(out_d_chk[0]) > 28:
                #         out_d = 1

            if not message.author.id in bypass_list:
                if word in config.chat_filter_ilbe or word in config.chat_filter_megal:
                    if word in config.chat_filter_ilbe:
                        await client.send_message(message.channel, "삐빅, 일베충 검출")
                        await client.change_nickname(message.author, "일베충 " + str(out_d) + "일 " + str(out_h) + "시 " + str(
                            now.minute) + "분 해제")
                    if word in config.chat_filter_megal:
                        await client.send_message(message.message.channel, "삐빅, 메갈 검출")
                        await client.change_nickname(message.author, "메갈 " + str(out_d) + "일 " + str(out_h) + "시 " + str(
                            now.minute) + "분 해제")
                    try:
                        await client.remove_roles(message.author, role_baebung)
                        await asyncio.sleep(0.5)
                    except discord.Forbidden:
                        await client.send_message(message.channel, "권한이 없음")
                    try:
                        await client.add_roles(message.author, role_jungwaja)
                        await asyncio.sleep(0.5)
                    except discord.Forbidden:
                        await client.send_message(message.channel, "권한이 없음")
                    try:
                        await client.add_roles(message.author, role_nochat)
                        await asyncio.sleep(0.5)
                    except discord.Forbidden:
                        await client.send_message(message.channel, "권한이 없음")

        if message.content.startswith('$해제'):
            split_name = message.author.display_name.split(" ")
            out_d_chk = split_name[1].split("일")
            out_h_chk = split_name[2].split("시")
            out_m_chk = split_name[3].split("분")
            now_time = now.day * 1440 + now.hour * 60 + now.minute
            if out_m_chk[0].isdigit():
                out_time = int(out_d_chk[0]) * 1440 + int(out_h_chk[0]) * 60 + int(out_m_chk[0])
            else:
                out_time = int(out_d_chk[0]) * 1440 + int(out_h_chk[0]) * 60

            if out_time <= now_time:
                if out_m_chk[0].isdigit():
                    await client.send_message(message.channel,
                                              "나갈시간 : " + str(out_d_chk[0]) + "일 " + str(out_h_chk[0]) + "시 " + str(
                                                  out_m_chk[0]) + "분, 현재시간 : " + str(now.day) + "일 " + str(
                                                  now.hour) + "시 " + str(now.minute) + "분")
                else:
                    await client.send_message(message.channel, "나갈시간 : " + str(out_d_chk[0]) + "일 " + str(
                        out_h_chk[0]) + "시, 현재 시간 : " + str(now.day) + "일 " + str(now.hour) + "시 " + str(now.minute) + "분")
                await client.send_message(message.channel, "나갈시간 됐다")
                try:
                    await client.remove_roles(message.author, role_nochat)
                    await client.change_nickname(message.author, "")
                    await asyncio.sleep(0.5)
                except discord.Forbidden:
                    await client.send_message(message.author, "권한이 없음")
                try:
                    await client.add_roles(message.author, role_baebung)
                    await asyncio.sleep(0.5)
                except discord.Forbidden:
                    await client.send_message(message.channel, "권한이 없음")
            else:
                if out_m_chk[0].isdigit():
                    await client.send_message(message.channel,
                                              "나갈시간 : " + str(out_d_chk[0]) + "일 " + str(out_h_chk[0]) + "시 " + str(
                                                  out_m_chk[0]) + "분, 현재시간 : " + str(now.day) + "일 " + str(
                                                  now.hour) + "시 " + str(now.minute) + "분")
                else:
                    await client.send_message(message.channel, "나갈시간 : " + str(out_d_chk[0]) + "일 " + str(
                        out_h_chk[0]) + "시, 현재 시간 : " + str(now.day) + "일 " + str(now.hour) + "시 " + str(now.minute) + "분")
                await client.send_message(message.channel, "나갈시간 아직이다")

    # 신고함채널 설정
    # if message.content.startswith("$신고함채널설정"):
    #     contactus_channel = message.content.split(" ")
    #     contact_channel = contactus_channel[1]
    #
    # if message.server is None and message.author.id != '480847872074448906':
    #     await client.send_message(contact_channel, message.content)

    # 건의함 기능 (DM이용)
    # contact_channel = client.get_channel('446335093254914050')
    # if message.server is None and message.author.id != '480847872074448906':
    #     embed_contactus = discord.Embed(title="닉네임 : " + str(message.author), description=message.content,
    #                                     color=0x1895a7)
    #     if message.attachments:
    #         embed_contactus.set_image(url=message.attachments[0]['proxy_url'])
    #     await client.send_message(contact_channel, embed=embed_contactus)

def find_channel(server, refresh = False):
    """
    음성 이벤트를 기록할 채널을 찾아 반환.

    :param server: 채널을 찾을 서버.
    :param refresh: 이 서버의 채널 캐시를 새로 고칠지 여부.
    """
    if not refresh and server in server_channels:
        return server_channels[server]

    for channel in client.get_all_channels():
        if channel.server == server and channel.name == config.VOICE_LOG_CHANNEL:
            print("{}: 로그 채널 설정 완료".format(server))
            server_channels[server] = channel
            return channel

    return None

@client.event
async def on_voice_state_update(member_before, member_after):
    """
    서버에서 멤버의 음성 상태가 변경되면 호출됨.

    :param member_before: The state of the member before the change.
    멤버의 변화 전의 음성 상태
    :param member_after: The state of the member after the change.
    멤버의 변화 후의 음성 상태
    """
    server = member_after.server
    channel = find_channel(server)

    voice_channel_before = member_before.voice_channel
    voice_channel_after = member_after.voice_channel

    if voice_channel_before == voice_channel_after:
        # 변경되지 않음
        return

    if voice_channel_before == None:
        # 멤버가 상태 변경 전에 음성 채널에 접속해 있지 않았음
        msg = "{} 님이 _{}_ 채널에 접속하였습니다.".format(member_after.mention, voice_channel_after.id)
    else:
        # 멤버가 상태 변경 전에 음성 채널에 접속해 있었음
        if voice_channel_after == None:
            # 멤버가 상태 변경 후에 음성 채널에 접속해 있지 않음
            msg = "{} 님이 _{}_ 채널을 나갔습니다.".format(member_after.mention, voice_channel_before.id)
        else:
            # 멤버가 상태 변경 후에 계속해서 음성 채널에 접속해 있음
            msg = "{} 님이 _{}_ 채널에서 _{}_ 채널로 옮겼습니다.".format(member_after.mention, voice_channel_before.id, voice_channel_after.id)

    # 채널에 음성 이벤트를 기록
    try:
        await client.send_message(channel, msg)
    except:
        # 채널에 메시지를 보낼 수 없습니다. 강제로 채널 캐시를 새로 고친 후 다시 시도하십시오.
        channel = find_channel(server, refresh = True)
        if channel == None:
            # 채널을 찾을 수 없습니다.
            print("Error: {}서버에 #{} 채널이 존재하지 않습니다.".format(server, config.VOICE_LOG_CHANNEL))
        else:
            # 메시지를 다시 보내십시오
            try:
                await client.send_message(channel, msg)
            except discord.DiscordException as exception:
                # 예외를 출력함
                print("Error: {} 서버의 #{} 채널에 보낼 수 있는 메시지가 없습니다. 예외: {}".format(server, config.VOICE_LOG_CHANNEL, exception))

async def dogdrip_post():
    while True:
        dogdrip = gegle.get_dogdrip_post()
        print("{} {} {}".format(dogdrip[0], dogdrip[1], dogdrip[2]))

        # await client.send_message('573904343703748638', dogdrip[0])
        dogdrip_channel = client.get_channel('573904343703748638')
        await client.send_file(destination=dogdrip_channel, fp='./result/dogdrip.png', content="{} |?{} |?{}".format(dogdrip[0], dogdrip[1], dogdrip[2]))
        await asyncio.sleep(600)


# print('{}: {}'.format(author, content))

# async def on_voice_state_update(before, after):
#     if not before.voice_channel and after.voice_channel:
#         print(after.display_name + " joined voice channel: " + after.voice_channel.name)
#     elif before.voice_channel and after.voice_channel and before.voice_channel != after.voice_channel:
#         print(after.display_name + " changed voice channel from " + before.voice_channel.name + " to " + after.voice_channel.name)
#     elif before.voice_channel and not after.voice_channel:
#         print(after.display_name + " left voice channel: " + before.voice_channel.name)

# 이미지 검색
# if message.content.startswith('$이미지'):
#   img = message.content.split(" ")
#   imgsrc = image.get_image(img[1])
#   print(imgsrc)
#    await client.send_message(message.channel, imgsrc)

# @client.event
# async def on_message_delete(message):
#     author = message.author
#     content = message.content
#     channel = message.channel
#     await client.send_message(channel, '@{}가 #{} 채널에서 메시지를 지웠습니다\n{}'.format(author, channel, content))

# 특정 인물이 채팅 칠 때마다 특정 채팅 치기
# if author.id == '':
#    await client.send_message(message.channel, "")

client.run(config.TOKEN)