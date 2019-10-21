from selenium.webdriver import Chrome
from selenium.webdriver import ChromeOptions

from lxml import etree

import random
import time

import redis


# redis 连接池
pool = redis.ConnectionPool(host="192.168.120.51", port=6379,max_connections=1024)
r = redis.Redis(connection_pool=pool)

# webdriver
driver = ChromeOptions()
driver.add_argument('headless')
driver = Chrome( chrome_options=driver)

# 科技
def get_id():
    driver.get(r'https://www.toutiao.com/ch/news_world/')  # ---------------- 更换type
    time.sleep(random.randint(3, 5))

    html = etree.HTML(driver.page_source)
    id_list = html.xpath('//div[@class="wcommonFeed"]//li/@group_id')[:-1]

    product(id_list)
    
    pass

# 写入redis
def product(id_list):
    
    length=r.llen("news_world")  # ----------------------- 更换type
    print(length)
    if length>10000:
        print("长度过大睡一会")
        time.sleep(random.randint(1, 3))
        product(id_list)
    else:
        #生产者
        for i in id_list:
            r.lpush("news_world", str(i))  # ------------------------------- 更换type
            print("{} 已插入....".format(str(i)))
        # time.sleep(5)

if __name__ == "__main__":
    for i in range(50000):
        get_id()
