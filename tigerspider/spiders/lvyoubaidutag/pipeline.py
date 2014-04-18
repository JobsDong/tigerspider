#!/usr/bin/python
#-*- coding=utf-8 -*-

__author__ = ['"wuyadong" <wuyadong@tigerknows.com>']

import csv
from tigerspider.core.spider.pipeline import BasePipeline
from tigerspider.spiders.lvyoubaidutag.items import TagItem


class TagItemPipeline(BasePipeline):
    """处理标签信息的pipeline
    """
    def __init__(self, namespace, csv_file_path="/tmp/tag.csv"):
        BasePipeline.__init__(self, namespace)
        self._out_file = open(csv_file_path, "wb")
        self._csv_writer = csv.writer(self._out_file, delimiter=',', quotechar='"',
                                      quoting=csv.QUOTE_ALL, lineterminator='\n')
        self.logger.info("init tag item pipeline")

    def process_item(self, item, kwargs):
        """处理函数
        """
        if isinstance(item, TagItem):
            row = [item.sid, item.tag]
            row = [t.encode('utf-8') if isinstance(t, unicode) else t for t in row]
            self._csv_writer.writerow(row)

    def clear_all(self):
        self._out_file.close()