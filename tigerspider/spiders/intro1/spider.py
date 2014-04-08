#!/usr/bin/python
#-*- coding=utf-8 -*-

__author__ = ['"wuyadong" <wuyadong@tigerknows.com>']

from tornado.httpclient import HTTPRequest

from tigerspider.core.spider.spider import BaseSpider
from tigerspider.core.datastruct import HttpTask
from tigerspider.spiders.intro1.parser import ActivityParser
from tigerspider.spiders.intro1.pipeline import WebItemPipeline


class Intro1Spider(BaseSpider):

    parsers = {
        u"ActivityParser": ActivityParser,
    }

    pipelines = {
        u"WebItem": WebItemPipeline,
    }

    start_tasks = [HttpTask(HTTPRequest(u"http://www.228.com.cn/ticket-49052202.html"),
                            callback=u"ActivityParser")]