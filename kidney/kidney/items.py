# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field


class HaodfItem(Item):
    collection = table = 'haodf_bj'
    # collection = table = 'haodf_hz'
    name = Field()
    department = Field()
    title = Field()
    expert = Field()  # 擅长
    experience = Field()  # 执业经历
    person_web = Field()  # 个人网站
    outpatient_time = Field()  # 门诊时间
    outpatient_info = Field()  # 门诊信息
    patient_tips = Field()  # 出诊提示
    warm_tips = Field()  # 温馨提示
