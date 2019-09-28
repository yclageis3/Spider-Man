import urllib
import requests
from lxml import etree
import time
import os
import pandas as pd
import pymysql
import datetime
import csv


class cncn_Spider:

    def __init__(self, path):
        self.path = path
        self.sheng_name = ''
        self.shi_name = ''
        self.file_path = ''
        self.file_name = ''
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
            'Referer': 'https://www.cncn.com',
        }
        self.conn = pymysql.connect(
            host='192.168.120.58',
            db='cncn_hn',
            port=3306,
            user='root',
            passwd='123456',
            charset='utf8',
            use_unicode=False
        )
        self.cursor = self.conn.cursor()

        pass

    def make_dir(self, addr_path):
        if os.path.exists(addr_path) == False:
            os.makedirs(addr_path)
            pass

        pass

    # 结果：返回省级url
    def sheng_(self, url):
        time.sleep(1)
        resp = requests.get(url, headers=self.headers)
        html = etree.HTML(resp.content)

        addr_list = html.xpath('//div[@class="change_box"]/dl[1]//a/text()')
        url_list = html.xpath('//div[@class="change_box"]/dl[1]//a/@href')

        for addr, sheng_url in zip(addr_list[1:-1][15:16], url_list[1:-1][15:16]):
            self.sheng_name = addr
            self.shi_('https://www.cncn.com{}'.format(sheng_url))

        pass

    # 结果：返回市级url
    def shi_(self, sheng_url):
        time.sleep(1)
        resp = requests.get(sheng_url, headers=self.headers)
        html = etree.HTML(resp.content)

        dl_list = html.xpath('//div[@class="change_box"]/dl')
        if len(dl_list) == 5:  # 不是直辖市
            addr_list = html.xpath('//div[@class="change_box"]/dl[2]/dd/a/text()')
            url_list = html.xpath('//div[@class="change_box"]/dl[2]/dd/a/@href')

            for addr, shi_url in zip(addr_list[1:][:1], url_list[1:][:1]):
                self.shi_name = addr
                self.start_1('https://www.cncn.com{}'.format(shi_url))
        else:
            self.start_1(sheng_url)

        pass

    # 结果：获取页数，拼接url进一步获取单个景区
    def start_1(self, url):
        time.sleep(1)
        
        response = requests.get(url, headers=self.headers)
        html = etree.HTML(response.content)

        # 获取最大页数
        max_page = html.xpath('//div[@class="toolbar"]/ul/li/text()')
        if max_page:
            max_page = max_page[0].split('/')[-1]
        else:
            max_page = 1

        # 根据页数拼接url
        new_url = ''
        if max_page != 1:
            for page in range(int(max_page)):
                new_url = '{}/1s{}.htm'.format(url, page + 1)
                self.start_2(new_url)
                new_url = ''
                pass
        else:
            new_url = url
            self.start_2(new_url)
        
            
    # 结果：获取单个景区名、星级、url，进一步获取详情信息
    def start_2(self, url):
        time.sleep(1)
        
        response = requests.get(url, headers=self.headers)
        html = etree.HTML(response.content)
        
        # //div[2]/div[1]/div/div/a/strong
        info_list = html.xpath(r'//div[@class="list_top"]')

        for item in info_list:
            url = 'https://www.cncn.com'+ self.return_str(item.xpath(r'./div/div[1]/a/@href'))
            name = self.return_str(item.xpath(r'./div/div[1]/a/strong/text()'))
            star = self.return_0(item.xpath(r'./div/div[1]/b/text()'))

            # 拼接文件名，星级 + 景区名
            if star:
                self.file_name = '{}A · {}'.format(len(star), name)
            else:
                self.file_name = name
            # 拼接目录
            if len(html.xpath('//div[@class="change_box"]/dl')) == 5:
                self.file_path = r'{}\{}\{}\{}'.format(self.path, self.sheng_name, self.shi_name, name)
            else:
                self.file_path = r'{}\{}\{}'.format(self.path, self.sheng_name, name)
            
            # 创建目录
            self.make_dir(self.file_path)
            
            self.start_3(url)
        
        pass

    # 结果：获取到景区详情信息，并保存
    def start_3(self, url):
        resp = requests.get(url)
        html = etree.HTML(resp.content)

        img_list1 = html.xpath('//ul[@id="tFocus-pic"]//img/@src')
        self.download_imgs1(img_list1=img_list1, file_path=self.file_path)  # 下载图片
        imgs1 = self.return_img(img_list1)  # 以逗号间隔，拼接图片连接
        name = html.xpath('//h1[@class="media-title"]/text()')[0]
        address = html.xpath('//span[@class="address"]/text()')[0]
        opentime = self.return_0(html.xpath('//span[@class="j-limit"]/text()'))
        ticket = self.return_str(html.xpath('//div[@id="J-MediaLabel"][1]/text()')).strip()
        content1 = self.return_str(html.xpath('//div[@id="J-Jdjj"]//text()'))
        content2 = self.return_str(html.xpath('//div[@class="produce_con mt20"]/text()'))[:-2]

        # print('景区名称：{}'.format(name))
        # print('景区图片：{}'.format(imgs1))
        # print('景区地点：{}'.format(address))
        # print('开放时间：{}'.format(opentime))
        # print('门票信息：{}'.format(ticket))
        # print('景点简介：{}'.format(content1))
        # print('交通指南：{}'.format(content2))
        self.download_csv(name, imgs1, address, opentime, ticket.strip(), content1, content2)

        pass

    def download_imgs1(self, img_list1, file_path):
        for num, url in enumerate(img_list1, 1):
            response = requests.get('https:' + url)

            with open(file_path + r'\样{}.jpg'.format(num), 'wb')as f:
                f.write(response.content)
                pass

        pass

    def download_csv(self, name, imgs1, address, opentime, ticket, content1, content2):
        try:
            sql = "insert into china(name, imgs1, address, opentime, ticket, content1, content2) values ('%s','%s','%s','%s','%s','%s','%s')" % (name, imgs1, address, opentime, ticket, content1, content2)
            # print(sql)
            self.cursor.execute(sql)
            self.conn.commit()
            # print('数据插入成功')
        except Exception as ex:
            print('数据插入失败')
            print(ex.args)

        with open(r'{}\{}.csv'.format(self.file_path, self.file_name), 'w+', encoding='utf-8-sig', newline='') as f:
            csvObj = csv.writer(f)
            csvObj.writerow(
                ['景区名称', '景区图片', '景区地点', '开放时间', '门票信息', '景点简介', '交通指南'])
            csvObj.writerow([name, imgs1, address, opentime, ticket, content1, content2])
            print('【{}】景区数据已保存'.format(self.file_name))

        pass
      

    def return_str(self, str_list):
        str1 = ''
        for i in str_list:
            str1 += i.strip()
            pass
        return str1

    def return_img(self, imgs):
        a = ''
        if imgs:
            if len(imgs) == 1:
                a = 'https:' + imgs[0]
            else:
                for k, i in enumerate(imgs, 1):
                    if k != len(imgs):
                        a += 'https:' + i + '，'
                    else:
                        a += 'https:' + i
        return a

    def return_0(self, item):
        if item:
            return item[0]
        else:
            return ''
        pass

    pass


if __name__ == "__main__":
    path = r'E:\欣欣旅游网'  # 数据保存位置

    cncn = cncn_Spider(path=path)

    cncn.sheng_(r'https://www.cncn.com/piao/all/#?')

    pass