#!/usr/bin/python
# -*- coding: utf-8 -*-

from tornado.httpclient import HTTPRequest

from core.datastruct import Task
from core.spider.spider import BaseSpider
from core.spider.pipeline import EmptyPipeline

from spiders.baiduoffset.parser import CoordParser
from spiders.baiduoffset.pipeline import CoordItemPipeline
from spiders.baiduoffset.parser import OffsetParser


class BaiduoffsetSpider(BaseSpider):
    u'''用于获取Baidu Offset
    '''

    parsers = {
        'OffsetParser': OffsetParser,
        'CoordParser': CoordParser,
    }

    pipelines = {
        'CityItem': EmptyPipeline,
        'CoordItem': CoordItemPipeline,
    }

    start_tasks = [
        Task(HTTPRequest(url='http://www.baidu.com/',
                         connect_timeout=3, request_timeout=5),
             callback='OffsetParser',
             kwargs={}),
    ]
