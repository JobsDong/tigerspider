#!/usr/bin/python2.7
#-*- coding=utf-8 -*-

# Copy Rights (c) Beijing TigerKnows Technology Co., Ltd.

"""用于获取窝窝团购数据的爬虫描述
    Tuan55Spider: 窝窝团爬虫
"""

__author__ = ['"wuyadong" <wuyadong@tigerknows.com>']

from tornado.httpclient import HTTPRequest
from core.datastruct import FileTask, HttpTask
from core.spider.spider import BaseSpider

from spiders.tuan55.parser import WebParser, DealParser, PictureParser, AddressParser
from spiders.tuan55.pipeline import (DealItemPipeline, WebItemPipeline,
                                PictureItemPipeline, AddressItemPipeline)

class Tuan55Spider(BaseSpider):
    """用于获取55tuan团购数据的爬虫
    """
    parsers = {
        'DealParser': DealParser,
        'WebParser': WebParser,
        'PictureParser': PictureParser,
        'AddressParser': AddressParser,
    }

    pipelines = {
        'DealItem': DealItemPipeline,
        'WebItem': WebItemPipeline,
        'PictureItem': PictureItemPipeline,
        'AddressItem': AddressItemPipeline,
    }

    start_tasks = [
         # Task(HTTPRequest(url='http://www.55tuan.com/city.xml',
         #                  connect_timeout=10, request_timeout=20),
         #      dns_need=False, max_fail_count=8,callback='CityParser', kwargs={}),
         #HttpTask(HTTPRequest(url='http://www.55tuan.com/openAPI.do?city=shanghai',
         #                 connect_timeout=1, request_timeout=1), callback='DealParser',
         #      max_fail_count=5, kwargs={'citycode':360100})
         # HttpTask(HTTPRequest(url='http://dalian.55tuan.com/goods-92d9c592242770cf.html'),
         #     callback='WebParser')
        FileTask("/home/wuyadong/Downloads/55tuan_mobile.xml", callback='DealParser')
    ]
