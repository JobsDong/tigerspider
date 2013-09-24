#!/usr/bin/python2.7
#-*- coding=utf-8 -*-

# Copy Rights (c) Beijing TigerKnows Technology Co., Ltd.


__authors__ = ['"wuyadong" <wuyadong@tigerknows.com>']

from core.spider.spider import BaseSpider

from spiders.mtime.parser import RealInfoParser, JSParser
from spiders.mtime.pipeline import RealInfoPipeline

class MtimeSpider(BaseSpider):
    """抓取mtime中影片信息的类
    """
    parsers = {
        "RealInfoParser": RealInfoParser,
        "JSParser": JSParser,
    }

    pipelines = {
        "RealInfoItem": RealInfoPipeline,
    }



