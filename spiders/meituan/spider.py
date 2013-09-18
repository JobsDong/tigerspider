#!/usr/bin/python2.7
#-*- coding=utf-8 -*-

# Copy Rights (c) Beijing TigerKnows Technology Co., Ltd.

__authors__ = ['"wuyadong" <wuyadong@tigerknows.com>']

from tornado.httpclient import HTTPRequest

from core.datastruct import Task
from core.spider.spider import BaseSpider
from core.spider.pipeline import EmptyPipeline

from spiders.meituan.parser import CityParser, WebParser, DealParser, PictureParser
from spiders.meituan.pipeline import DealItemPipeline, WebItemPipeline, PictureItemPipeline

class MeituanSpider(BaseSpider):
    u"""用于获取美团团购数据的爬虫
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
        Task(HTTPRequest(url='http://www.meituan.com/api/v2/nanchang/deals',
                         connect_timeout=3, request_timeout=99), callback='DealParser',
             kwargs={'citycode':"360100"}),
        # Task(HTTPRequest(url='http://api.union.meituan.com/data/citylist',
        # connect_timeout=10, request_timeout=60), callback='CityParser', kwargs={}),
    ]




