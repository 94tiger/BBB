from selenium import webdriver

def get_stat(pubgid, pubgmode):
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
    driver.implicitly_wait(0.5)

    # Screenshots stat
    stat = driver.find_element_by_xpath("//div[@class='ranked-stats-wrapper__card ']/*[@class='ranked-stats-wrapper__card-title ranked-stats-wrapper__card-title--" + pubgmode + "']/parent::div")
    stat.screenshot('./stat/'+ pubgid + '_' + pubgmode + '.png')

    # 종료
    driver.quit()