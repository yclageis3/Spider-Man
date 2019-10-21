import time

import redis
from pymongo import MongoClient


# redis 连接池
pool = redis.ConnectionPool(host="192.168.120.51", port=6379, decode_responses=True)
r = redis.Redis(connection_pool=pool)


# mongo 连接
conn = MongoClient('192.168.120.51', 27017)  # 创建MongoDB连接
tt = conn.tt  # 创建数据库连接
tt_type = tt.guoji  # ---------------------- 更换类别  拼音
tt_cf = tt_type.guoji_cf  # ------------------ 更换类别  拼音


# 消费者
def users():
    
    length = r.llen("news_world")  # ------------------ 更换类别
    while length > 0:
        length=r.llen("news_world")  # ------------------ 更换类别
        print(length)
        tt_id = r.lpop("news_world")  # ------------------ 更换类别

        # 判断 mongo 中是否存在 tt_id
        if tt_type.find({"文章id":tt_id}).count() == 0:
            tt_type.insert({
                '文章id': tt_id
            })

            print(tt_id, '已插入mongo....')
        else:
            if tt_id == None:
                continue
            tt_cf.insert({
                '文章id': tt_id
            })
            print('重复值:{}'.format(tt_id))
            

    else:
        print('无值..请稍等....')
        time.sleep(60)
        users()

# 写入 mongo


if __name__ == "__main__":
    users()
