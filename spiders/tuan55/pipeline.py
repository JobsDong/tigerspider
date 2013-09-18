#!/usr/bin/python2.7
#-*- coding=utf-8 -*-

# Copy Rights (c) Beijing TigerKnows Technology Co., Ltd.

"""这是描述item处理过程模块
    DealItemPipeline: 用于处理DealItem的类
    WebItemPipeline: 用于处理WebItem的类
    PictureItemPipeline: 用于处理PictureItem的类
"""

__author__ = ['"wuyadong" <wuyadong@tigerknows.com>']

import datetime
import os
import json

from core.spider.pipeline import BasePipeline
from core.redistools import RedisDict, RedisError
from core.db import DB, DBException

from spiders.tuan55.items import  DealItem, WebItem, PictureItem
from spiders.tuan55.util import item2dict

class DealItemPipeline(BasePipeline):
    """处理DealItem的类

    """
    def __init__(self, namespace, temp_host="localhost", temp_port=6379, temp_db=0):
        """初始化DealItemPipeline
            主要是连接redis
        """
        BasePipeline.__init__(self, namespace)
        self.logger.debug("init 55tuan.DealItemPipeline")
        try:
            temp_namespace = "%s:%s" % (namespace, "temp")
            self.temp_item_dict = RedisDict(temp_namespace, host=temp_host, port=temp_port, db=temp_db)
        except RedisError, e:
            self.logger.error("redis error %s" % e)

    def process_item(self, item, kwargs):
        """处理item
            Args:
                item: DealItem 解析的对象
                kwargs: dict, 额外的参数字典
        """
        if isinstance(item, DealItem):
            self.temp_item_dict.set(item.url, item)

    def clear_all(self):
        pass


class WebItemPipeline(BasePipeline):
    """处理webItem的类
    """
    def __init__(self, namespace, temp_host="localhost", temp_port=6379,
                 temp_db=0, db_host="192.168.11.195", db_port=5432, db_user="postgres",
                 db_password="titps4gg", db_base="swift"):
        """初始化WebItemPipeline
            主要是连接redis，postgres
        """
        BasePipeline.__init__(self, namespace)
        self.logger.debug("init 55tuan.WebItemPipeline")
        try:
            temp_namespace = "%s:%s" % (namespace, "temp")
            self.temp_item_dict = RedisDict(temp_namespace, host=temp_host, port=temp_port, db=temp_db)
            self.item_db = DB(host=db_host, port=db_port,user=db_user,
                              password=db_password, database=db_base)
        except DBException, e:
            self.logger.error("db error %s" % e)
        except RedisError, e:
            self.logger.error("redis error %s" % e)

    def process_item(self, item, kwargs):
        """处理WebItem
            Args:
                item:WebItem，解析后的结果
                kwargs:dict, 参数字典
        """
        if isinstance(item, WebItem):
            if not kwargs.has_key('url'):
                self.logger.error("web item 'kwargs' lack of url")
            else:
                deal_item = self.temp_item_dict.get(kwargs['url'])
                if deal_item is not None:
                    self.temp_item_dict.delete(kwargs['url'])
                    deal_item.name = item.name
                    deal_item.noticed = item.noticed
                    deal_item.description = item.description
                    deal_item.short_desc = item.short_desc
                    deal_item.refund = item.refund
                    deal_item.content_text = item.content_text
                    deal_item.content_pic = item.content_pic
                    deal_item.save = item.save
                    deal_item.place = item.place
                    deal_item.discount_type = item.discount_type
                    # if len(item.deadline) > 0:
                    #     deal_item.deadline = item.deadline
                    if deal_item.discount_type is not None:
                        self._store_item(deal_item)

    def _store_item(self, item):
        try:
            clone_dict = item2dict(item)

            encodestr = json.dumps(clone_dict, ensure_ascii=False)
            selectsql = "SELECT * FROM rt_crawl WHERE url=%(url)s LIMIT 1"
            if len(self.item_db.execute_query(selectsql, {'url': item.url})) >= 1:
                updatesql = "UPDATE rt_crawl SET city_code=%(city_code)s, type=%(type)s," \
                            " start_time=%(start_time)s, end_time=%(end_time)s, info=%(info)s," \
                            " source=%(source)s, update_time=%(update_time)s WHERE url=%(url)s"

                self.item_db.execute_update(updatesql, {'city_code': item.city_code,
                                                        'type': 90002003, 'start_time': datetime.datetime.fromtimestamp(
                                                        float(item.start_time)),
                                                        'end_time': datetime.datetime.fromtimestamp(float(item.end_time)),
                                                        'info': encodestr, 'source': '55tuan',
                                                        'update_time': datetime.datetime.now(), 'url': item.url})
            else:
                insertsql = "INSERT INTO rt_crawl \
                (city_code, type, start_time, end_time, \
                info, url, source, update_time, add_time) \
                VALUES(%(city_code)s, %(type)s, %(start_time)s, %(end_time)s, " \
                            "%(info)s, %(url)s, %(source)s, %(update_time)s, %(add_time)s)"


                self.item_db.execute_update(insertsql, {'city_code': item.city_code,
                    'type': 90002003, 'start_time': datetime.datetime.fromtimestamp(float(item.start_time)),
                    'end_time': datetime.datetime.fromtimestamp(float(item.end_time)),'info': encodestr,
                    'url': item.url, 'source': '55tuan','update_time': datetime.datetime.now(),
                    'add_time': datetime.datetime.now()})

        except Exception, e:
            self.logger.warn("sql error:%s" % e)
            raise e

    def clear_all(self):
        """释放资源
            关闭数据库连接，清空redis中的数据
        """
        try:
            self.temp_item_dict.clear()
            self.item_db.close()
        except Exception, ignore:
            self.logger.warn("clear failed:%s" % ignore)


class PictureItemPipeline(BasePipeline):
    """对应于PictureItem的处理类
    """
    def __init__(self, namespace):
        BasePipeline.__init__(self, namespace)
        self.logger.debug("init 55tuan.PictureItemPipeline")

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
