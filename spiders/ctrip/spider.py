#!/usr/bin/python2.7
#-*- coding=utf-8 -*-

# Copy Rights (c) Beijing TigerKnows Technology Co., Ltd.

"""spider of ctrip through api
    CtripSpider: spider for ctrip
"""

__authors__ = ['"wuyadong" <wuyadong@tigerknows.com>']

from core.spider.spider import BaseSpider
from core.datastruct import FileTask

from spiders.ctrip.parser import CityParser, HotelListParser, HotelParser
from spiders.ctrip.pipeline import (CityItemPipeline, HotelCodeItemPipeline,
                                    RoomInfoItemPipeline, HotelInfoItemPipeline,
                                    ImageItemPipeline)
from spiders.ctrip.util import build_hotels_task_for_city, build_rooms_task_for_hotel


class CtripSpider(BaseSpider):
    """用于获取ctrip的酒店信息的爬虫
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
        FileTask("/home/wuyadong/Documents/ctrip/ctrip_city.xml",
                 callback="CityParser", max_fail_count=8)
        # build_hotels_task_for_city("1", "110000", "北京"),
        # build_hotels_task_for_city("39", "650100", "乌鲁木齐"),
        # build_hotels_task_for_city("559", "410100", "郑州"),
        # build_hotels_task_for_city("2", "310000", "上海"),
        #build_hotels_task_for_city("376", "360100", "南昌"),
        # build_rooms_task_for_hotel(["522716", "517466"], "110000", "北京")
    ]
