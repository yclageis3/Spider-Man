# -*- coding:utf-8 -*-
import requests
from selenium import webdriver
from selenium.webdriver import ChromeOptions
from lxml import etree

from pymongo import MongoClient
import pandas as pd

import re, os, json, time, csv


class Sina_Photo:

    def __init__(self):
        self.url_init = ''
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

        self.reg = re.compile(r'{.*}')

        self.lever_1 = ''
        self.lever_2 = ''
        self.name = ''
        self.createtime = ''
        self.creator = ''

        self.addr_path = ''



        pass


    def page_number(self):
        # http://api.slide.news.sina.com.cn/interface/api_album.php?activity_size=198_132&size=img&ch_id=1&sub_ch=c
        # &page=2&num=16&jsoncallback=slideNewsSinaComCnCB&_=1571278271827
        # int(time.time()*1000)

        data = pd.DataFrame(list(self.all_type.find()))
        for lever_1, lever_2, api, page_number in zip(data['lerve_1'], data['lerve_2'], data['api'], data['page_number']):
            self.lever_1 = lever_1
            self.lever_2 = lever_2

            for num in range(page_number):
                urls = '{}&page={}&num=16&jsoncallback=slideNewsSinaComCnCB&_={}'.format(api, num+1, int(time.time()*1000))
                print(lever_1, lever_2, urls)

                # 从 json 文件中 获取item_list
                self.item_list(urls)

                pass
        
        pass


    def item_list(self, urls):
        time.sleep(3)
        json_data = json.loads(self.reg.findall(requests.get(urls, headers=self.headers, timeout=5).text)[0])

        for item in json_data['data']:
            name = item['name']
            urls = item['url']
            self.createtime = item['createtime']
            self.creator = item['creator']

            # 创建目录
            self.name = name.replace(r"\\", '').replace(r"/", '').replace(r":", '').replace(r"*", '').replace(r"?", '？').replace(r"\"", '“').replace(r"<", '《').replace(r">", '》').replace(r"|", '丨')
            self.addr_path = r'D:/图库库库库库/新浪图片/{}/{}/{}'.format(self.lever_1, self.lever_2, self.name)
            self.make_dir()

            # 获取图片链接和文字
            option = ChromeOptions()
            option.add_argument('headless')
            driver = webdriver.Chrome(options=option)
            driver.get(urls)
            html = etree.HTML(driver.page_source)
            driver.quit()

            dl_list = html.xpath('//div[@id="eData"]/dl')  # 图片组
            for k, item in enumerate(dl_list, 1):
                img = item.xpath('./dd[1]/text()')[0]
                content = item.xpath('./dd[5]/text()')[0]

                self.download(k, img, content)

                pass
            print()

            pass


    def download(self, k, img, content):
        try:
            time.sleep(1)
            addr_path = '{}/img-{}.jpg'.format(self.addr_path, k)
            print('正在保存图片....    {}'.format(addr_path))
            resp = requests.get(img).content

            # 保存图片
            with open(addr_path, 'wb') as f:
                f.write(resp)
                pass

            # 保存文字
            with open(r'{}/图片-文字.csv'.format(self.addr_path), 'w+', encoding='utf-8-sig', newline='') as f:
                csvObj = csv.writer(f)
                csvObj.writerow(['img-{}'.format(k), content])
                
                pass

        except Exception as ex:
            print(ex.args)
            print('保存失败...重新尝试....')
            self.download(k, img, content)
        
        pass


    def make_dir(self):
        try:
            print(self.addr_path)
            if os.path.exists(self.addr_path) == False:
                os.makedirs(self.addr_path)
            
            print('目录创建成功!')

        except Exception as ex:
            print('{}  目录创建错误  {}'.format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), ex.args))
            with open('错误.txt', 'a+', encoding='utf-8') as f:
                f.write('{}  目录创建错误  {}'.format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), ex.args))






    pass

if __name__ == '__main__':
    sina_photo = Sina_Photo()
    sina_photo.page_number()
    