import discord
from discord.ext import commands
import os
from pytz import timezone
from datetime import datetime
import asyncio
import random
import openpyxl
import image
import bg

client = discord.Client()
#client = commands.Bot(command_prefix = '$')

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

    author = message.author
    content = message.content

    role_jungwaja = discord.utils.get(message.server.roles, name="전과자")
    role_nochat = discord.utils.get(message.server.roles, name="채팅금지(공지확인)")
    role_baebung = discord.utils.get(message.server.roles, name="배붕이")

    # print('{}: {}'.format(author, content))

    # if message.content.startswith("$신고함채널설정"):
    #     contactus_channel = message.content.split(" ")
    #     contact_channel = contactus_channel[1]
    #
    # if message.server is None and message.author.id != '480847872074448906':
    #     await client.send_message(contact_channel, message.content)

    # 건의함 기능
    contact_channel = client.get_channel('446335093254914050')
    if message.server is None and message.author.id != '480847872074448906':
        embed_contactus = discord.Embed(title="닉네임 : " + str(message.author), description= message.content, color=0x1895a7)
        if message.attachments:
            embed_contactus.set_image(url=message.attachments[0]['proxy_url'])
        await client.send_message(contact_channel, embed=embed_contactus)

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

    if message.content.startswith('$명령어'):
        command_msg = "```css\n$명령어 - 봇 명령어 안내\n$주사위 [굴릴 주사위]\n$골라 [1 2 3 ...] - 1,2,3랜덤 선택 \n$뭐먹지 - 메뉴 랜덤 \n$뭔겜할까 - 게임 랜덤 \n$맵 - 맵 랜덤\n$이미지 [검색어]  - 이미지 검색 by NAVER ```"
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
        await client.send_message(message.channel, "`"+ message.author.display_name + "`님의 선택은 __**" + choiceResult + "**__ 입니다.")

    if message.content.startswith('$뭐먹지'):
        #category = "중식, 일식, 분식, 치킨, 피자, 햄버거"
        food = "짱깨 피자 햄버거 치킨 라면 굶기"
        foodChoice = food.split(" ")
        foodNum = random.randint(0, len(foodChoice)-1)
        foodResult = foodChoice[foodNum]
        await client.send_message(message.channel, foodResult)

    if message.content.startswith('$뭔겜할까'):
        game = "배그 롤 하스 오버워치 메이플"
        gameChoice = game.split(" ")
        gameNum = random.randint(0, len(gameChoice)-1)
        gameResult = gameChoice[gameNum]
        await client.send_message(message.channel, gameResult)

    if message.content.startswith('$맵'):
        map = "에란겔 미라마 사녹 비켄디"
        mapChoice = map.split(" ")
        mapNum = random.randint(0, len(mapChoice)-1)
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
        #await client.send_message(message.channel, message.author.avatar_url)

    #await client.send_message(message.channel, str(role_baebung) + " : " + str(role_baebung.id) + "\n" + str(role_jungwaja) + " : " + str(role_jungwaja.id) + "\n" + str(role_nochat) + " : " + str(role_nochat.id))

    #if message.content.startswith('$이미지'):
    #   img = message.content.split(" ")
    #   imgsrc = image.get_image(img[1])
    #   print(imgsrc)
    #    await client.send_message(message.channel, imgsrc)


    #처벌
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
    # 일베용어 채팅필터
    chat_filter_ilbe = ["고무통", "고무현", "까보전", "김머중", "노무", "노무추", "노무노무", "노미넴", "노시계", "노알라", "노짱", "다이쥬", "두부외상", "무현",
                        "ㅁㅈㅎ", "민주화", "문죄인", "문재앙", "라디언", "슨상", "슨상님", "슨탄절", "운지", "이기야", "익이", "익이야", "일게이", "좌빨", "쩔뚜기",
                        "쩔뚝이", "통구이", "핵슨상", "핵펭귄", "홍오쉐리", "盧", "MC무현"]
    chat_filter_megal = ["소추", "6.9센치"]
    bypass_list = ['415535047203094541']
    contents = message.content.split(" ")

    #if client.servers == 291849424953409536:
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
            split_name = author.display_name.split(" ")
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

        if not author.id in bypass_list:
            if word in chat_filter_ilbe or word in chat_filter_megal:
                if word in chat_filter_ilbe:
                    await client.send_message(message.channel, "삐빅, 일베충 검출")
                    await client.change_nickname(author, "일베충 " + str(out_d) + "일 " + str(out_h) + "시 " + str(now.minute) + "분 해제")
                if word in chat_filter_megal:
                    await client.send_message(message.channel, "삐빅, 메갈 검출")
                    await client.change_nickname(author, "메갈 " + str(out_d) + "일 " + str(out_h) + "시 " + str(now.minute) + "분 해제")
                try:
                    await client.remove_roles(author, role_baebung)
                    await asyncio.sleep(0.5)
                except discord.Forbidden:
                    await client.send_message(message.channel, "권한이 없음")
                try:
                    await client.add_roles(author, role_jungwaja)
                    await asyncio.sleep(0.5)
                except discord.Forbidden:
                    await client.send_message(message.channel, "권한이 없음")
                try:
                    await client.add_roles(author, role_nochat)
                    await asyncio.sleep(0.5)
                except discord.Forbidden:
                    await client.send_message(message.channel, "권한이 없음")

    if message.content.startswith('$해제'):
        split_name = author.display_name.split(" ")
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
                await client.send_message(message.channel, "나갈시간 : " + str(out_d_chk[0]) + "일 " + str(out_h_chk[0]) + "시 " + str(out_m_chk[0]) + "분, 현재시간 : " + str(now.day) + "일 " + str(now.hour) + "시 " + str(now.minute) + "분")
            else:
                await client.send_message(message.channel, "나갈시간 : " + str(out_d_chk[0]) + "일 " + str(out_h_chk[0]) + "시, 현재 시간 : " + str(now.day) + "일 " + str(now.hour) + "시 " + str(now.minute) + "분")
            await client.send_message(message.channel, "나갈시간 됐다")
            try:
                await client.remove_roles(author, role_nochat)
                await client.change_nickname(author, "")
                await asyncio.sleep(0.5)
            except discord.Forbidden:
                await client.send_message(author, "권한이 없음")
            try:
                await client.add_roles(author, role_baebung)
                await asyncio.sleep(0.5)
            except discord.Forbidden:
                await client.send_message(message.channel, "권한이 없음")
        else:
            if out_m_chk[0].isdigit():
                await client.send_message(message.channel, "나갈시간 : " + str(out_d_chk[0]) + "일 " + str(out_h_chk[0]) + "시 " + str(out_m_chk[0]) + "분, 현재시간 : " + str(now.day) + "일 " + str(now.hour) + "시 " + str(now.minute) + "분")
            else:
                await client.send_message(message.channel, "나갈시간 : " + str(out_d_chk[0]) + "일 " + str(out_h_chk[0]) + "시, 현재 시간 : " + str(now.day) + "일 " + str(now.hour) + "시 " + str(now.minute) + "분")
            await client.send_message(message.channel, "나갈시간 아직이다")

'''
    if "test" in message.content:
        if author.id != 415535047203094541:

            await client.change_nickname(author, str(now.tm_mday) + "일 " + str(now.tm_hour) + "시 " + str(now.tm_min) + "분 해제")
            try:
                await client.remove_roles(author, role_baebung)
                await asyncio.sleep(1)
            except discord.Forbidden:
                await client.send_message(author, "권한이 없음")
            try:
                await client.add_roles(author, role_jungwaja)
                await asyncio.sleep(1)
            except discord.Forbidden:
                await client.send_message(author, "권한이 없음")
            try:
                await client.add_roles(author, role_nochat)
                await asyncio.sleep(1)
                await client.send_message(message.channel, "삐빅, 일베충 검출")
            except discord.Forbidden:
                await client.send_message(author, "권한이 없음")
'''

'''
@client.event
async def on_message_delete(message):
    author = message.author
    content = message.content
    channel = message.channel
    await client.send_message(channel, '@{}가 #{} 채널에서 메시지를 지웠습니다\n{}'.format(author, channel, content))
'''
# 특정 인물이 채팅 칠 때마다 특정 채팅 치기
# if author.id == '':
#    await client.send_message(message.channel, "")

# f = open('./TOKEN.txt', 'r')
# TOKEN = f.read()
# f.close()

access_token = os.inviron("BOT_TOKEN")
client.run(access_token)