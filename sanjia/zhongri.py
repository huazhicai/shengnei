# 中日友好医院
# 肾内科医生信息
import json
import os

import requests
from pyquery import PyQuery as pq


def get_resp(url):
    try:
        response = requests.get(url)
        response.encoding = 'utf-8'
        if response.status_code == 200:
            return response.text
    except ConnectionError as e:
        print(e)


def parse_index(html):
    doc = pq(html)
    detaile_urls = doc('ul.docteam_list.clearfix li div.docteam_cont a.doc_name').items()
    return detaile_urls


def parse_detail(html, link):
    doc = pq(html)
    name = doc('ul.files li a.doc_name').text()
    title = doc('ul.files li:nth-child(2) span').text()
    department = doc('ul.files li:nth-child(3) span').text()
    special = doc('div.doc_intro p').text()
    resume = doc('div.doc_index_right1.otherdocmar').text() or doc('div.doc_index_right1').text()
    outpatient_info = parse_outpatient(doc)
    yield {
        'name': name,
        'title': title,
        'department': department,
        'special': special,
        'resume': resume,
        'outpatient_info': outpatient_info,
        'url': link,
    }


# 解析出诊信息
def parse_outpatient(doc):
    week = {2: '周四', 3: '周五', 4: '周六', 5: '周日', 6: '周一', 7: '周二', 8: '周三'}
    outpatient_info = []
    morning = doc('div.PCDisplay table tr:nth-child(2) td').items()
    for a, b in enumerate(morning):
        if b('span'):
            outpatient_info.append((week[a], '上午'))

    afternoon = doc('div.PCDisplay table tr:nth-child(3) td').items()
    for a, b in enumerate(afternoon):
        if b('span'):
            outpatient_info.append((week[a + 1], '下午'))

    return outpatient_info


def write_to_file(content):
    with open('.'.join([os.path.splitext(__file__)[0], 'txt']), 'a', encoding='utf-8') as f:
        f.write(json.dumps(content, ensure_ascii=False) + '\n')


def main(url):
    html = get_resp(url)
    detail_urls = parse_index(html)
    for url in detail_urls:
        link = 'https://www.zryhyy.com.cn' + url.attr('href')
        html = get_resp(link)
        results = parse_detail(html, link)
        for result in results:
            print(result)
            write_to_file(result)


if __name__ == '__main__':
    url = 'https://www.zryhyy.com.cn/Html/Departments/Main/DoctorTeam_33.html'
    main(url)
