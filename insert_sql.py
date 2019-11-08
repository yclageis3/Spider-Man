# -*- coding:utf-8 -*-
# https://blog.csdn.net/weixin_42703149/article/details/85120029
import uuid, pymysql, time
import pandas as pd

# 进程 / 线程
from concurrent.futures import ProcessPoolExecutor

# 装饰器，计时
def timer(func):
    def decor(*args):
        start_time = time.time()
        func(*args)
        end_time = time.time()
        d_time = end_time - start_time
        print('running time : ', d_time)

    return decor

"""
1. 从数据库读取手机号前7位号段
2. 生成0000 - 9999后四位
3. 存入数据库

量级：30e

"""

# 读取号段
@timer
def read_mysql():
    mysql_con = pymysql.connect(
        host='192.168.120.59',
        port=3306,
        user='root',
        passwd='123456',
        db='mobile_number',
        charset='utf8',
    )
    # pandas 读取sql
    df = pd.read_sql('select number, area, type, area_code from mobile_address', con=mysql_con)
    mysql_con.close()
    # 创建进程
    process = ProcessPoolExecutor(max_workers=10)
    db_num = 29  # 数据库编号， 
    for i in range(3000):
        if i % 100 == 0: db_num += 1  # 一张表存1000个号段 1000W条手机号
        for number, area, type, area_code in df.values[i*10:(i+1)*10]: # 一次取十条号段， 循环取3000次
            process.submit(generate_phone_number, number, area, type, area_code, db_num, i)
            pass
    process.shutdown()  # 阻塞主线程
    pass

# 生成后四位
def generate_phone_number(number, area, type, area_code, db_num, iii):
    mysql_con = pymysql.connect(
        host='127.0.0.1',
        port=3306,
        user='root',
        passwd='123456',
        db='number_pool',
        charset='utf8',
    )

    # 批量插入1：将字段 append 入列表
    usersvalues = []
    for i in range(10000):  # 生成号码
        if len(str(i)) == 1: phone = f'{number}000{i}'
        if len(str(i)) == 2: phone = f'{number}00{i}'
        if len(str(i)) == 3: phone = f'{number}0{i}'
        if len(str(i)) == 4: phone = f'{number}{i}'
        usersvalues.append((uuid.uuid4().hex, number, area, type, area_code, phone))
        pass

    cursor = mysql_con.cursor()
    # 批量插入2： 使用 executemany 创建批量sql语句
    """
    execute(sql) : 接受一条语句从而执行
    executemany(templet,args)：能同时执行多条语句，执行同样多的语句可比execute()快很多，强烈建议执行多条语句时使用executemany

    效果：十个进程 百万条数据，逐条插入 耗时91s， 批量插入 耗时15 - 17s， 写入速度提升四倍以上(真实提速还要看本机配置)
    """
    cursor.executemany(f'insert into mobile_phone_number_copy{db_num} (id, number, area, type, area_code, phone) values (%s, %s, %s, %s, %s, %s)',usersvalues)
    print(f"{iii} --> {db_num}")
    mysql_con.commit()  # 一次提交
    mysql_con.close()
    pass

if __name__ == "__main__":
    read_mysql()


