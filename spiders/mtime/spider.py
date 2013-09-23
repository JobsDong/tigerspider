#!/usr/bin/python2.7
#-*- coding=utf-8 -*-

# Copy Rights (c) Beijing TigerKnows Technology Co., Ltd.


__authors__ = ['"wuyadong" <wuyadong@tigerknows.com>']

from tornado.httpclient import HTTPRequest
from core.spider.spider import BaseSpider

from core.datastruct import HttpTask

from spiders.mtime.parser import RealInfoParser
from spiders.mtime.pipeline import RealInfoPipeline

class MtimeSpider(BaseSpider):
    """抓取mtime中影片信息的类
    """
    parsers = {
        "RealInfoParser": RealInfoParser,
    }

    pipelines = {
        "RealInfoItem": RealInfoPipeline,
    }

    start_tasks = [
        HttpTask(HTTPRequest("http://theater.mtime.com/China_Hunan_Province_Changsha_Yuhuaqu/2883/"),
                 callback="RealInfoParser", kwargs={"citycode":"430100"})
    ]


