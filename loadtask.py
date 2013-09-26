#!/usr/bin/python2.7
#-*- coding=utf-8 -*-

# Copy Rights (c) Beijing TigerKnows Technology Co., Ltd.

"""用于加载开始任务模块
"""

__authors__ = ['"wuyadong" <wuyadong@tigerknows.com>']

import os
from tornado.httpclient import HTTPRequest
from tornado.options import options, define
from core.datastruct import HttpTask
from core.redistools import RedisQueue

DEFAULT_PATH = r"/home/wuyadong/test/"

define("namespace", default="mtime", type=str, help="the namespace of the prepare-queue")
define("city_codes", default=None, type=list, help="citycode you want to crawl")
define("host", default="localhost", type=str, help="redis host")
define("port", default=6379, type=int, help="redis port")
define("db", default=0, type=int, help="redis db")
define("path", default=DEFAULT_PATH, type=str, help="cinema root path")

def build_cinema_path(path=DEFAULT_PATH, city_codes=None):
    """构造cinema的路径
        Args:
            path: str, cinema存放的路径
            city_code: str, citycode
        Yields:
            path: str, cinema对应的路径
    """
    children_paths = os.listdir(path)
    if not city_codes:
        city_codes = children_paths
    city_codes = ['110000']
    for city_code in city_codes:
        if city_code.isdigit():
            yield city_code, os.path.join(path, city_code, "cinema.csv")

def read_cinema_file(file_path):
    """读取cinema.csv,导出二元组
        Args:
            file_path: str, 文件路径
        Yields:
            ()
    """
    with open(file_path, "rb") as in_file:
        line = in_file.readline()
        while len(line) > 0:
            text_splits = line.split(",")
            cinema_id, district_str = text_splits[1], text_splits[-1]
            yield (cinema_id.strip(), district_str.strip())
            line = in_file.readline()

def build_http_task(city_code, cinema_id, district_str):
    """构造抓取任务
        Args:
            city_code: str, 城市code
            cinema_id: str, cinemacode
            district_str: str, 区域名
        Returns:
            task: HTTPTask, 任务描述
    """
    url = r"%s/%s/%s/" % ("http://theater.mtime.com",
                        district_str, cinema_id,)
    return HttpTask(HTTPRequest(url, connect_timeout=10, request_timeout=20),
                callback='RealInfoParser', max_fail_count=3, kwargs={'citycode':city_code,
                                                   'cinemaid':cinema_id,
                                                   'district': district_str,
                                                   'requesturl': url})

def load_tasks(namespace, city_codes=None, host="localhost", port=6379, db=0, path=DEFAULT_PATH):
    key = "%s:%s" % (namespace, "prepare")
    que = RedisQueue(key, host=host, port=port, db=db)

    for city_code, cinema_path in build_cinema_path(city_codes=city_codes, path=path):
        for cinema_id, district_str in read_cinema_file(cinema_path):
            task = build_http_task(city_code, cinema_id, district_str)
            que.push(task)

if __name__ == "__main__":
    options.parse_command_line()
    load_tasks(options.namespace, options.city_codes, options.host,
               options.port, options.db, options.path)

