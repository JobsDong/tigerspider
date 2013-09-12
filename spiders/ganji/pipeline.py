#!/usr/bin/python
# -*- coding: utf-8 -*-

"""主要是描述ganji数据的处理部分
    WebItemPipeline: 处理WebItem的类
"""


import os

from core.spider.pipeline import BasePipeline

from spiders.ganji.items import CommunityItem

DEFAULT_COMMUNITY_DIR = u"/home/iceout/ganji/"


class CommunityItemPipeline(BasePipeline):
    """用于处理CommunityItem
    """

    def process_item(self, item, kwargs):
        """将item存储在文件中
        """
        print 'pipeline:', item
        if isinstance(item, CommunityItem):
            if item.city and item.community:
                self._store_item(item)

    def _store_item(self, item):
        """存储item
            Args:
                item:Item
        """
        path = DEFAULT_COMMUNITY_DIR + item.city + ".csv"
        print path
        if not os.path.exists(path):
            self._check_and_create(path)
        else:
            with open(path, "ab") as out_file:
                line = u'"%s","%s"' % (item.community, item.address)
                out_file.write(line.encode("utf-8"))
                out_file.write("\n")

    def _check_and_create(self, path):
        """检查path所在的目录是否存在，如果不存在就创建
            path: str, 存储的路径
        """
        try:
            dot = path.rindex("/")
        except ValueError:
            pass
        else:
            directory = path[0:dot]
            if not os.path.exists(directory):
                os.makedirs(directory)
