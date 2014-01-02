#!/usr/bin/python
#-*- coding=utf-8 -*-

__author__ = ['"wuyadong" <wuyadong@tigerknows.com>']

import os
from core.redistools import RedisDict, RedisError
from core.db import DB, DBError
from core.spider.pipeline import BasePipeline
from spiders.com228.items import PictureItem, ActivityItem


class PictureItemPipeline(BasePipeline):
    """对应于PictureItem的处理类
    """
    def __init__(self, namespace):
        BasePipeline.__init__(self, namespace)
        self.logger.debug("init 228.com PictureItemPipeline")

    def process_item(self, item, kwargs):
        """生成目录，保存图片文件
        """
        if isinstance(item, PictureItem):
            if not os.path.exists(item.path):
                self._check_and_create(item.path)
                with open(item.path, "wb") as picture_file:
                    picture_file.write(item.picture)

    def _check_and_create(self, path):
        """检查path所在的目录是否存在，如果不存在就创建
            path: str, picture存储的路径
        """
        try:
            dot = path.rindex("/")
        except ValueError:
            pass
        else:
            directory = path[0:dot]
            if not os.path.exists(directory):
                os.makedirs(directory)

    def clear_all(self):
        pass

