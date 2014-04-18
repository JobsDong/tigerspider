#!/usr/bin/python2.7
#-*- coding=utf-8 -*-


"""定义糯米网数据抓取的spider结构
    NuomiSpider: 控制糯米网抓取的类
"""

__authors__ = ['"wuyadong" <wuyadong@tigerknows.com>']

from tornado.httpclient import HTTPRequest

from tigerspider.core.datastruct import HttpTask
from tigerspider.core.spider.spider import BaseSpider
from tigerspider.core.spider.pipeline import EmptyPipeline

from tigerspider.spiders.nuomi.parser import CityParser, DealParser, PictureParser
from tigerspider.spiders.nuomi.pipeline import DealItemPipeline, PictureItemPipeline


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
        #HttpTask(HTTPRequest(url='http://www.nuomi.com/api/tiger?city=nanchang',
        #                  connect_timeout=10, request_timeout=120),
        #                 callback='DealParser', kwargs={'citycode':360100})
    ]