# 首都医科大学附属北京朝阳医院
# 肾内科科室专家，代号 289
import json
import os

import requests
from pyquery import PyQuery as pq
import pandas


def get_resp(url):
    try:
        response = requests.get(url)
        response.encoding = 'utf-8'
        if response.status_code == 200:
            return response.text
    except ConnectionError as e:
        print(str(e))


def parse_index(html):
    doc = pq(html)
    detail_urls = doc('.doctorList.mt15 .doct_li a.doc_name').items()
    return detail_urls


def parse_detail(url):
    html = get_resp(url)
    doc = pq(html)
    name_title = doc('div.doct_con p:nth-child(1)').text()
    department = doc('div.doct_con p.szks_list').text()
    special = doc('div.doct_con p.doc_ShanChang').text()
    resume = doc('div.tab_box p').text()
    outpatient_info = parse_outpatient(doc)
    yield {
        'name_title': name_title,
        'deaprtment': department,
        'special': special,
        'resume': resume,
        'outpatient_info': outpatient_info,
    }


# 解析出诊信息
def parse_outpatient(doc):
    week = {2: '周一', 3: '周二', 4: '周三', 5: '周四', 6: '周五', 7: '周六', 8: '周日'}
    outpatient_info = []
    morning = doc('div.PCDisplay table tr:nth-child(2) td').items()
    for a, b in enumerate(morning):
        if b('span'):
            outpatient_info.append((week[a], '上午'))

    afternoon = doc('div.PCDisplay table tr:nth-child(3) td').items()
    for a, b in enumerate(afternoon):
        if b('span'):
            outpatient_info.append((week[a+1], '下午'))

    return outpatient_info


def write_to_file(content):
    with open('.'.join([os.path.splitext(__file__)[0], 'txt']), 'a', encoding='utf-8') as f:
        f.write(json.dumps(content, ensure_ascii=False) + '\n')


def main(url):
    resp = get_resp(url)
    detail_urls = parse_index(resp)
    for url in detail_urls:
        url = 'https://www.bjcyh.com.cn' + url.attr('href')
        results = parse_detail(url)
        for result in results:
            print(result)
            write_to_file(result)


if __name__ == '__main__':
    url = 'https://www.bjcyh.com.cn/Html/Departments/Main/DoctorTeam_289.html'
    main(url)
