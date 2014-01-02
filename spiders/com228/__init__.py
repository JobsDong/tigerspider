#!/usr/bin/python
#-*- coding=utf-8 -*-

"""www.228.com 抓取系统
"""

__author__ = ['"wuyadong" <wuyadong@tigerknows.com>']

from core.spider.spider import BaseSpider


class Com228Spider(BaseSpider):
    """用于抓取228.com的活动数据的爬虫
    """

    parsers = {
        "CityParser": None,
        "TypeParser": None,
        "ActivityParser": None,
        "PictureParser": None,
    }

    pipelines = {
        "CityDeal": None,
        "TypeDeal": None,
    }