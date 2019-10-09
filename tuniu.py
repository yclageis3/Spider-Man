#-*- coding:utf-8 -*-

# 请求、解析 库
import requests
from selenium import webdriver
from bs4 import BeautifulSoup
from lxml import etree
import csv
import re
reg = re.compile(r'\d+')

# sql 库
import pymysql
from pymongo import MongoClient

# url 编码
import urllib

# 删除文件夹库
import shutil

import time
import random
import os

class Tuniu_Spider:

    def __init__(self):
        # webdriver
        self.driver = webdriver.ChromeOptions()
        self.driver.add_argument('headless')
        self.driver = webdriver.Chrome(chrome_options=self.driver)

        # 时间
        self.now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        self.int_time = int(time.time())

        # 请求头
        self.headers = {
            "Cookie": "tuniu_partner=MTE2OSwwLCwwN2FhZTE4ZWQxMTAxMTI5MWRkNjNjMjkyZWI0NTJkZQ%3D%3D; p_phone_400=4007-999-999; p_phone_level=0; p_global_phone=%2B0086-25-8685-9999; _tact=Yzk4OWMzMzctODg3YS1lMThiLTEzMzMtYjgxM2FkOWRiNmJi; _tacau=MCxhODY2ODU0Yy1iNDQzLTMyZjEtY2ExZS0xNThiYWQ1YzBiMmMs; _tacz2=taccsr%3D%28direct%29%7Ctacccn%3D%28none%29%7Ctaccmd%3D%28none%29%7Ctaccct%3D%28none%29%7Ctaccrt%3D%28none%29; _tacc=1; PageSwitch=1%2C213612736; _ga=GA1.2.671788455.1570500807; _gid=GA1.2.1804023345.1570500807; OLBSESSID=9no4k11ijv4492fhb3oiktjkm1; __utma=1.671788455.1570500807.1570500837.1570500837.1; __utmc=1; __utmz=1.1570500837.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); isHaveShowPriceTips=1; Hm_lvt_51d49a7cda10d5dd86537755f081cc02=1570501041; tuniuuser_citycode=MTIwMg==; tuniuuser_ip_citycode=MTIwMg==; fp_ver=4.7.3; BSFIT_EXPIRATION=1571757620404; BSFIT_OkLJUJ=FHMzqCKZE7CTi2Rqxa3Z1Xfw3FWLjEsL; BSFIT_DEVICEID=sjoC1pdqpSPXJwgDwwE21fr5qalVtdjyDbBFuOoLGhjyzD3obtwYTF9BHdZIyoqgL9rj315fYwKep6LXPoRzmF37DwfgWiQ-aODd-PutbzaHJy9FD9yb4Ij34KMkqfkCI2_EDqGVcgt7Zr0aUx5mMgEgejGQ9ifs; pt_s_5a1137d9=vt=1570501975598&cad=; pt_5a1137d9=uid=vbX-y7E9/2wnS-gxe8STmw&nid=0&vid=dnyUsS8-7YA5M4/46UyCiw&vn=2&pvn=1&sact=1570502115382&to_flag=0&pl=fFuFLuOqf0ct-4bqwLCggA*pt*1570501975598; _pzfxuvpc=1570500806346%7C1227594061758633702%7C6%7C1570503472824%7C2%7C5696982396847887435%7C9903661103129827196; __xsptplus352=352.1.1570500829.1570503479.9%234%7C%7C%7C%7C%7C%23%23HyZyzVH8JrIeJ4fSXF7DhkQaaGCi8Whk%23; tuniu_zeus=M18zXzFfMV8xXzI6Omh0dHA6Ly9tZW5waWFvLnR1bml1LmNvbS86OjIwMTktMTAtMDggMTA6NTg6MDQ%3D; tuniu_searched=a%3A5%3A%7Bi%3A0%3Ba%3A2%3A%7Bs%3A7%3A%22keyword%22%3Bs%3A6%3A%22%E6%B4%9B%E9%98%B3%22%3Bs%3A4%3A%22link%22%3Bs%3A48%3A%22%2F%2Fs.tuniu.com%2Fsearch_complex%2Fticket-zz-0-%E6%B4%9B%E9%98%B3%2F%22%3B%7Di%3A1%3Ba%3A2%3A%7Bs%3A7%3A%22keyword%22%3Bs%3A6%3A%22%E6%B5%8E%E6%BA%90%22%3Bs%3A4%3A%22link%22%3Bs%3A48%3A%22%2F%2Fs.tuniu.com%2Fsearch_complex%2Fticket-zz-0-%E6%B5%8E%E6%BA%90%2F%22%3B%7Di%3A2%3Ba%3A2%3A%7Bs%3A7%3A%22keyword%22%3Bs%3A9%3A%22%E6%B5%8E%E6%BA%90%E5%B8%82%22%3Bs%3A4%3A%22link%22%3Bs%3A51%3A%22http%3A%2F%2Fwww.tuniu.com%2Fg1207%2Fwhole-zz-0%2Flist-h0-j0_0%2F%22%3B%7Di%3A3%3Ba%3A2%3A%7Bs%3A7%3A%22keyword%22%3Bs%3A6%3A%22%E5%91%A8%E5%8F%A3%22%3Bs%3A4%3A%22link%22%3Bs%3A51%3A%22http%3A%2F%2Fwww.tuniu.com%2Fg1219%2Fwhole-zz-0%2Flist-h0-j0_0%2F%22%3B%7Di%3A4%3Ba%3A2%3A%7Bs%3A7%3A%22keyword%22%3Bs%3A9%3A%22%E9%A9%BB%E9%A9%AC%E5%BA%97%22%3Bs%3A4%3A%22link%22%3Bs%3A51%3A%22%2F%2Fs.tuniu.com%2Fsearch_complex%2Fticket-zz-0-%E9%A9%BB%E9%A9%AC%E5%BA%97%2F%22%3B%7D%7D; _taca=1570500802836.1570500802836.1570505934997.2; _tacb=YmRkNzVlYzctZGI5ZS02NzI3LTZhMzItM2NjZDIwZThkYTRj; Hm_lpvt_51d49a7cda10d5dd86537755f081cc02={}".format(self.int_time),
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36",
        }
        
        # mongo 连接
        self.conn = MongoClient('192.168.120.51', 27017)  # 创建MongoDB连接
        self.tuniu = self.conn.tuniu  # 创建数据库连接
        self.henan = self.tuniu.henan

        # 地区字典
        self.area = {
            '北京':['北京'],
            '上海':['上海'],
            '深圳':['深圳'],
            '天津':['天津'],
            '重庆':['重庆'],
            '澳门':['澳门'],
            '香港':['香港'],
            '海南':['海口','三亚'],
            '台湾':['台湾','台北','高雄','基隆','台中','台南','新竹','嘉义'],
            '河北':['唐山','邯郸','邢台','保定','承德','沧州','廊坊','衡水','石家庄','秦皇岛','张家口'],
            '山西':['太原','大同','阳泉','长治','晋城','朔州','晋中','运城','忻州','临汾','吕梁'],
            '山东':['济南','青岛','淄博','枣庄','东营','烟台','潍坊','济宁','泰安','威海','日照','莱芜','临沂','德州','聊城','滨州','荷泽','菏泽'],
            '江苏':['南京','无锡','徐州','常州','苏州','南通','淮安','盐城','扬州','镇江','泰州','宿迁','连云港'],
            '浙江':['杭州','宁波','温州','嘉兴','湖州','绍兴','金华','衢州','舟山','台州','丽水'],
            '安徽':['合肥','芜湖','蚌埠','淮南','淮北','铜陵','安庆','黄山','滁州','阜阳','宿州','巢湖','六安','亳州','池州','宣城','马鞍山'],
            '福建':['福州','厦门','莆田','三明','泉州','漳州','南平','龙岩','宁德'],
            '江西':['南昌','萍乡','新余','九江','鹰潭','赣州','吉安','宜春','抚州','上饶','景德镇'],
            '河南':['郑州','开封','洛阳','焦作','鹤壁','新乡','安阳','濮阳','许昌','漯河','南阳','商丘','信阳','周口','驻马店','济源','平顶山','三门峡'],
            '湖北':['武汉','黄石','襄樊','十堰','荆州','宜昌','荆门','鄂州','孝感','黄冈','咸宁','随州','恩施','仙桃','天门','潜江'],
            '湖南':['长沙','株洲','湘潭','衡阳','邵阳','岳阳','常德','益阳','郴州','永州','怀化','娄底','吉首','张家界'],
            '广东':['广州','深圳','珠海','汕头','韶关','佛山','江门','湛江','茂名','肇庆','惠州','梅州','汕尾','河源','阳江','清远','东莞','中山','潮州','揭阳','云浮'],
            '广西':['南宁','柳州','桂林','梧州','北海','钦州','贵港','玉林','百色','贺州','河池','来宾','崇左','防城港'],
            '四川':['成都','自贡','泸州','德阳','绵阳','广元','遂宁','内江','乐山','南充','宜宾','广安','达州','眉山','雅安','巴中','资阳','西昌','攀枝花'],
            '贵州':['贵阳','遵义','安顺','铜仁','毕节','兴义','凯里','都匀','六盘水','黔西南布依族苗族自治州','黔东南苗族侗族自治州','黔南布依族苗族自治州'],
            '云南':['昆明','曲靖','玉溪','保山','昭通','丽江','思茅','临沧','景洪','楚雄','大理','潞西'],
            '陕西':['西安','铜川','宝鸡','咸阳','渭南','延安','汉中','榆林','安康','商洛'],
            '甘肃':['兰州','金昌','白银','天水','武威','张掖','平凉','酒泉','庆阳','定西','陇南','临夏','合作','嘉峪关'],
            '辽宁':['沈阳','大连','鞍山','抚顺','本溪','丹东','锦州','营口','盘锦','阜新','辽阳','铁岭','朝阳','葫芦岛'],
            '吉林':['长春','吉林','四平','辽源','通化','白山','松原','白城','延吉'],
            '黑龙江':['鹤岗','鸡西','大庆','伊春','黑河','绥化','双鸭山','牡丹江','佳木斯','七台河''哈尔滨','齐齐哈尔',],
            '青海':['西宁','德令哈','格尔木'],
            '宁夏':['银川','吴忠','固原','中卫','石嘴山'],
            '西藏':['拉萨','日喀则'],
            '新疆':['哈密','和田','喀什','昌吉','博乐','伊宁','塔城','吐鲁番','阿图什','库尔勒','五家渠','阿克苏','阿勒泰','石河子','阿拉尔','乌鲁木齐','克拉玛依','图木舒克'],
            '内蒙古':['包头','乌海','赤峰','通辽','鄂尔多斯','呼伦贝尔','巴彦淖尔','乌兰察布','兴安盟','呼和浩特','锡林郭勒盟','阿拉善盟','巴彦淖尔盟','乌兰察布盟'],
        }

        self.sheng_name = ''
        self.shi_name = ''
        self.jq_name = ''
        self.addr_path = ''

        pass


    def shi_info(self):
        for sheng_name in self.area:  # 检阅省级地区
            self.sheng_name = sheng_name
            if self.sheng_name not in ['河南']:  # 获取指定地区的景点信息
                continue
            for shi_name in self.area[sheng_name]:
                self.shi_name = shi_name
                shi_url = r'http://s.tuniu.com/search_complex/ticket-zz-0-{}/'.format(urllib.parse.quote(self.shi_name))

                resp = requests.get(shi_url, headers=self.headers, verify=False)
                time.sleep(random.randint(5, 15))
                html = etree.HTML(resp.text)

                if html.xpath('//div[@class="searchw800 mt_10 mb_10"]'):  # 没有地区的景点信息
                    print('[{}] 本站没有该地区的景点信息!'.format(self.shi_name))
                    pass
                else:
                    page_num = self.max_num(html.xpath('//div[@class="page-bottom"]/a/text()'))  # 获取最大页数
                    for num in range(page_num):
                        shi_url_2 = r'{}{}'.format(shi_url, num+1)
                        self.jq_list(shi_url=shi_url_2)
                        pass
                pass
            pass
        pass


    def jq_list(self, shi_url):
        resp = requests.get(shi_url, headers=self.headers, verify=False)
        html = etree.HTML(resp.text)

        wz_title = html.xpath('//ul[@class="thebox clearfix menpiaobox"]/li//p[@class="title ticket"]/span/text()')
        wz_url = html.xpath('//ul[@class="thebox clearfix menpiaobox"]/li/div/a/@href')

        for title, url in zip(wz_title, wz_url):
            self.jq_name = title
            jq_url = r'http://www.tuniu.com/menpiao/{}#/index'.format(reg.findall(url)[0])

            self.jq_info(jq_url=jq_url)

            pass

        pass


    def jq_info(self, jq_url):
        resp = requests.get(jq_url, headers=self.headers, verify=False)
        html = etree.HTML(resp.text)

        div_code = ''
        if html.xpath('//div[@class="text"]/@title'):
            address = html.xpath('//div[@class="text"]/@title')[0]
            div_code += f'{self.jq_name}</br>地址:{address}</br>'

        self.addr_path = r'//192.168.100.173/移动库/旅游景区/途牛/{}/{}/{}/'.format(self.sheng_name, self.shi_name, self.jq_name)
        self.make_dir(self.addr_path)
        print('目录创建成功!')

        yang_dict = self.yangtu(html.xpath('//img[@class="image"]/@src'))
        xiang_dict = self.xiangtu(html.xpath('//div[@class="scenicIntroduction clearfix"]//img/@data-src'))
        div_code += self.div_code(jq_url)
        # print(div_code)

        if self.insert_MongoDB(yang_dict=yang_dict, xiang_dict=xiang_dict, div_code=div_code):
            print(f'{self.now}  插入Mongo成功\n')
        else:
            if not os.path.isdir(self.addr_path):
                shutil.rmtree(self.addr_path)
                print('插入Mongd失败,目录删除成功!')
        pass


    def max_num(self, num_list):
        if len(num_list) > 2:
            return int(max(num_list[:-1]))
        else:
            return int(max(num_list))
        pass


    def div_code(self, url):
        time.sleep(1)
        soup = BeautifulSoup(requests.get(url=url).text)
        # 图文 html源码
        wz_code = ''

        try:
            # 景区须知
            if soup.find_all('div', class_='scheduledNote clearfix'):
                for item in soup.find_all('div', class_='scheduledNote clearfix'):
                    wz_code += str(item)
                    pass

            # 图文介绍
            if soup.find_all('div', class_='scenicIntroduction clearfix'):
                for item in soup.find('div', class_='scenicIntroduction clearfix').select('.content'):
                    wz_code += '</br><h1>景区介绍</h1></br>{}'.format(str(item).replace('data-src', 'src'))
                    pass

            # 交通路线
            if soup.find_all('div', class_='scenicAddress'):
                for item in soup.find_all('div', class_='scenicAddress'):
                    wz_code += str(item)
                    pass
                pass
            pass

        except Exception as ex:
            print(ex.args)
            with open('错误.txt', 'a+', encoding='utf-8') as f:
                f.write('{}  获取div源码错误  {}\n'.format(self.now, ex.args))

        return wz_code


    def insert_MongoDB(self, yang_dict, xiang_dict, div_code):
        try:
            self.henan.insert({
                '景区名称': self.jq_name,
                '样图位置': yang_dict,
                '详图位置': xiang_dict,
                '图文源码': div_code,
            })

            self.down_csv(yangtu=yang_dict, xiangtu=xiang_dict, div_code=div_code)

            return True
        except Exception as ex:
            print(ex.args)
            with open('错误.txt', 'a+', encoding='utf-8') as f:
                f.write('{}  插入mongo错误  {}'.format(self.now, ex.args))
            return False


    def down_csv(self, yangtu, xiangtu, div_code):
        try:

            file_name = f'{self.addr_path}/{self.jq_name}.csv'
            with open(file_name, 'w+', encoding='utf-8-sig', newline='') as f:
                csvObj = csv.writer(f)
                csvObj.writerow(
                    ['景区名称', '样图位置', '详图位置', '图文代码'])
                csvObj.writerow([self.jq_name, str(yangtu), str(xiangtu), div_code])
                print('{} {}【{}.csv】已写入'.format(self.sheng_name, self.shi_name, self.jq_name))

        except Exception as ex:
            self.down_csv_tf = False
            print('{}  写入csv错误  {}\n'.format(self.now, ex.args))
            with open('错误.txt', 'a+', encoding='utf-8') as f:
                f.write('{}  写入csv错误  {}\n'.format(self.now, ex.args))

            pass

        pass


    def yangtu(self, img_list: list) -> dict:
        local_path = {}
        if img_list:
            try:
                for k, v in enumerate(img_list, 1):
                    time.sleep(random.randint(1, 3))
                    resp = requests.get(v).content
                    file_name = self.addr_path + r'样{}.jpg'.format(k)
                    with open(file_name, 'wb+') as f:
                        f.write(resp)
                        local_path['样图{}'.format(k)] = [v, (os.path.join(os.getcwd(), file_name))]  
                print(f'{self.now}  样图保存ok啦')
            except Exception as ex:
                print('{}  保存图片错误  {}'.format(self.now, ex.args))
                with open('错误.txt', 'a+', encoding='utf-8') as f:
                    f.write('{}  保存图片错误  {}'.format(self.now, ex.args))

        return local_path


    def xiangtu(self, img_list: list) -> dict:
        local_path = {}
        if img_list:
            try:
                for k, v in enumerate(img_list, 1):
                    time.sleep(random.randint(1, 3))
                    resp = requests.get(v).content
                    file_name = self.addr_path + r'详{}.jpg'.format(k)
                    with open(file_name, 'wb+') as f:
                        f.write(resp)
                        local_path['祥图{}'.format(k)] = [v, (os.path.join(os.getcwd(), file_name))]
                print(f'{self.now}  详情图保存OK啦')
            except Exception as ex:
                print('{}  保存图片错误  {}'.format(self.now, ex.args))
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
    tuniu = Tuniu_Spider()
    tuniu.shi_info()
