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
         Task(HTTPRequest(url='http://www.55tuan.com/city.xml',
                          connect_timeout=4, request_timeout=5),
              dns_need=False, callback='CityParser', kwargs={}),
         #Task(HTTPRequest(url='http://www.55tuan.com/openAPI.do?city=beijing',
         #                 connect_timeout=2, request_timeout=99), callback='DealParser',
         #     kwargs={'citycode':360100})
        #jTask(HTTPRequest(url='http://www.55tuan.com/goods-967ba93aeaa2208a.html'),
         #    callback='WebParser')
    ]
