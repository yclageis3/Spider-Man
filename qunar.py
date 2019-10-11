import requests
import time
from lxml import etree
import urllib
import os
import pymysql
import csv
import random
from bs4 import BeautifulSoup
from selenium import webdriver
from pymongo import MongoClient


class Qunar:

    def __init__(self, path):
        self.driver = webdriver.ChromeOptions()
        self.driver.add_argument('headless')
        self.driver = webdriver.Chrome( chrome_options=self.driver)

        self.path = path  # 总目录
        self.sheng_name = ''
        self.shi_name = ''
        self.addr_path = ''
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.75 Safari/537.36",
            "Referer": "https://piao.qunar.com/"
        }
        
        self.now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        # mongo 连接
        self.conn = MongoClient('192.168.120.51', 27017)  # 创建MongoDB连接
        self.qunar = self.conn.qunar  # 创建数据库连接
        self.henan = self.qunar.henan


        pass

    def city_list(self, qunar_url):
        resp = requests.get(qunar_url, headers=self.headers)
        html = etree.HTML(resp.content)

        num = 1
        item_list = html.xpath('//ul[@class="mp-city-list mp-city-list-long"]')[1:]
        for item in item_list:
            a_list = item.xpath('//div[@class="mp-city-area"]/div[1]/ul/li//text()')
            b_list = item.xpath('//div[@class="mp-city-area"]/div[@class="mp-city-list-container mp-privince-city mp-hide"]/ul')
            for a, b in zip(a_list[10:11], b_list[10:11]):  # 切片 ----------------------- 河南
                self.sheng_name = a
                b_name = b.xpath('./li/a/text()')
                for name in b_name:  # 城市切片 ----------------------- 
                    self.shi_name = name
                    url = 'https://piao.qunar.com/ticket/list.htm?keyword={}&region=&from=mpl_search_suggest'.format(urllib.parse.quote(name))
                    
                    self.page_info(url)

            num += 1

        pass

    def page_info(self, url):
        resp = requests.get(url)
        html = etree.HTML(resp.text)

        for x in html.xpath('//div[@class="show loading"]/a/@href'):
            time.sleep(random.randint(2, 4))
            new_url ='https://piao.qunar.com'+x
            self.content_urls(new_url)
            
        if html.xpath('//div[@id="pager-container"]/div/a/text()')[-1]=='下一页':
            next_num = html.xpath('//div[@id="pager-container"]/div/a/@href')[-1]
            # print('下一页')
            if next_num:
                self.page_info('https://piao.qunar.com'+next_num)

        pass

    def content_urls(self,url):
        html1 = requests.get(url)
        html = etree.HTML(html1.text)
        content_list = []
        # 标题
        title = ''
        if html.xpath('//div[@class="mp-description-detail"]/div/span/text()'):
            title = html.xpath('//div[@class="mp-description-detail"]/div/span/text()')[0]
        address = ''
        if html.xpath('//div[@class="mp-description-detail"]/div[3]/span[3]/text()'):
            address = html.xpath('//div[@class="mp-description-detail"]/div[3]/span[3]/text()')[0]
        content_list.append(title)
        content_list.append(address)
        if self.sheng_name == self.shi_name:
            self.addr_path = r'{}\{}\{}'.format(self.path, self.sheng_name, title)
        else:
            self.addr_path = r'{}\{}\{}\{}'.format(self.path, self.sheng_name, self.shi_name, title)
        
        self.make_dir(self.addr_path)
        # print('标题 >>')
        # print(title)
        # 景区图片
        pict = ''
        if html.xpath('//div[@id="slide"]/div/div/img/@src'):
            for a, y in enumerate(html.xpath('//div[@id="slide"]/div/div/img/@src'), 1):
                pict += y + '\n'
                file_name ='样' + str(a) + '.jpg'
                self.down_img(y,file_name,title)
        content_list.append(pict)
        # print('景区图片 >>')
        # print(pict)
        # 景区概述
        intro = html.xpath('//div[@class="mp-charact-intro"]/div/p/text()')
        if intro:
            intro = intro[0]
        else:
            intro = ''
        content_list.append(intro)
        # print('景区概述 >>')
        # print(intro)
        # 开放时间
        open_time = ''
        if html.xpath('//div[@id="mp-charact"]/div[1]/div/div/div/p/text()'):
            for x in html.xpath('//div[@id="mp-charact"]/div[1]/div/div/div/p/text()'):
                open_time += x.strip() + '\t'
        content_list.append(open_time)
        # print('开放时间 >>')
        # print(open_time.replace('\t', ''))
        # 详情图片
        content_all = ''
        b =0
        for x, y, z in zip(html.xpath('//div[@class="mp-charact-event"]/div/img/@src'),
                           html.xpath('//div[@class="mp-charact-event"]/div/div/h3/text()'),
                           html.xpath('//div[@class="mp-charact-event"]/div/div/p/text()')):
            file_name ='详' + str(b) + '.jpg'
            self.down_img(x,file_name,title)
            content_all += x + '\n' + y + '\n' + z + '\n'
            b += 1
            # print('详情图片 >>' + x)
            # print('详情标题 >>' + y)
            # print('详情文字 >>' + z)
        content_list.append(content_all)
        # 入园公告
        notice_text = ''
        if html.xpath('//div[@class="mp-charact-littletips"]/div[@class="mp-littletips"]'):
            for x in html.xpath('//div[@class="mp-charact-littletips"]/div[@class="mp-littletips"]'):
                type_one_title = x.xpath('./h2/text()')[0]
                notice_text += type_one_title + '\n'
                # print(type_one_title + '\n')
                type_two_title = x.xpath('./div[@class="mp-littletips-item"]/div[@class="mp-littletips-itemtitle"]/text()')
                type_content = x.xpath('./div[@class="mp-littletips-item"]/div/p/text()')
                for y, z in zip(type_two_title, type_content):
                    notice_text += y + '\n' + z + '\n'
                    # print(y + '\n')
                    # print(z + '\n')
        content_list.append(notice_text)
        # 机场与车站
        if html.xpath('//div[@class="mp-traffic-transfer"]'):
            # print('线路 >>')
            bus_content = ''
            if html.xpath('//div[@class="mp-traffic-transfer"]/div[1]/text()'):
                bus_content += html.xpath('//div[@class="mp-traffic-transfer"]/div[1]/text()')[0] + '\n'
            else:
                bus_content += '自驾游线路暂无' + '\n'
            for x in html.xpath('//div[@class="mp-traffic-transfer"]/div[2]/p/text()'):
                bus_content += x + '\n'
            if html.xpath('//div[@class="mp-traffic-transfer"]/div[3]/text()') == []:
                pass
            else:
                if html.xpath('//div[@class="mp-traffic-transfer"]/div[3]/text()')[0]:
                    bus_content += html.xpath('//div[@class="mp-traffic-transfer"]/div[3]/text()')[0] + '\n'
                else:
                    bus_content += '公交线路暂无' + '\n'
                for x in html.xpath('//div[@class="mp-traffic-transfer"]/div[4]/p/text()'):
                    bus_content += x + '\n'
            content_list.append(bus_content)

        # content_list.append(self.div_code(url))
        self.download_mongo(content_list)

        pass


    def div_code(self, url):
        self.driver.get(url)
        time.sleep(1)
        soup = BeautifulSoup(self.driver.page_source)
        # 图文 html源码
        wz_code = ''

        try:
            # 图文介绍
            if soup.find_all('div', id='mp-charact'):
                for item in soup.find_all('div', id='mp-charact'):
                    wz_code += str(item)
                    pass

            # 交通路线
            if item in soup.find_all('div', class_='mp-traffic'):
                for item in soup.find_all('div', class_='mp-traffic'):
                    wz_code += str(item)
                    pass
                pass
            pass

        except Exception as ex:
            print(ex.args)
            with open('错误.txt', 'a+', encoding='utf-8') as f:
                f.write('{}  获取div源码错误  {}'.format(self.now, ex.args))

        return wz_code


    # def downlond(self, content_list):
    #     # print(content_list)
    #     try:
    #         sql = "insert into china(name, address, imgs, info, opentime, content1, content2) values ('%s','%s','%s','%s','%s','%s','%s')" % (content_list[0], content_list[1], content_list[2], content_list[3], content_list[4], content_list[5], content_list[6])
    #         # print(sql)
    #         self.cursor.execute(sql)
    #         self.connect.commit()
    #         # print('数据插入成功')
    #     except Exception as ex:
    #         print('数据插入失败')
    #         print(ex.args)


    #     with open(r'{}\{}.csv'.format(self.addr_path, content_list[0]),'a+', encoding='utf-8-sig', newline='') as f:
    #         csvObj = csv.writer(f)
    #         csvObj.writerow(
    #             ['景区名称', '景区地点', '景区图片', '景区概述', '开放时间', '入园公告', '出行路线'])
    #         csvObj.writerow(content_list)
    #         print('{} {}【{}】已写入'.format(self.sheng_name, self.shi_name, str(content_list[0])))
        
    #     pass


    def download_mongo(self, content_list: list):
        try:
            self.henan.insert({
                '景区名称': content_list[0],
                '景区地点': content_list[1],
                '景区图片': content_list[2],
                '内容排版': content_list[7],
            })

            print('插入Mongo成功\n')
            return True
        except Exception as ex:
            print(ex.args)
            with open('错误.txt', 'a+', encoding='utf-8') as f:
                f.write('{}  插入mongo错误  {}'.format(self.now, ex.args))
            return False


        with open(r'{}\{}.csv'.format(self.addr_path, content_list[0]),'a+', encoding='utf-8-sig', newline='') as f:
            csvObj = csv.writer(f)
            csvObj.writerow(
                ['景区名称', '景区地点', '景区图片', '景区概述', '开放时间', '入园公告', '出行路线'])
            csvObj.writerow(content_list)
            print('{} {}【{}】已写入'.format(self.sheng_name, self.shi_name, str(content_list[0])))
        
        pass


    def down_img(self, url,file_name,title):
        # 3.图片下载,图片文件名定义
        # print(url)
        cont = requests.get(url, timeout=20).content
        # .content得到的是二进制数据  图片都是二进制数据存储的
        # print('正在抓取图片:' + file_name)
        # 4.图片保存
        with open(r'{}\{}'.format(self.addr_path, file_name), "wb") as f:
            # 写二进制数据
            f.write(cont)


    def make_dir(self, addr_path):
        if os.path.exists(addr_path) == False:
            os.makedirs(addr_path)
            pass

        pass


if __name__ == "__main__":
    path = r'//192.168.100.173/移动库/旅游景区/去哪儿'
    qunar_url = r'https://piao.qunar.com'

    qunar = Qunar(path=path)
    qunar.city_list(qunar_url=qunar_url)

    pass
