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
import json

# 删除文件夹库
import shutil

# 写入csv
import csv


class Ctrip_Area:

    def __init__(self):
        # webdriver
        self.driver = webdriver.ChromeOptions()
        self.driver.add_argument('headless')
        self.driver = webdriver.Chrome( chrome_options=self.driver)
        # 请求头
        self.headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36",
            "cookie": "_abtest_userid=349cd4ed-5af5-4530-b802-a676576cc995; _RSG=9DKv21sZgO7JnPJpG_Uxt9; _RDG=28196a3ab5b620296c0d879b432aaa5274; _RGUID=762a8f60-42e5-4349-9dfb-7bf4334d9c53; _ga=GA1.2.1849946178.1569376974; MKT_Pagesource=PC; GUID=09031104212064802052; _RF1=219.157.246.11; _gid=GA1.2.1475100398.1569502085; gad_city=01e2fcd36d1bc003f51f35eff054dab1; StartCity_Pkg=PkgStartCity=2; TicketSiteID=SiteID=1017; ASP.NET_SessionSvc=MTAuMTQuMy4xODB8OTA5MHxvdXlhbmd8ZGVmYXVsdHwxNTY2ODc0NTQ5NjQ2; Session=smartlinkcode=U130026&smartlinklanguage=zh&SmartLinkKeyWord=&SmartLinkQuary=&SmartLinkHost=; Union=AllianceID=4897&SID=130026&OUID=&Expires=1570151473278; _bfa=1.1569545793754.yt827.1.1569545793754.1569545793754.1.35; _bfs=1.35; _jzqco=%7C%7C%7C%7C1569502085133%7C1.1907424426.1569376974004.1569547075436.1569547642131.1569547075436.1569547642131.undefined.0.0.54.54; __zpspc=9.4.1569546673.1569547642.28%232%7Cwww.baidu.com%7C%7C%7C%7C%23; appFloatCnt=51; _bfi=p1%3D290528%26p2%3D290528%26v1%3D35%26v2%3D34",
            "referer": "https://www.ctrip.com/",
        }
        # mongo 连接
        self.conn = MongoClient('192.168.120.51', 27017)  # 创建MongoDB连接
        self.ctrip = self.conn.ctrip  # 创建数据库连接
        self.henan = self.ctrip.henan

        # 时间
        self.now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

        # 目录
        self.sheng_name = ''
        self.shi_name = ''
        self.wz_title = ''

        # 地区
        self.area = {}

        # 正则匹配 id
        self.reg = re.compile(r'\d+')

        # 目录
        self.addr_path = ''

        pass

    """
    获取省份 url id
    url --> /sitemap/spots/c100058
    'https://you.ctrip.com{}'.format(url)

    id = reg.findall(url)[-1]

    省份 + id + url --> 另存

    """
    def sheng_info(self, url):
        resp = requests.get(url, headers=self.headers, verify=False)
        html = etree.HTML(resp.text)

        sheng_list = html.xpath('//div[@class="sitemap_block"]')
        sheng_dict = {}

        if sheng_list:
            
            for sheng_ in sheng_list[9:10]:  # 河南
                shi_list = []
                shi_dict = {}

                self.sheng_name = sheng_.xpath('./div/h2/text()')[0].strip()

                for addr, url in zip(sheng_.xpath('./ul//a/@title'), sheng_.xpath('./ul//a/@href')):
                    shi_dict[addr] = 'https:{}'.format(url)
                    # print(shi_dict)
                    pass

                shi_list.append(shi_dict)
                sheng_dict[self.sheng_name] = shi_list

                pass

            # del sheng_dict['上海']  # 删除上海地区
            # print(sheng_dict)
            self.shi_info(sheng_dict=sheng_dict)

        # with open('JSON-省份链接.txt', 'w+') as f:
        #     f.write(json.dumps(sheng_dict))
        #     print('>>> JSON-省份链接 <<< 写入成功!    路径 >>> {}'.format(os.path.join(os.getcwd(), 'JSON-省份链接.txt')))

        pass


    """
    获取市级 url title
    url --> /sightlist/zhengzhou157.html
    'https://you.ctrip.com{}'.format(url)

    id = reg.findall(url)[-1]

    title + url --> 另存

    """
    def shi_info(self, sheng_dict: dict):

        for sheng_ in sheng_dict:
            print(sheng_dict[sheng_])

            for shi_ in sheng_dict[sheng_][0]:
                self.sheng_name = sheng_
                self.shi_name = shi_
                if self.shi_name in ['商丘景点', '郑州景点']:
                    continue
                url = sheng_dict[sheng_][0][shi_]
                url_split = url.split('.html')
                
                time.sleep(random.randint(1, 2))
                resp = requests.get(url, headers=self.headers, verify=False)
                html = etree.HTML(resp.text)

                for i in range(int(html.xpath('//b[@class="numpage"]/text()')[0])):
                    url_new = '{}/s0-p{}.html'.format(url_split[0], i+1)
                    self.ctrip_id(shi_url=url_new)

                    pass


            pass


    """
    获取景区 id, 拼接url
    url --> /sight/zhengzhou157/9593.html

    id = reg.findall(url)[-1]

    new_url = 'https://piao.ctrip.com/ticket/dest/t{}.html'.format(id)

    景区名 + id + new_url --> 另存

    """
    def ctrip_id(self, shi_url):
        time.sleep(random.randint(1, 3))
        resp = requests.get(shi_url, headers=self.headers, verify=False)
        html = etree.HTML(resp.text)

        info_dict = {}

        title_list = html.xpath('//div[@class="rdetailbox"]//dt/a/@title')
        url_list = html.xpath('//div[@class="rdetailbox"]//dt/a/@href')

        
        for k, v in zip(title_list[2:], url_list[2:]):
            self.wz_title = k.replace('/', '')

            wz_id = self.reg.findall(v)[-1]
            wz_url = 'https://piao.ctrip.com/ticket/dest/t{}.html'.format(wz_id)

            info_dict[k] = wz_url
            self.page_info(wz_url=wz_url)

            pass

        pass

    
    def page_info(self, wz_url):
        time.sleep(random.randint(5, 15))
        resp = requests.get(wz_url, headers=self.headers, verify=False)

        html = etree.HTML(resp.text)

        if html.xpath('//div[@class="brief-right"]/span/strong/text()'):
            star = html.xpath('//div[@class="brief-right"]/span/strong/text()')[0]
            a = self.wz_title
            self.wz_title = '【{}A】{}'.format(star.count('A'), a)  # 

        
        self.addr_path = r'//192.168.100.173/移动库/旅游景区/携程/{}/{}/{}/'.format(self.sheng_name, self.shi_name, self.wz_title)
        # 创建目录
        self.make_dir(self.addr_path)
            
        yangtu = self.yangtu(self.driver_yangtu(wz_url))
        xiangtu = self.xiangtu(html.xpath('//div[@class="introduce-content"]/p/img/@src'))
        div_code = self.div_code(wz_url)

        if self.insert_MongoDB(yangtu=yangtu, xiangtu=xiangtu, div_code=div_code):
            print('插入Mongo成功\n')
        else:
            if not os.path.isdir(self.addr_path):
                shutil.rmtree(self.addr_path)

        pass


    def div_code(self, wz_url):
        self.driver.get(wz_url)
        soup = BeautifulSoup(self.driver.page_source)

        # 图文 html源码
        wz_code = ''

        try:
            # 头部介绍
            if soup.find_all('div', class_='brief-right'):
                for item in soup.find_all('div', class_='brief-right'):
                    wz_code += str(item)
                    pass
                pass
            pass

            # 图文介绍
            if soup.find_all('div', class_='content-wrapper'):
                for item in soup.find_all('div', class_='content-wrapper')[1]:
                    wz_code += str(item)
                    pass
                pass
            pass

        except Exception as ex:
            print('{}  获取div源码错误  {}'.format(self.now, ex.args))
            with open('错误.txt', 'a+', encoding='utf-8') as f:
                f.write('{}  获取div源码错误  {}'.format(self.now, ex.args))

        return wz_code


    def insert_MongoDB(self, yangtu, xiangtu, div_code):
        try:
            self.henan.insert({
                '景区名称': self.wz_title,
                '样图位置': yangtu,
                '详图位置': xiangtu,
                '图文代码': div_code,
            })

            self.down_csv(yangtu, xiangtu, div_code)

            return True
        except Exception as ex:
            print('{}  插入mongo错误  {}'.format(self.now, ex.args))
            with open('错误.txt', 'a+', encoding='utf-8') as f:
                f.write('{}  插入mongo错误  {}'.format(self.now, ex.args))
            return False


    def down_csv(self, yangtu, xiangtu, div_code):
        try:
            file_name = '{}/{}.csv'.format(self.addr_path, self.wz_title)
            with open(file_name, 'w+', encoding='utf-8-sig', newline='') as f:
                csvObj = csv.writer(f)
                csvObj.writerow(
                    ['景区名称', '样图位置', '详图位置', '图文代码'])
                csvObj.writerow([self.wz_title, str(yangtu), str(xiangtu), div_code])
                print('{} {}【{}.csv】已写入'.format(self.sheng_name, self.shi_name, self.wz_title))

        except Exception as ex:
            print('{}  写入csv错误  {}'.format(self.now, ex.args))
            with open('错误.txt', 'a+', encoding='utf-8') as f:
                f.write('{}  写入csv错误  {}'.format(self.now, ex.args))

            pass

        pass


    def yangtu(self, img_list: list) -> dict:
        local_path = {}
        if img_list:
            try:
                for k, v in enumerate(img_list, 1):
                    time.sleep(random.randint(1, 3))
                    resp = requests.get(v).content
                    file_name = self.addr_path + '样{}.jpg'.format(k)
                    with open(file_name, 'wb+') as f:
                        f.write(resp)
                        local_path['样图{}'.format(k)] = [v, (os.path.join(os.getcwd(), file_name))]  
                print('样图保存ok啦')
            except Exception as ex:
                print('{}  保存图片错误  {}'.format(self.now, ex.args))
                with open('错误.txt', 'a+', encoding='utf-8') as f:
                    f.write('{}  保存图片错误  {}'.format(self.now, ex.args))
                    
        return local_path


    def driver_yangtu(self, url) -> list:
        time.sleep(random.randint(1, 3))

        self.driver.get(url)
        html = etree.HTML(self.driver.page_source)

        img_list = html.xpath('//div[@class="small_photo_wrap"]/ul//li/a/img/@src')
        if img_list:
            return img_list

        pass


    def xiangtu(self, img_list: list) -> dict:
        local_path = {}
        if img_list:
            try:
                for k, v in enumerate(img_list, 1):
                    time.sleep(random.randint(1, 3))                    
                    resp = requests.get(v).content
                    file_name = self.addr_path + '详{}.jpg'.format(k)
                    with open(file_name, 'wb+') as f:
                        f.write(resp)
                        local_path['祥图{}'.format(k)] = [v, (os.path.join(os.getcwd(), file_name))] 
                print('详情图保存OK啦')    
            except Exception as ex:
                print('{}  保存图片错误  {}'.format(self.now, ex.args))
                with open('错误.txt', 'a+', encoding='utf-8') as f:
                    f.write('{}  保存图片错误  {}'.format(self.now, ex.args))
                    
        return local_path


    def make_dir(self, addr_path):
        try:
            
            if os.path.exists(self.addr_path) == False:
                os.makedirs(self.addr_path)
            pass

        except Exception as ex:
            print('{}  创建目录错误  {}'.format(self.now, ex.args))
            with open('错误.txt', 'a+', encoding='utf-8') as f:
                f.write('{}  创建目录错误  {}'.format(self.now, ex.args))

    pass

if __name__ == '__main__':
    url = r'https://you.ctrip.com/sitemap/spotdis/c0'
    ctrip = Ctrip_Area()
    ctrip.sheng_info(url=url)
    
