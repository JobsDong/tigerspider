#!/usr/bin/python
# -*- coding: utf-8 -*-

from tornado.httpclient import HTTPRequest

from core.datastruct import Task
from core.spider.spider import BaseSpider
from core.spider.pipeline import EmptyPipeline

from spiders.ganji.parser import CommunityParser
from spiders.ganji.pipeline import CommunityItemPipeline
from spiders.ganji.parser import CityParser


class GanjiSpider(BaseSpider):
    u'''用于获取赶集网小区名称的爬虫
    '''

    parsers = {
        'CityParser': CityParser,
        'CommunityParser': CommunityParser,
    }

    pipelines = {
        'CityItem': EmptyPipeline,
        'CommunityItem': CommunityItemPipeline,
    }

    start_tasks = [
        # Task(HTTPRequest(url='http://www.meituan.com/api/v2/nanchang/deals',
        #                  connect_timeout=3, request_timeout=99),
        #                  callback='DealParser',
        #                  kwargs={'citycode':"360100"}),
        #Task(HTTPRequest(url='http://www.ganji.com/index.htm',
                         #connect_timeout=3, request_timeout=5),
             #callback='CityParser',
             #cookie_host='http://www.ganji.com/index.htm',
             #cookie_count=15, kwargs={}),

        Task(HTTPRequest('http://bj.ganji.com/xiaoqu/', connect_timeout=5, request_timeout=10),
             callback='CommunityParser', cookie_host='http://www.ganji.com/index.htm', cookie_count=15,
             kwargs={'cityname': '110000'})
    ]
