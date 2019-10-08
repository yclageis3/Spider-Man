#-*- coding:utf-8 -*-

# 请求、解析 库
import requests
from selenium import webdriver
from bs4 import BeautifulSoup
from lxml import etree
import re

# sql 库
import pymysql
from pymongo import MongoClient

import time
import random
import os

# 删除文件夹 库
import shutil

# 中文转url编码
from urllib import parse

class Lv_spider:

    def __init__(self):
        # webdriver
        self.driver = webdriver.ChromeOptions()
        self.driver.add_argument('headless')
        self.driver = webdriver.Chrome( chrome_options=self.driver)

        self.sheng_name = ''
        self.shi_name = ''
        self.jq_name = ''
        self.level = ''
        self.addr_path = ''

        # 请求头
        self.headers = {
            "Host": "s.lvmama.com",
            "Referer": "http://s.lvmama.com/ticket/H191K410100?keyword={}&tabType=route".format(parse.quote(self.sheng_name)),
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36",
        }
        
        # mongo 连接
        self.conn = MongoClient('192.168.120.51', 27017)  # 创建MongoDB连接
        self.lvmama = self.conn.lvmama  # 创建数据库连接
        self.henan = self.lvmama.henan

        # 时间
        self.now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

        pass


    def shi_info(self, area_list: list):
        # http://s.lvmama.com/ticket/?keyword=%E5%8C%97%E4%BA%AC&k=1&dropdownlist=true#list
        for area in area_list:
            if area not in ['河南']:
                continue
            self.sheng_name = area
            url = r'http://s.lvmama.com/ticket/K410100?keyword={}&k=0#list'.format(area)

            resp = requests.get(url, headers=self.headers)
            html = etree.HTML(resp.text)

            # 市区内景区列表
            # a = html.xpath('//div[@class="search-lists"]/div[1]/ul/li//a/text()')
            for shi_name in html.xpath('//div[@class="search-lists"]/div[1]/ul/li//a/text()'):
                self.shi_name = shi_name
                url_page = r'http://s.lvmama.com/ticket/K410100?keyword={}&k=0#list'.format(shi_name)

                # 拼接 页数 url
                for num in range(self.page_num(url_page=url_page)):
                    url_info = r'http://s.lvmama.com/ticket/K410100P{}?keyword={}&k=0#list'.format(num+1, shi_name)

                    # 单页 景区列表
                    self.jq_list(url_info=url_info)

                    pass

                pass

            pass

        pass


    def page_num(self, url_page):
        resp = requests.get(url_page, headers=self.headers)
        time.sleep(random.randint(5, 10))
        html = etree.HTML(resp.text)

        num = html.xpath('//div[@class="pagebox"]/a/text()')[-2]
        return int(num)
        

    def jq_list(self, url_info):
        resp = requests.get(url_info, headers=self.headers)
        time.sleep(random.randint(5, 10))
        html = etree.HTML(resp.text)

        for item in html.xpath('//div[@class="product-list"]/div/div[1]/div[2]'):
            # 景区名称
            self.jq_name = item.xpath('./h3/a/@title')[0]
            # 景区级别
            self.level = item.xpath('./h3/span[2]/text()')[0].count('A')
            jq_url = item.xpath('./h3/a/@href')[0]

            # 访问详情页
            self.page_info(jq_url=jq_url)

            pass

        pass


    def page_info(self, jq_url):
        self.driver.get(jq_url)
        time.sleep(random.randint(5, 10))
        html = etree.HTML(self.driver.page_source)

        # print(self.sheng_name, self.shi_name, self.jq_name, self.level)

        address = self.list_to_str(html.xpath('//p[@class="linetext"]/@title'))
        opentime = ''
        if html.xpath('//div[@class="hasdown-pre"]/p/text()'):
            opentime = self.list_to_str(html.xpath('//div[@class="hasdown-pre"]/p/text()'))
        else:
            opentime = self.list_to_str(html.xpath('//div[@class="sec-inner"]/dl[2]/dd/p/text()'))

        yang_dict = self.yangtu(html.xpath('//dl[@class="pic_tab_dl"]/dd/img/@src'))
        xiang_dict = self.xiangtu(html.xpath('//div[@id="introduction"]/div[2]//img/@to'))

        div_code = self.div_code(url=jq_url).replace('to=', 'src=')

        div_code += '景区:  {}</br>'.format(self.jq_name)
        div_code += '地址:  {}</br>'.format(address)
        div_code += '开放时间:  {}</br></br>'.format(opentime)

        # 创建目录
        self.addr_path = r'//192.168.100.173/移动库/旅游景区/驴妈妈/{}/{}/{}/'.format(self.sheng_name, self.shi_name, self.jq_name)

        self.make_dir(addr_path=self.addr_path)
        print('创建目录成功啦!')

        car_title = html.xpath('//div[@class="nchTrafficDerc clearfix"]/div[1]/ul/li/b/text()')
        car_content = html.xpath('//div[@class="nchTrafficDerc clearfix"]/div[@class="nchTrafficTab"]')

        traffic_info = ''
        # print('交通指南:\n')
        for k, v in zip(car_title, car_content):
            content = ''
            for i in v.xpath('./div/p//text()'):
                content += '{} </br>'.format(i)
            traffic_info += '{}</br>\n{}</br>\n'.format(k, content)
            # print(traffic_info)
            pass

        div_code += traffic_info

        if self.insert_MongoDB(jq_name=self.jq_name, yang_dict=yang_dict, xiang_dict=xiang_dict, div_code=div_code):
            print('插入Mongo成功\n')
        else:
            if not os.path.isdir(self.addr_path):
                shutil.rmtree(self.addr_path)
                print('目录以移除!')

        pass


    def div_code(self, url):
        self.driver.get(url)
        time.sleep(random.randint(5, 10))
        soup = BeautifulSoup(self.driver.page_source)
        # 图文 html源码
        wz_code = ''

        try:
            # 图文介绍
            if soup.find_all('div', id='introduction'):
                for item in soup.find_all('div', id='introduction'):
                    wz_code += str(item)
                    pass
        except Exception as ex:
            print(ex.args)
            with open('错误.txt', 'a+', encoding='utf-8') as f:
                f.write('{}  获取div源码错误  {}'.format(self.now, ex.args))

        return wz_code


    def insert_MongoDB(self, jq_name, yang_dict, xiang_dict, div_code):
        # print(yang_dict)
        # print(xiang_dict)
        try:
            self.henan.insert({
                '景区名称': self.jq_name,
                '样图位置': yang_dict,
                '详图位置': xiang_dict,
                '图片位置': div_code,
            })

            return True
        except Exception as ex:
            print(ex.args)
            with open('错误.txt', 'a+', encoding='utf-8') as f:
                f.write('{}  插入mongo错误  {}'.format(self.now, ex.args))
            return False


    def yangtu(self, img_list: list) -> dict:
        local_path = {}
        if img_list:
            try:
                for k, v in enumerate(img_list, 1):
                    resp = requests.get(v).content
                    file_name = '样{}.jpg'.format(k)
                    with open(file_name, 'wb+') as f:
                        f.write(resp)
                        local_path['样图{}'.format(k)] = [v, (os.path.join(os.getcwd(), file_name))  ]
            except Exception as ex:
                print(ex.args)
                with open('错误.txt', 'a+', encoding='utf-8') as f:
                    f.write('{}  保存图片错误  {}'.format(self.now, ex.args))
                    
        return local_path


    def xiangtu(self, img_list: list) -> dict:
        local_path = {}
        if img_list:
            try:
                for k, v in enumerate(img_list, 1):
                    resp = requests.get(v).content
                    file_name = '详{}.jpg'.format(k)
                    with open(file_name, 'wb+') as f:
                        f.write(resp)
                        local_path['祥图{}'.format(k)] = [v, (os.path.join(os.getcwd(), file_name))]
            except Exception as ex:
                print(ex.args)
                with open('错误.txt', 'a+', encoding='utf-8') as f:
                    f.write('{}  保存图片错误  {}'.format(self.now, ex.args))

        return local_path


    def make_dir(self, addr_path):
        try:
            if os.path.exists(addr_path) == False:
                os.makedirs(addr_path)
            pass
        except Exception as ex:
            print('{}  创建目录错误  {}'.format(self.now, ex.args))
            with open('错误.txt', 'a+', encoding='utf-8') as f:
                f.write('{}  创建目录错误  {}'.format(self.now, ex.args))


    def list_to_str(self, data_list: list) -> str:
        string = ''

        for item in data_list:
            string += item.strip() + '\n'
            pass

        return string
    

    pass

if __name__ == '__main__':
    # 省份列表, 拼接按省份搜索的url http://s.lvmama.com/ticket/?keyword=%E5%8C%97%E4%BA%AC&k=1&dropdownlist=true#list
    area_list = [
        "北京",
        "天津",
        "上海",
        "重庆",
        "香港",
        "澳门",
        "安徽",
        "福建",
        "甘肃",
        "广东",
        "广西",
        "贵州",
        "海南",
        "河北",
        "河南",
        "黑龙江",
        "湖北",
        "湖南",
        "吉林",
        "江苏",
        "江西",
        "辽宁",
        "内蒙古",
        "宁夏",
        "青海",
        "山东",
        "山西",
        "陕西",
        "四川",
        "西藏",
        "新疆",
        "云南",
        "浙江",
    ]

    lv = Lv_spider()
    lv.shi_info(area_list=area_list)
    
    
    