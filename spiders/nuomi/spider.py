#!/usr/bin/python2.7
#-*- coding=utf-8 -*-


"""定义糯米网数据抓取的spider结构
    NuomiSpider: 控制糯米网抓取的类
"""

__authors__ = ['"wuyadong" <wuyadong@tigerknows.com>']

from tornado.httpclient import HTTPRequest

from core.datastruct import HttpTask
from core.spider.spider import BaseSpider
from core.spider.pipeline import EmptyPipeline

from spiders.nuomi.parser import (CityParser, DealParser,
                                  PictureParser)
from spiders.nuomi.pipeline import (DealItemPipeline,
                                    PictureItemPipeline)


class NuomiSpider(BaseSpider):
    """团购类糯米网数据抓取
    """
    parsers = {
        'CityParser': CityParser,
        'DealParser': DealParser,
        'PictureParser': PictureParser,
    }

    pipelines = {
        'CityItem': EmptyPipeline,
        'DealItem': DealItemPipeline,
        'PictureItem': PictureItemPipeline,
    }

    start_tasks = [
        HttpTask(HTTPRequest(url='http://www.nuomi.com/help/api',
                         connect_timeout=10, request_timeout=20),
                         callback='CityParser', max_fail_count=8, kwargs={}),
    ]