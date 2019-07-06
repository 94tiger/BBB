import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import re

pattern = re.compile((r'\s+'))

def get_ihtml(url):
    headers = {'Accept-Language': 'ko'}
    _ihtml = ""
    iresp = requests.get(url, headers = headers)
    # status_code가 정상이면
    if iresp.status_code == 200:
        _ihtml = iresp.text
    return _ihtml

def get_pubg_stat(pubgid, pubgmode):
    """
    :param pubgid:
    :param pubgmode:
    :return: stat [stat_KD, stat_AVD, stat_NoG, stat_PoV, avatar_img] [K/D, 평균딜, 게임수,
    """
    URL = ("https://dak.gg/profile/" + pubgid)
    ihtml = get_ihtml(URL)
    isoup = BeautifulSoup(ihtml, 'html.parser')
    ielement = isoup.find('section', {'class': pubgmode})
    # avatar = isoup.find('section', {'class' : })
    avatar = isoup.find('div', {'class' : 'userInfo'})
    avatar = avatar.find('img')
    avatar = avatar.get('src')
    if avatar == "/images/icons/avatars/kakao-dakgg.jpg":
        avatar = "https://dak.gg/images/icons/avatars/kakao-dakgg.jpg"
    avatar_img = str(avatar)
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

    # stat_list = "K/D : `" + stat_KD + "` 평딜 : ` " + stat_AVD + "` 게임수 : ` " + stat_NoG + "` 승률 : `" + stat_PoV + "`\n" + avatar_img
    stat = [stat_KD, stat_AVD, stat_NoG, stat_PoV, avatar_img]

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

def get_pubg_stat_screenshot(pubgid, pubgmode):
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

    # pubg.op.gg 접속
    driver.get(URL + pubgid)
    print("https://pubg.op.gg Connect Success")

    driver.find_element_by_xpath("//button[@id='renewBtn']").click()
    print("Refresh Success")
    driver.implicitly_wait(0.2)

    # Screenshots stat
    stat = driver.find_element_by_xpath("//div[@class='ranked-stats-wrapper__card ']/*[@class='ranked-stats-wrapper__card-title ranked-stats-wrapper__card-title--" + pubgmode + "']/parent::div")
    stat.screenshot('./stat/'+ pubgid + '_' + pubgmode + '.png')

    # 종료
    driver.quit()

def get_lol_stat(lolid):
    URL = ("https://www.op.gg/summoner/userName=" + lolid)
    html = get_ihtml(URL)
    soup = BeautifulSoup(html, 'html.parser')
    """
    op.gg 구조
    SummonerRatingMedium > TierRankInfo > RankType, TierRank, TierInfo > LeaguePoints, WinLose > wins, losses, winratio 
    
    :returns : stat = [rank_available, profile_image, tier_icon, rank_type, tier_rank, league_points, wins, losses, winratio]
    :returns : stat = [랭크유무, 프로필이미지링크, 티어아이콘링크, 랭크타입, 현재티어, 점수, 승, 패, 승률]
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

        stat = [rank_available, profile_image, tier_icon, rank_type, tier_rank, league_points, wins, losses, winratio]
    else:
        rank_available = False

        tier_icon = "http://opgg-static.akamaized.net/images/medals/default.png"
        stat = [rank_available, profile_image, tier_icon]
    return stat
