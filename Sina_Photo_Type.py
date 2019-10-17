# -*- coding:utf-8 -*-
import requests
from selenium import webdriver
from selenium.webdriver import ChromeOptions
from lxml import etree
import time

from pymongo import MongoClient

import re


class Sina_Photo:

    def __init__(self):
        self.url_init = r'http://slide.photo.sina.com.cn/'
        self.headers = {
            "Cookie": "SINAGLOBAL=125.41.129.104_1569037716.347762; SCF=AiF696XccWdBoT4kgBmCEK9jt2Rvv5q7SXcyzFnmQOIiwgIx6KQLUtOSaRP9j4KGzAsv-fUKQIDDRCnW6_sDgf0.; UOR=www.baidu.com,finance.sina.com.cn,; U_TRS1=00000088.de441402.5d8c5e9e.059d3a13; lxlrttp=1560672234; UM_distinctid=16d75740af8aeb-084ff261d0e5b4-67e1b3f-1fa400-16d75740af9318; SUB=_2AkMq-fnsdcPxrAVYmfkVzmLmaI5H-jyZLJAaAn7tJhMyAhh77gYkqSVutBF-XMhMvmSfga0tsHarCd3skYfhXzkP; SUBP=0033WrSXqPxfM72wWs9jqgMF55529P9D9W5VlP.OMDVMfZdfkdXU8d565JpVF020eh2XSoefSh5c; Apache=125.41.136.210_1571221257.139609; SGUID=1571221260457_2255427; ULV=1571221260551:8:5:4:125.41.136.210_1571221257.139609:1571221257763",
            "Host": "slide.photo.sina.com.cn",
            "Referer": "http://photo.sina.com.cn/",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36",
        }
        
        # mongo 连接
        self.conn = MongoClient('192.168.120.51', 27017)  # 创建MongoDB连接
        self.sina_photo = self.conn['sina_photo']  # 创建数据库连接
        self.all_type = self.sina_photo['all_type']

        self.reg_baseurl = re.compile(r"var BASEURL = '.*';")

        pass


    def get_type(self):
        option = ChromeOptions()
        option.add_argument('headless')
        driver = webdriver.Chrome(options=option)
        driver.get(self.url_init)
        html = etree.HTML(driver.page_source)
        driver.quit()

        # 一级分类
        type_name_list = html.xpath('//div[@id="nav-slider-wrap"]/ol/li/a/text()')
        type_urls_list = html.xpath('//div[@id="nav-slider-wrap"]/ol/li/a/@href')

        for name, urls in zip(type_name_list, type_urls_list):
            print(name, urls)  # 一级分类: 类别  urls

            time.sleep(3)
            option = ChromeOptions()
            option.add_argument('headless')
            driver = webdriver.Chrome(options=option)
            driver.get(urls)
            html = etree.HTML(driver.page_source)
            driver.quit()
            
            # 二级分类
            if len(html.xpath('//div[@class="inner"]/ul/li/a/text()')[1:]) > 1:
                type_name_list2 = html.xpath('//div[@class="inner"]/ul/li/a/text()')[2:]
                type_urls_list2 = html.xpath('//div[@class="inner"]/ul/li/a/@href')[2:]
            else:
                type_name_list2 = html.xpath('//div[@class="inner"]/ul/li/a/text()')[1:]
                type_urls_list2 = html.xpath('//div[@class="inner"]/ul/li/a/@href')[1:]

            for name2, urls2 in zip(type_name_list2, type_urls_list2):
                page_number = self.page_number(urls2)
                api = self.api(urls2)
                print('      ', name2, api, page_number)  # 二级分类: 类别  urls

                self.all_type.insert({
                    "lerve_1": name,
                    "lerve_2": name2,
                    "api": api,
                    "page_number": page_number
                })

            pass

        pass


    def page_number(self, urls):
        time.sleep(1)
        option = ChromeOptions()
        option.add_argument('headless')
        driver = webdriver.Chrome(options=option)
        driver.get(urls)
        html = etree.HTML(driver.page_source)
        driver.quit()

        max_page_num = int(html.xpath('//span[@class="pager-a-txt"]/span/text()')[0])

        return max_page_num


    def api(self, urls):
        time.sleep(1)
        option = ChromeOptions()
        option.add_argument('headless')
        driver = webdriver.Chrome(options=option)
        driver.get(urls)
        resp = driver.page_source
        driver.quit()

        baseurl = self.reg_baseurl.findall(resp)[0]

        return baseurl.split("'")[1]






    pass

if __name__ == '__main__':
    sina_photo = Sina_Photo()
    sina_photo.get_type()
    