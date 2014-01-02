#!/usr/bin/python
#-*- coding=utf-8 -*-

__author__ = ['"wuyadong" <wuyadong@tigerknows.com>']

from core.spider.spider import BaseSpider
from spiders.com228.util import create_city_type_tasks
from spiders.com228.parser import DealParser

class Com228Spider(BaseSpider):
    """用于处理www.228.com的数据抓取爬虫
    """
    parsers = {
        "DealParser": DealParser,
    }
    start_tasks = create_city_type_tasks()
