#!/usr/bin/python2.7
#-*- coding=utf-8 -*-

# Copy Rights (c) Beijing TigerKnows Technology Co., Ltd.


__authors__ = ['"wuyadong" <wuyadong@tigerknows.com>']

from tornado.httpclient import HTTPRequest

from core.spider.spider import BaseSpider
from core.datastruct import HttpTask
from spiders.mtime.parser import RealInfoParser, JSParser
from spiders.mtime.pipeline import RealInfoPipeline, MovieInfoPipeline

class MtimeSpider(BaseSpider):
    """抓取mtime中影片信息的类
    """

    parsers = {
        "RealInfoParser": RealInfoParser,
        "JSParser": JSParser,
    }

    pipelines = {
        "RealInfoItem": RealInfoPipeline,
        "MovieInfoItem": MovieInfoPipeline,
    }

    # start_tasks = [
    #     HttpTask(
    #         HTTPRequest("http://theater.mtime.com/China_Beijing_Chaoyang/2697/",
    #                     connect_timeout=5, request_timeout=10), callback='RealInfoParser',
    #         max_fail_count=2, proxy_need=True,
    #         kwargs={'citycode':'110000', 'cinemaid': 2697, 'district': 'China_Beijing_Chaoyang',
    #                                   'requesturl': "http://theater.mtime.com/China_Beijing_Chaoyang/2697/"}
    #             )
    # ]



