#!/usr/bin/python2.7
#-*- coding=utf-8 -*-

# Copy Rights (c) Beijing TigerKnows Technology Co., Ltd.

"""用于获取窝窝团购数据的爬虫描述
    Tuan55Spider: 窝窝团爬虫
"""

__author__ = ['"wuyadong" <wuyadong@tigerknows.com>']

from tornado.httpclient import HTTPRequest

from core.datastruct import Task
from core.spider.spider import BaseSpider
from core.spider.pipeline import EmptyPipeline

from spiders.tuan55.parser import CityParser, WebParser, DealParser, PictureParser
from spiders.tuan55.pipeline import DealItemPipeline, WebItemPipeline, PictureItemPipeline

class Tuan55Spider(BaseSpider):
    """用于获取55tuan团购数据的爬虫
    """
    parsers = {
        'CityParser': CityParser,
        'DealParser': DealParser,
        'WebParser': WebParser,
        'PictureParser': PictureParser,
    }

    pipelines = {
        'CityItem': EmptyPipeline,
        'DealItem': DealItemPipeline,
        'WebItem': WebItemPipeline,
        'PictureItem': PictureItemPipeline,
    }

    start_tasks = [
         # Task(HTTPRequest(url='http://www.55tuan.com/city.xml',
         #                  connect_timeout=10, request_timeout=20),
         #      dns_need=False, max_fail_count=8,callback='CityParser', kwargs={}),
         Task(HTTPRequest(url='http://www.55tuan.com/openAPI.do?city=shanghai',
                         connect_timeout=1, request_timeout=1), callback='DealParser',
              max_fail_count=5, kwargs={'citycode':360100})
        # Task(HTTPRequest(url='http://www.55tuan.com/goo2ds-967ba93aeaa2208a.html'),
        #     callback='WebParser')
    ]
