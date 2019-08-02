import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re

pattern = re.compile((r'\s+'))

def get_html(url):
    headers = {'Accept-Language': 'ko'}
    _html = ""
    resp = requests.get(url, headers = headers)
    # status_code가 정상이면
    if resp.status_code == 200:
        _html = resp.text
    return _html

def get_pubg_stat(pubgid, pubgmode, tpp):
    """
    :param pubgid:
    :param pubgmode:
    :return: stat [stat_KD, stat_AVD, stat_NoG, stat_PoV, avatar_img] [K/D, 평균딜, 게임수,
    """
    URL = ("https://dak.gg/profile/" + pubgid)
    html = get_html(URL)
    soup = BeautifulSoup(html, 'html.parser')
    avatar = soup.find('div', {'class' : 'userInfo'})

    try:
        avatar = avatar.find('img')
        id_exist = True
    except AttributeError:
        id_exist = False
        stat = [id_exist]
        return stat

    avatar = avatar.get('src')
    if avatar == "/images/icons/avatars/kakao-dakgg.jpg":
        avatar = "https://dak.gg/images/icons/avatars/kakao-dakgg.jpg"
    avatar_img = str(avatar)

    ielement = soup.find('section', {'class': pubgmode})
    if tpp == True:
        ielement = ielement.find('div', {'class': 'mode-section tpp'})
    else:
        ielement = ielement.find('div', {'class': 'mode-section fpp'})

    try:
        stat_KD = ielement.find('div', {'class': 'kd stats-item stats-top-graph'})
        stat_KD = stat_KD.find('p', {'class':'value'})
        stat_KD = str(stat_KD)[str(stat_KD).find('ue">') + 4:str(stat_KD).find('</p>')]
        stat_KD = re.sub(pattern, '', stat_KD)

        stat_AVD = ielement.find('div', {'class': 'deals stats-item stats-top-graph'})
        stat_AVD = stat_AVD.find('p', {'class': 'value'})
        stat_AVD = str(stat_AVD)[str(stat_AVD).find('ue">') + 4:str(stat_AVD).find('</p>')]
        stat_AVD = re.sub(pattern, '', stat_AVD)

        stat_PoV = ielement.find('div', {'class': 'winratio stats-item stats-top-graph'})
        stat_PoV= stat_PoV.find('p', {'class': 'value'})
        stat_PoV = str(stat_PoV)[str(stat_PoV).find('ue">') + 4:str(stat_PoV).find('</p>')]
        stat_PoV = re.sub(pattern, '', stat_PoV)

        stat_NoG = ielement.find('div', {'class': 'games stats-item stats-top-graph'})
        stat_NoG = stat_NoG.find('p', {'class': 'value'})
        stat_NoG = str(stat_NoG)[str(stat_NoG).find('ue">') + 4:str(stat_NoG).find('</p>')]
        stat_NoG = re.sub(pattern, '', stat_NoG)

        stat_exist = True
        # stat_exist =    stat_list = "K/D : `" + stat_KD + "` 평딜 : ` " + stat_AVD + "` 게임수 : ` " + stat_NoG + "` 승률 : `" + stat_PoV + "`\n" + avatar_img
        stat = [id_exist, stat_exist, stat_KD, stat_AVD, stat_NoG, stat_PoV, avatar_img]
    except AttributeError:
        stat_exist = False
        stat = [id_exist, stat_exist]

    # if int(stat_AVD) < 100:
    #     stat = ""
    # elif int(stat_AVD) < 150:
    #     stat = ""
    # elif int(stat_AVD) < 250:
    #     stat = ""
    # elif int(stat_AVD) < 350:
    #     stat = ""
    # elif int(stat_AVD) < 600:
    #     stat = ""
    # else:
    #     stat = "핵"
    return stat

def get_pubg_stat_screenshot(pubgid, pubgmode, tpp):
    URL = "https://pubg.op.gg/user/"

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
    driver.set_window_size(1200, 800)
    # driver.implicitly_wait(0.5)

    data_id = "pc-2018-03|fpp|"

    # pubg.op.gg 접속
    driver.implicitly_wait(0.5)
    driver.get(URL + pubgid)
    print("Successful Connection to https://pubg.op.gg")

    driver.find_element_by_xpath("//button[@id='renewBtn']").click()
    print("Refresh Success")
    driver.implicitly_wait(2)

    data_id = driver.find_element_by_xpath(
        "//*/div/div/div/div/h4/span[text() = '솔로']/parent::h4/parent::div/parent::div/parent::div/parent::div").get_attribute(
        'data-id')

    if pubgmode == "solo":
        pubgmode_str = "솔로"
    if pubgmode == "duo":
        pubgmode_str = "듀오"
    if pubgmode == "squad":
        pubgmode_str = "스쿼드"
    # 'data-status="fpp"'
    tpp_status = driver.find_element_by_xpath("//input[@id='rankedStatsChkMode']").get_attribute("data-status")
    if tpp == True:
        if tpp_status == "fpp":
            driver.find_element_by_xpath("//input[@id='rankedStatsChkMode']").click()
            print("tpp clicked")
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR,
                                                "#rankedStatsWrap > div.ranked-stats-wrapper__list > div[data-id='pc-2018-03|tpp|'][style='display: block;'][data-async='2']"))
            )
            driver.implicitly_wait(6)

        stat = driver.find_element_by_xpath("//*/div[@data-id='" + data_id + "']/div/div/div/h4/span[text() = '" + pubgmode_str + "']/parent::h4/parent::div")

        stat.screenshot('./stat/'+ pubgid + '_' + pubgmode + '_tpp.png')
        print("Screenshot Success")
    if tpp == False:
        pubgmode_str = pubgmode_str + " FPP"
        data_id = data_id.replace("tpp", "fpp")

        if tpp_status == "tpp":
            driver.find_element_by_xpath("//input[@id='rankedStatsChkMode']").click()
            print("fpp clicked")
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#rankedStatsWrap > div.ranked-stats-wrapper__list > div[data-id='pc-2018-03|fpp|'][style='display: block;'][data-async='2']"))
            )
            driver.implicitly_wait(6)

        stat = driver.find_element_by_xpath("//*/div[@data-id='" + data_id + "']/div/div/div/h4/span[text() = '" + pubgmode_str + "']/parent::h4/parent::div")
        stat.screenshot('./stat/' + pubgid + '_' + pubgmode + '_fpp.png')
        print("Screenshot Success")

    # 종료
    driver.quit()

def get_lol_stat(lolid):
    URL = ("https://www.op.gg/summoner/userName=" + lolid)
    html = get_ihtml(URL)
    soup = BeautifulSoup(html, 'html.parser')
    stat = []

    # # 최근 전적(게임타입, 승패)
    # entries = soup.find_all('div', {'class': 'GameItemWrap'})
    #
    # recent_entries = []
    # for i in range(5):
    #     line = []
    #
    #     entry = entries[i]
    #
    #     recent_game_type = entry.find('div', {'class': 'GameType'})
    #     recent_game_type = re.sub(pattern, '', recent_game_type.text)
    #     recent_game_result = entry.find('div', {'class': 'GameResult'})
    #     recent_game_result = re.sub(pattern, '', recent_game_result.text)
    #
    #     line.append(recent_game_type)
    #     line.append(recent_game_result)
    #
    #     recent_entries.append(line)
    #     print(line)
    # stat.append(recent_entries)

    # 최근 전적(게임타입, 승패)
    entries = soup.find_all('div', {'class': 'GameItemWrap'})
    recent_entries = []
    # 밑의 range의 변수로 가져올 전적 갯수 설정 (embed에 썸네일 추가시 5개 이상은 넘어감)
    for i in range(5):
        line = []

        entry = entries[i]

        recent_game_type = entry.find('div', {'class': 'GameType'})
        recent_game_type = re.sub(pattern, '', recent_game_type.text)
        recent_game_result = entry.find('div', {'class': 'GameResult'})
        recent_game_result = re.sub(pattern, '', recent_game_result.text)
        # 게임 타입 옵션
        if recent_game_type == "일반":
            recent_game_type = "Normal"
        elif recent_game_type == "솔랭":
            recent_game_type = " SoloR"
        elif recent_game_type == "자유5:5랭크":
            recent_game_type = " TeamR"
        elif recent_game_type == "무작위총력전":
            recent_game_type = " ARAM "
        elif recent_game_type == "Bot":
            recent_game_type = "  Bot "
        elif recent_game_type == "우르프":
            recent_game_type = "  Urf "
        else:
            recent_game_type = "   ?  "
        # 게임 결과 옵션
        if recent_game_result == "승리":
            recent_game_result = " 'Win'"
        elif recent_game_result == "패배":
            recent_game_result = " Lose "
        elif recent_game_result == "다시하기":
            recent_game_result = "replay"
        else:
            recent_game_result = "   ?  "

        line.append(recent_game_type)
        line.append(recent_game_result)

        recent_entries.append(line)

    text_table_top_start = "┏"
    text_table_top = "━━━━━━┳"
    text_table_top_end = "━━━━━━┓\n"

    text_table_middle_start = "┣"
    text_table_middle = "━━━━━━╋"
    text_table_middle_end = "━━━━━━┫\n"

    text_table_bottom_start = "┗"
    text_table_bottom = "━━━━━━┻"
    text_table_bottom_end = "━━━━━━┛"

    text_teble_wall = "┃"

    col_len = len(recent_entries)
    row_len = len(recent_entries[0])

    recent_ent = "```prolog\n"

    recent_ent = recent_ent + text_table_top_start
    for i in range(col_len-1):
        recent_ent = recent_ent + text_table_top
    recent_ent = recent_ent + text_table_top_end

    for j in range(row_len):
        recent_ent = recent_ent + text_teble_wall
        for i in range(col_len):
            recent_ent = recent_ent + recent_entries[i][j] + text_teble_wall
        recent_ent = recent_ent + "\n"

        if j != row_len-1:
            recent_ent = recent_ent + text_table_middle_start
            for i in range(col_len - 1):
                recent_ent = recent_ent + text_table_middle
            recent_ent = recent_ent + text_table_middle_end

    recent_ent = recent_ent + text_table_bottom_start
    for i in range(col_len - 1):
        recent_ent = recent_ent + text_table_bottom
    recent_ent = recent_ent + text_table_bottom_end + "```"

    # recent_entry = "```prolog\n┏━━━━━━┳━━━━━━┳━━━━━━┳━━━━━━┳━━━━━━┓\n┃" + recent_entries[0][0] + "┃" + recent_entries[1][0] + "┃" + recent_entries[2][0] + "┃" + recent_entries[3][0] + "┃" + recent_entries[4][0] + "┃\n┣━━━━━━╋━━━━━━╋━━━━━━╋━━━━━━╋━━━━━━┫\n┃" + recent_entries[0][1] + "┃" + recent_entries[1][1] + "┃" + recent_entries[2][1] + "┃" + recent_entries[3][1] + "┃" + recent_entries[4][1] + "┃\n┗━━━━━━┻━━━━━━┻━━━━━━┻━━━━━━┻━━━━━━┛```"
    stat.append(recent_ent)

    """
    op.gg 구조
    SummonerRatingMedium > TierRankInfo > RankType, TierRank, TierInfo > LeaguePoints, WinLose > wins, losses, winratio 
    
    :returns : stat = [recent_ent, rank_available, profile_image, tier_icon, rank_type, tier_rank, league_points, wins, losses, winratio]
    :returns : stat = [최근전적[게임타입, 승패], 랭크유무, 프로필이미지링크, 티어아이콘링크, 랭크타입, 현재티어, 점수, 승, 패, 승률]
    """
    profile_image = soup.find('img', {'class': 'ProfileImage'})
    profile_image = profile_image.get('src')
    profile_image = "http:" + profile_image

    solo_tier_info = soup.find('div', {'class': 'SummonerRatingMedium'})
    tier_rank_info = solo_tier_info.find('div', {'class': 'TierRankInfo'})
    tier_info = tier_rank_info.find('div', {'class': 'TierInfo'})

    if solo_tier_info.find('div', {'class': 'Medal tip'}):
        rank_available = True

        tier_icon = solo_tier_info.find('div', {'class': 'Medal tip'})
        tier_icon = tier_icon.find('img')
        tier_icon = tier_icon.get('src')
        tier_icon = "http:" + tier_icon

        rank_type = tier_rank_info.find('div', {'class': 'RankType'}).text
        tier_rank = tier_rank_info.find('div', {'class': 'TierRank'}).text

        league_points = tier_info.find('span', {'class': 'LeaguePoints'}).text
        league_points = re.sub(pattern, '', league_points)

        wins = tier_info.find('span', {'class': 'wins'}).text
        losses = tier_info.find('span', {'class': 'losses'}).text
        winratio = tier_info.find('span', {'class': 'winratio'}).text

        stat.append(rank_available)
        stat.append(profile_image)
        stat.append(tier_icon)
        stat.append(rank_type)
        stat.append(tier_rank)
        stat.append(league_points)
        stat.append(wins)
        stat.append(losses)
        stat.append(winratio)

        # = [rank_available, profile_image, tier_icon, rank_type, tier_rank, league_points, wins, losses, winratio]
    else:
        rank_available = False

        tier_icon = "http://opgg-static.akamaized.net/images/medals/default.png"

        stat.append(rank_available)
        stat.append(profile_image)
        stat.append(tier_icon)

    return stat
