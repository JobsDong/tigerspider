#!/usr/bin/python
#-*- coding=utf-8 -*-

__author__ = ['"wuyadong" <wuyadong@tigerknows.com>']

import csv

from tigerspider.core.spider.pipeline import BasePipeline
from tigerspider.spiders.intro1.items import WebItem


class WebItemPipeline(BasePipeline):

    def __init__(self, namespace, out_path=u"webitem.csv"):
        BasePipeline.__init__(self, namespace)
        self._out_file = open(out_path, u"wb")
        self._csv_file = csv.writer(self._out_file)
        self.logger.info(u"init WebItemPipeline finish")

    def process_item(self, item, kwargs):
        """process web item
            Args:
                item: WebItem
        """
        if isinstance(item, WebItem):
            no_unicode = lambda a: a.encode(u'utf-8') if isinstance(
                a, unicode) else a

            url = no_unicode(item.url)
            order = no_unicode(item.order)
            description = no_unicode(item.description)
            time_info = no_unicode(item.time_info)
            price = no_unicode(item.price)
            name = no_unicode(item.name)
            self._csv_file.writerow([name, url, order, price, time_info,
                                     description])

    def clear_all(self):
        self._out_file.close()
