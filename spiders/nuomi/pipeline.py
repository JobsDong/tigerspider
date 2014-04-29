#!/usr/bin/python2.7
#-*- coding=utf-8 -*-


__authors__ = ['"wuyadong" <wuyadong@tigerknows.com>']

import datetime
import os
import json

from core.spider.pipeline import BasePipeline
from core.db import DB, DBError

from spiders.nuomi.items import DealItem, PictureItem
from spiders.nuomi.util import item2dict


class DealItemPipeline(BasePipeline):
    """处理DealItem的类
    """
    def __init__(self, namespace, db_host="127.0.0.1", db_port=5432,
                 db_user="postgres", db_password="titps4gg", db_base="swift"):
        """初始化DealItemPipeline
            主要是链接数据库
        """
        BasePipeline.__init__(self, namespace)
        self.logger.debug("init nuomi DealItemPipeline")
        try:
            self.item_db = DB(host=db_host, port=db_port, user=db_user,
                              password=db_password, database=db_base)
        except DBError, e:
            self.logger.error("db error %s" % e)

    def process_item(self, item, kwargs):
        """处理item
            Args:
                item: DealItem 解析的对象
                kwargs: dict, 额外的参数字典
        """
        if isinstance(item, DealItem):
            self._store_item(item)

    def _store_item(self, item):
        try:
            clone_dict = item2dict(item)

            encodestr = json.dumps(clone_dict, ensure_ascii=False)
            selectsql = "SELECT * FROM rt_crawl WHERE url=%(url)s LIMIT 1"
            if len(self.item_db.execute_query(selectsql, {'url': item.url})) >= 1:
                updatesql = "UPDATE rt_crawl SET city_code=%(city_code)s," \
                            " type=%(type)s," \
                            " start_time=%(start_time)s, end_time=%(end_time)s," \
                            " info=%(info)s," \
                            " source=%(source)s, update_time=%(update_time)s " \
                            "WHERE url=%(url)s"

                self.item_db.execute_update(updatesql,
                                            {'city_code': item.city_code,
                                            'type': 90002003,
                                            'start_time': item.start_time,
                                            'end_time': item.end_time,
                                            'info': encodestr, 'source': 'nuomi',
                                            'update_time': datetime.datetime.now(),
                                            'url': item.url})
            else:
                insertsql = "INSERT INTO rt_crawl \
                (city_code, type, start_time, end_time, \
                info, url, source, update_time, add_time) \
                VALUES(%(city_code)s, %(type)s, %(start_time)s, %(end_time)s, " \
                            "%(info)s, %(url)s, %(source)s, " \
                            "%(update_time)s, %(add_time)s)"

                self.item_db.execute_update(
                    insertsql, {'city_code': item.city_code, 'type': 90002003,
                                'start_time': item.start_time,
                                'end_time': item.end_time, 'info': encodestr,
                                'url': item.url, 'source': 'nuomi',
                                'update_time': datetime.datetime.now(),
                                'add_time': datetime.datetime.now()})

        except Exception, e:
            self.logger.warn("sql error:%s" % e)
            raise e

    def clear_all(self):
        """释放资源
            关闭数据库连接
        """
        try:
            self.item_db.close()
        except Exception, ignore:
            self.logger.warn("clear failed:%s" % ignore)


class PictureItemPipeline(BasePipeline):
    """对应于PictureItem的处理类
    """
    def __init__(self, namespace):
        BasePipeline.__init__(self, namespace)
        self.logger.debug("init nuomi PictureItemPipeline")

    def process_item(self, item, kwargs):
        """生成目录，保存图片文件
        """
        if isinstance(item, PictureItem):
            if not os.path.exists(item.path):
                _check_and_create(item.path)
                with open(item.path, "wb") as picture_file:
                    picture_file.write(item.picture)

    def clear_all(self):
        pass


def _check_and_create(path):
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