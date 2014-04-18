#!/usr/bin/python2.7
#-*- coding=utf-8 -*-


"""spider of ctrip through api
    CtripSpider: spider for ctrip
"""

__authors__ = ['"wuyadong" <wuyadong@tigerknows.com>']

from tigerspider.core.spider.spider import BaseSpider
from tigerspider.core.datastruct import FileTask
from tigerspider.core.util import get_project_path

from tigerspider.spiders.ctrip.parser import CityParser, HotelListParser, HotelParser
from tigerspider.spiders.ctrip.pipeline import (CityItemPipeline, HotelCodeItemPipeline,
                                    RoomInfoItemPipeline, HotelInfoItemPipeline,
                                    ImageItemPipeline)


class CtripSpider(BaseSpider):
    """用于获取携程酒店信息的爬虫
    """

    parsers = {
        "CityParser": CityParser,
        "HotelParser": HotelParser,
        "HotelListParser": HotelListParser,
    }

    pipelines = {
        "CityItem": CityItemPipeline,
        "HotelCodeItem": HotelCodeItemPipeline,
        "HotelInfoItem": HotelInfoItemPipeline,
        "RoomInfoItem": RoomInfoItemPipeline,
        "ImageItem": ImageItemPipeline,
    }

    start_tasks = [
        FileTask("%sctrip_city.xml" % get_project_path(),
                 callback="CityParser", max_fail_count=8),
    ]
