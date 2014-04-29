#!/usr/bin/python
#-*- coding=utf-8 -*-

__author__ = ['"wuyadong" <wuyadong@tigerknows.com>']

from tigerspider.core.spider.spider import BaseSpider
from tigerspider.spiders.lvyoubaidutag.parser import TagListParser
from tigerspider.spiders.lvyoubaidutag.pipeline import TagItemPipeline

from tigerspider.spiders.lvyoubaidutag.utils import build_tag_tasks


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