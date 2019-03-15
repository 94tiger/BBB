import requests
from bs4 import BeautifulSoup
import re

pattern = re.compile((r'\s+'))

def get_ihtml(url):
    _ihtml = ""
    iresp = requests.get(url)
    # status_code가 정상이면
    if iresp.status_code == 200:
        _ihtml = iresp.text
    return _ihtml

def get_stat(pubgid, pubgmode):
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