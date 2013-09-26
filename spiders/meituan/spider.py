#!/usr/bin/python2.7
#-*- coding=utf-8 -*-

# Copy Rights (c) Beijing TigerKnows Technology Co., Ltd.

__authors__ = ['"wuyadong" <wuyadong@tigerknows.com>']

from tornado.httpclient import HTTPRequest

from core.datastruct import HttpTask
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
        # HttpTask(HTTPRequest(url='http://www.meituan.com/api/v2/nanchang/deals',
        #                  connect_timeout=3, request_timeout=99),
        #      callback='DealParser', max_fail_count = 5, kwargs={'citycode':"360100"}),
        HttpTask(HTTPRequest(url='http://api.union.meituan.com/data/citylist',
        connect_timeout=10, request_timeout=60), callback='CityParser',
        max_fail_count=8, kwargs={}),
    ]




