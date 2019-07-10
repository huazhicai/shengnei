"""
从redis中获取医生介绍界面的url， 爬取肾内科医生信息
Author: seven
"""

import time

import pymongo
from selenium import webdriver
from pyquery import PyQuery as pq
from redis import StrictRedis, ConnectionPool
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')     # 以根用户身份打开chrome , linux中添加
browser = webdriver.Chrome(options=chrome_options)

wait = WebDriverWait(browser, 9)

client = pymongo.MongoClient('localhost', 27017)
db = client['kidney']
collection = db['bj']

# 连接本地redis数据库
pool = ConnectionPool(host='localhost', port=6379, db=0)
redis_client = StrictRedis(connection_pool=pool)


def parse_detail(url):
    try:
        browser.get(url)
        # 需要设置一个等待网页加载的时间
        time.sleep(1)
        wait.until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, '#gray > div.container > div.mian'))
        )
        html = browser.page_source
        doc = pq(html)
        intro_url = url
        name = doc('.nav h1 a').text() or doc('div.lt_name > a > h1 > span:nth-child(1)').text()
        department = doc('div.lt > table:nth-child(1) tr td:nth-child(3) > a > h2').text()
        title = doc('div.lt > table:nth-child(1) tr:nth-last-child(3) > td:nth-last-child(1)').text()
        special = doc('#full_DoctorSpecialize').text() or '暂无'
        experience = doc('#full').text() or doc(
            'div.lt>table:nth-child(1) tr:nth-last-child(1) td:nth-last-child(1)').text()
        person_web = doc('.doctor-home-page.clearfix > span:nth-child(3) > a').text()

        outpatient_info = menzhen_info(doc)
        if name:
            yield {
                'name': name,
                'department': department,
                'title': title,
                'special': special,
                'experience': experience,
                'person_web': person_web,
                'outpatient_info': outpatient_info,
                'intro_url': intro_url
            }
        else:
            parse_detail(url)
    except TimeoutException as e:
        parse_detail(url)


# 获取门诊信息
def menzhen_info(doc):
    week = {1: '周一', 2: '周二', 3: '周三', 4: '周四', 5: '周五', 6: '周六', 7: '周日'}
    outpatient_info = []
    morning = doc('table.doctortimefrom1 tr:nth-child(2) td').items()
    for a, b in enumerate(morning):
        date = b('img').attr('title')
        if date:
            outpatient_info.append((week[a] + '上午', date))

    afternoon = doc('table.doctortimefrom1 tr:nth-child(3) td').items()
    for a, b in enumerate(afternoon):
        date = b('img').attr('title')
        if date:
            outpatient_info.append((week[a] + '下午', date))

    return outpatient_info


def save_to_mongo(result):
    # if collection.insert_one(result):
    # 通过mongodb进行去重操作，每次插入新数据前都会检查name是否存在，不存在就进行插入
    # if result['name']:
    collection.update_one({'name': result['name']}, {'$set': result}, True)
    # collection.insert_one(result)
    print(result)


def main():
    lens = redis_client.llen('haodf:items')
    for item in range(lens):
        url = redis_client.lindex('haodf:items', item).decode('utf-8')
        # url = redis_client.lpop('haodf:items').decode('utf-8')
        url = eval(url)['url']
        results = parse_detail(url)
        for result in results:
            save_to_mongo(result)


if __name__ == '__main__':
    main()
