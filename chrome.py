# -*- coding: utf-8 -*-

from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from bs4 import BeautifulSoup
import datetime
import json
import contentsInfo
import sys
import os
sys.path.append('/settings')
from settings import config

chromeDriver = config.env['chromeDriverPath']

# enable browser logging
caps = DesiredCapabilities.CHROME
caps['loggingPrefs'] = {'performance': 'ALL'}

# 옵션을 줘본다.
options = webdriver.ChromeOptions()
options.headless = True
options.add_argument('--no-sandbox')
options.add_argument('headless')
# options.add_argument('window-size=1920x1080')			# size를 표기할 때에는 *가아니고 소문자x입니다.
options.add_argument('hide-scrollbars')			# 스크롤바 감추기


# setup driver(chrome) : 크롬드라이버를 사용하는 driver 생성
driver = webdriver.Chrome(chromeDriver, chrome_options=options)

networkPerformanceList = []

abspath = os.path.dirname(os.path.abspath(__file__))
with open(abspath+'/crawlingUrl.json')as url_file:
    url_data = json.load(url_file)
    print(url_data['url'])
    urls = url_data['url']

    for url in urls:
        print('url>>>> ', url)

        driver.get(url)

        # scrolling & performance
        performance_log = contentsInfo.performance(driver)
        networkPerformance = contentsInfo.get_network_performance(url, driver, performance_log)
        networkPerformanceList.append(networkPerformance)

today = datetime.datetime.today().strftime('%Y%m%d%H%M%S')

filePath = config.env['filePath']
imgSize = config.img_size

print('imgSize>>>> ', imgSize)

# 이미 파일이 존재하면 기존 파일을 _today 로 붙여서 저장 후, 새로 파일을 저장한다.
try:
    os.rename(filePath+'imgResources.json', filePath+'imgResources_'+today+'.json')
except FileNotFoundError as e:
    print(filePath+'imgResources.json 파일이 존재하지 않아 backup 파일을 생성할 수 없습니다.')

with open(config.env['filePath']+'imgResources.json', 'w', encoding='utf-8') as file:
    json.dump(networkPerformanceList, file, ensure_ascii=False, indent='\t')
    print(filePath+'imgResources.json 파일 생성 완료.')

driver.quit()


