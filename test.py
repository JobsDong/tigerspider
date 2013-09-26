#!/usr/bin/python2.7
#-*- coding=utf-8 -*-

# Copy Rights (c) Beijing TigerKnows Technology Co., Ltd.

__authors__ = ['"wuyadong" <wuyadong@tigerknows.com>']

from core.datastruct import HttpTask
from tornado.httpclient import HTTPRequest
from core.redistools import RedisQueue

if __name__ == "__main__":

    que = RedisQueue("mtime:prepare")

    with open("/home/wuyadong/git/tigerknows-spider"
              "/data/fails/MtimeSpider-2013-09-25 14:54:29.csv", "rb") \
    as input_file:
        line = input_file.readline()
        while line is not None and len(line) > 0:
            url = line.split(r'"')[1]
            request = HTTPRequest(url, connect_timeout=5, request_timeout=10)
            if url.startswith("http://service"):
                task = HttpTask(request, max_fail_count=4, callback="JSParser", kwargs=
                {'citycode'})
            else:
                task = HttpTask(request, max_fail_count=3, callback="RealInfoParser")
            que.push(task)
            line = input_file.readline()

