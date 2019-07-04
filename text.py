import requests as requests
from pyquery import PyQuery as pq
import requests
from selenium import webdriver

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.90 Safari/537.36'
}

url = 'https://www.haodf.com/doctor/DE4r0Fy0C9LuSMGNiaENvQhmqEELeHuif.htm'

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
browser = webdriver.Chrome(options=chrome_options)
browser.get(url)
html = browser.page_source
doc = pq(html)
print(doc)

name = doc('.nav h1 a').text() or doc('div.lt_name span').text()
department = doc('div.lt > table > tbody td:nth-child(3) > a > h2').text()
title = doc('div.lt > table:nth-child(1) > tbody > tr:nth-child(2) > td:nth-child(3)').text()
special = doc('#full_DoctorSpecialize').text()
experience = doc('div.lt > table:nth-child(1) > tbody > tr:nth-child(4) > td:nth-child(3)').text()
person_web = doc('.doctor-home-page.clearfix > span:nth-child(3) > a').text()

