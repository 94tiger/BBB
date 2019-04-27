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
import image
import bg
import gegle
import config

client = discord.Client()


# client = commands.Bot(command_prefix = '$')

@client.event
async def on_ready():
    print("login")
    print(client.user.name)
    print(client.user.id)
    print("-------------------------")
    await client.change_presence(game=discord.Game(name='디스코드 봇', type='1'))


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

        stat = bg.get_stat(pubgid, pubgmode_class)

        embed_stat = discord.Embed(color=0xdc6363)
        embed_stat.add_field(name="K/D", value=stat[0], inline=True)
        embed_stat.add_field(name="평균 딜량", value=stat[1], inline=True)
        embed_stat.add_field(name="게임 수", value=stat[2], inline=True)
        embed_stat.add_field(name="승률", value=stat[3], inline=True)
        embed_stat.set_thumbnail(url=stat[4])
        await client.send_message(message.channel, embed=embed_stat)

        # for value in stat:
        # await client.send_message(message.channel, stat)

    if message.content.startswith("$념글"):
        gegle_str = message.content.split(" ")
        gallery_name = gegle_str[1]
        if gallery_name == "야갤":
            gallery_str = "baseball_new7"
            gegl = gegle.get_gegle(gallery_str)
        if gallery_name == "힛갤":
            gallery_str = "hit"
            gegl = gegle.get_gegle(gallery_str)
        if gallery_name == "중갤":
            gallery_str = "aoegame"
            gegl = gegle.get_mgegle(gallery_str)
        if gallery_name == "이슈줌":
            gallery_str = "issuezoom"
            gegl = gegle.get_gegle(gallery_str)
        # gegl = gegle.get_gegle(gallery_str)
        gegl_value = ""
        for i in range(len(gegl)):
            gegl_value = gegl_value + str(i+1) + ". [" + gegl[i][0] + " " + gegl[i][1] + "](" + gegl[i][2] + ") \n"
        embed_gegl = discord.Embed(color=0xdc6363)
        embed_gegl.add_field(name=gallery_name + " 개념글", value=gegl_value, inline=False)
        await client.send_message(message.channel, embed=embed_gegl)

    if message.content.startswith("$개드립"):
        dogdrip = gegle.get_dogdrip()

        dogdrip_value = ""
        for i in range(len(dogdrip)):
            dogdrip_value = dogdrip_value + str(i + 1) + ". [" + dogdrip[i][0] + " " + dogdrip[i][1] + "](" + dogdrip[i][2] + ") \n"
        embed_dogdrip = discord.Embed(color=0xdc6363)
        embed_dogdrip.add_field(name="개드립", value=dogdrip_value, inline=False)

        await client.send_message(message.channel, embed=embed_dogdrip)

    if message.content.startswith('$명령어'):
        command_msg = "```md\n# 기본\n* $명령어 - 봇 명령어 안내\n* $주사위 [굴릴 주사위]\n# 선택 \n* $골라 [1 2 3 ...] - 1,2,3랜덤 선택\n* $뭐먹지 - 메뉴 랜덤 \n* $치킨뭐먹지 - 치킨 랜덤\n* $뭔겜할까 - 게임 랜덤 \n* $맵 - 맵 랜덤\n# 기능 \n* $전적 [배그아이디] [솔로|듀오|스쿼드] - 배그 전적 검색\n# 커뮤니티\n* $념글 [힛갤|야갤|중갤] - 최신 개념글 목록\n* $개드립 - 최신 개드립 목록 \n# 서버 \n* $해제 - 지옥 탈출```"
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
    '''
    if "이기야" in message.content:
        memid = message.content.split(" ")
        file = openpyxl.load_workbook("경고.xlsx")
        member = discord.utils.get(client.get_all_members(), id="335014396088680453")
        sheet = file.active

        for i in range(1, 31):
            if str(sheet["A" + str(i)].value) == str(message.author.id):
                sheet["B" + str(i)].value = int(sheet["B" + str(i)].value) + 1

                if int(sheet["B" + str(i)].value) == 3:
                    await client.ban(member, 1)
                    await client.change_nickname(member, now.tm_mday + "일 " + now.tm_hour + "시 " + now.tm_min + "분 해제")

                break
            if str(sheet["A" + str(i)].value) == "-":
                sheet["A" + str(i)].value = str(message.author.id)
                sheet["B" + str(i)].value = 1
                break
        file.save("경고.xlsx")
        await client.send_message(message.channel, "경고.")
        await client.change_nickname(member, str(now.tm_mday) + "일 " + str(now.tm_hour) + "시 " + str(now.tm_min) + "분 해제")
        await client.add_roles(member, role_jungwaja)
        await client.add_roles(member, role_nochat)
    '''
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