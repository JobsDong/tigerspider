#!/usr/bin/python
#-*- coding=utf-8 -*-

__author__ = ['"wuyadong" <wuyadong@tigerknows.com>']

from core.spider.spider import BaseSpider
from spiders.lvyoubaidutag.parser import TagListParser
from spiders.lvyoubaidutag.pipeline import TagItemPipeline

from spiders.lvyoubaidutag.utils import build_tag_tasks


class LvYouBaiDuTagSpider(BaseSpider):
    """用于抓取百度旅游标签信息的爬虫
    """
    parsers = {
        "TagListParser": TagListParser,
    }

    pipelines = {
        "TagItem": TagItemPipeline,
    }

    start_tasks = build_tag_tasks()