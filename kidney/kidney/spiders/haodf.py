# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

from ..items import HaodfItem


class HaodfSpider(CrawlSpider):
    name = 'haodf'
    # allowed_domains = ['haodf.com']
    start_urls = ['https://haoping.haodf.com/keshi/1008000/daifu_beijing.htm']

    rules = [
        Rule(LinkExtractor(allow=()), callback='parse_item'),
    ]

    def parse_item(self, response):
        item = HaodfItem()
        item['name'] = response.xpath('//*[@id="doctor_header"]/div[1]/div/a/h1/span[1]/text()').get()
        item['department'] = response.xpath(
            '//*[@id="bp_doctor_about"]/div/div[2]/div/table[1]/tbody/tr[2]/td[3]/a/h2/text()').get()
        item['title'] = response.xpath(
            '//*[@id="bp_doctor_about"]/div/div[2]/div/table[1]/tbody/tr[3]/td[3]/text()').get()
        item['expert'] = response.xpath('//*[@id="full_DoctorSpecialize"]/text()').extract_first()
        item['experience'] = response.xpath('//*[@id="truncate"]/text()').extract_first()
        item['person_web'] = response.xpath(
            '//*[@id="bp_doctor_about"]/div/div[2]/div/div[1]/span[3]/a/text()').extract_first()
        if item['person_web']:
            scrapy.Request(url=item['person_web'], callback='parse_person_web', meta={'item': item})
        else:
            pass
        next_page = response.xpath('//div[@class="p_bar"]/a[12]/@href').extract_first()
        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, callback='parse_item')

    def parse_person_web(self, response):
        # 门诊信息链接
        menzhen_info_url = response.xpath('//body/div[2]/div/div/ul/li[2]/a').re('门诊信息')
        if menzhen_info_url:
            yield scrapy.Request(menzhen_info_url, callback='parse_outpatient', meta=response.meta)

    # 解析门诊信息
    def parse_outpatient(self, response):
        outpatient_info = response.xpath('//ul[@class="menzhen-ul"]').extract()
        pass
