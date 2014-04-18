#!/usr/bin/python
#-*- coding=utf-8 -*-

__author__ = ['"wuyadong" <wuyadong@tigerknows.com>']


from tigerspider.core.spider.spider import BaseSpider
from tigerspider.core.datastruct import HttpTask

from tigerspider.spiders.lvyoudaodao.parser import AttractionListParser, AttractionParser, DescriptionParser
from tigerspider.spiders.lvyoudaodao.pipeline import AttractionItemPipeline, DescriptionItemPipeline
from tigerspider.spiders.lvyoudaodao.utils import build_description_request, build_next_page_request, build_attraction_request


class LvYouDaoDaoSpider(BaseSpider):
    """用于抓取道道旅游信息的爬虫
    """
    parsers = {
        "AttractionListParser": AttractionListParser,
        "AttractionParser": AttractionParser,
        "DescriptionParser": DescriptionParser,
    }

    pipelines = {
        "AttractionItem": AttractionItemPipeline,
        "DescriptionItem": DescriptionItemPipeline,
    }

    start_tasks = [HttpTask(build_next_page_request(u"/Attractions-g308272-Activities-Shanghai.html"),
                            callback="AttractionListParser",)]