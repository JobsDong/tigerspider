#!/usr/bin/python
#-*- coding=utf-8 -*-

__author__ = ['"wuyadong" <wuyadong@tigerknows.com>']

from tigerspider.core.spider.spider import BaseSpider
from tigerspider.spiders.com228.util import create_city_type_tasks
from tigerspider.spiders.com228.parser import DealParser, ActivityParser, PictureParser
from tigerspider.spiders.com228.pipeline import ActivityItemPipeline, WebItemPipeline, PictureItemPipeline


class Com228Spider(BaseSpider):
    """用于处理www.228.com的数据抓取爬虫
    """
    parsers = {
        "DealParser": DealParser,
        "ActivityParser": ActivityParser,
        "PictureParser": PictureParser,
    }

    pipelines = {
        "ActivityItem": ActivityItemPipeline,
        "WebItem": WebItemPipeline,
        "PictureItem": PictureItemPipeline,
    }

    start_tasks = create_city_type_tasks()
