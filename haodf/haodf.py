import requests
from pyquery import PyQuery as pq
import pymongo
from selenium import webdriver

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.90 Safari/537.36'
}

client = pymongo.MongoClient(host='localhost', port=27017)
db = client['kidney']
collection = db['haodf_bj']


def get_index(page):
    url = 'https://haoping.haodf.com/keshi/1008000/daifu_beijing_{}.htm'.format(page)
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.text
    except requests.ConnectionError:
        return None


# 解析索引页，提取详情页url
def parse_index(html):
    doc = pq(html)
    detail_links = doc('.good_doctor_list_td tr:nth-child(1) td:nth-child(2) a:nth-child(1)').items()
    if detail_links:
        return detail_links


def get_detail(url):
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.text
    except requests.ConnectionError:
        return None


def parse_detail(url):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    browser = webdriver.Chrome(options=chrome_options)
    browser.get(url)
    html = browser.page_source
    doc = pq(html)
    intro_url = url
    name = doc('.nav h1 a').text() or doc('div.lt_name > a > h1 > span:nth-child(1)').text()
    department = doc('div.lt > table > tbody td:nth-child(3) > a > h2').text()
    title = doc('div.lt > table:nth-child(1) > tbody > tr:nth-child(2) > td:nth-child(3)').text()
    special = doc('#full_DoctorSpecialize').text()
    experience = doc('div.lt > table:nth-child(1) > tbody > tr:nth-child(4) > td:nth-child(3)').text()
    person_web = doc('.doctor-home-page.clearfix > span:nth-child(3) > a').text()
    if person_web:
        outpatient_info = parse_outpatient_info(person_web)
    else:
        outpatient_info = parse_menzheng_info(doc)
    yield {
        'intro_url': intro_url,
        'name': name,
        'department': department,
        'title': title,
        'special': special,
        'experience': experience,
        'person_web': person_web,
        'outpatient_info': outpatient_info
    }


# 获取解析门诊信息
def parse_outpatient_info(url):
    response = get_detail(url)
    if response:
        doc = pq(response)
        outpatient_url = doc('ul.clearfix.f16 > li:nth-child(2) > a').attr('href')
        if outpatient_url.endswith('scheduletips.htm'):
            resp = get_detail('https:' + outpatient_url)
            if resp:
                doc = pq(resp)
                # 出诊信息
                info = doc('.menzhen-ul-li').items()
                outpatient_info = [i.text().split('\n') for i in info]
                return outpatient_info
        else:
            return '无门诊'


# 无个人网站的门诊信息
def parse_menzheng_info(doc):
    week = {1: '周一', 2: '周二', 3: '周三', 4: '周四', 5: '周五', 6: '周六', 7: '周日'}
    outpatient_info = []
    morning = doc('table.doctortimefrom1 tr:nth-child(2) td').items()
    for a, b in enumerate(morning):
        date = b('img').attr('title')
        if date:
            outpatient_info.append((week[a], '上午', date))

    afternoon = doc('table.doctortimefrom1 tr:nth-child(3) td').items()
    for a, b in enumerate(afternoon):
        date = b('img').attr('title')
        if date:
            outpatient_info.append((week[a], '下午', date))

    return outpatient_info


def save_to_mongo(result):
    # if collection.insert_one(result):
    # 通过mongodb进行去重操作，每次插入新数据前都会检查name是否存在，不存在就进行插入
    if result['name']:
        collection.update_one({'name': result['name']}, {'$set': result}, True)
        print(result)


def main(page):
    resp = get_index(page)
    detail_links = parse_index(resp)
    for link in detail_links:
        url = 'https:' + link.attr('href')
        results = parse_detail(url)
        for result in results:
            save_to_mongo(result)


if __name__ == '__main__':
    for page in range(10, 21):
        main(page)
