#!/usr/bin/python2.7
#-*- coding=utf-8 -*-

# Copy Rights (c) Beijing TigerKnows Technology Co., Ltd.

__authors__ = ['"wuyadong" <wuyadong@tigerknows.com>']

import json
import datetime

from core.spider.pipeline import BasePipeline
from core.db import DB, DBError

from spiders.mtime.util import item2dict
from spiders.mtime.items import RealInfoItem, MovieInfoItem

class MovieInfoPipeline(BasePipeline):
    """处理MovieInfo的pipeline
    """
    def __init__(self, namespace, db_host="192.168.11.195", db_port=5432,
                 db_user="postgres", db_password="titps4gg", db_base="test"):
        """初始化函数
            Args:
                namespace:str, 名字空间
                db_host: str, db的主机名
                db_port: int, db的端口
                db_user: str, db的用户名
                db_password: str, db的密码
                db_base: str, db的数据库名
        """
        BasePipeline.__init__(self, namespace)
        self.logger.debug("init mtime MovieInfoPipeline")
        try:
            self.item_db = DB(host=db_host, port=db_port,user=db_user,
                              password=db_password, database=db_base)
        except DBError, e:
            self.logger.error("db error %s" % e)

    def process_item(self, item, kwargs):
        """处理函数
            Args:
                item:MovieInfoItem, item对象
                kwargs: 参数字典，传递过来的参数
        """
        if isinstance(item, MovieInfoItem) and len(item.shopurl) > 0:
            self._store_item(item)

    def _store_item(self, item):
        """储存item项
            Args:
                item:MovieInfoItem, item项
        """
        selectsql = "SELECT * FROM rtmovie_mtime_urllist WHERE shopurl=%(shopurl)s LIMIT 1"
        if len(self.item_db.execute_query(selectsql, {'shopurl': item.shopurl})) >= 1:
            pass
        else:
            insertsql = """INSERT INTO rtmovie_mtime_urllist
            (cityname, shopurl)
            VALUES(%(cityname)s, %(shopurl)s)"""

            self.item_db.execute_update(insertsql, {'cityname': item.cityname,
                    'shopurl': item.shopurl})


class RealInfoPipeline(BasePipeline):
    """处理realInfo的pipeline
    """

    def __init__(self, namespace, db_host="192.168.11.195", db_port=5432,
                 db_user="postgres", db_password="titps4gg", db_base="test"):
        """初始化函数
            Args:
                namespace:str, 名字空间
                db_host: str, db的主机名
                db_port: int, db的端口
                db_user: str, db的用户名
                db_password: str, db的密码
                db_base: str, db的数据库名
        """
        BasePipeline.__init__(self, namespace)
        self.logger.debug("init mtime RealInfoPipeline")
        try:
            self.item_db = DB(host=db_host, port=db_port,user=db_user,
                              password=db_password, database=db_base)
        except DBError, e:
            self.logger.error("db error %s" % e)

    def process_item(self, item, kwargs):
        """处理函数
            Args:
                item:RealInfoItem, item对象
                kwargs: 参数字典，传递过来的参数
        """
        if isinstance(item, RealInfoItem) and len(item.url) > 0:
            self._store_item(item)

    def _store_item(self, item):
        """储存item项
            Args:
                item:RealInfItem, item项
        """
        clone_dict = item2dict(item)
        encodestr = json.dumps(clone_dict, ensure_ascii=False)
        selectsql = "SELECT * FROM rt_crawl WHERE url=%(url)s LIMIT 1"
        if len(self.item_db.execute_query(selectsql, {'url': item.url})) >= 1:
            updatesql = "UPDATE rt_crawl SET city_code=%(city_code)s, type=%(type)s," \
                        " start_time=%(start_time)s, info=%(info)s," \
                        " source=%(source)s, update_time=%(update_time)s WHERE url=%(url)s"
            self.item_db.execute_update(updatesql,
                                        {'city_code': item.city_code,'type': 90004002,
                                         'start_time': item.start_time,
                                        'info': encodestr, 'source': 'mtime',
                                        'update_time': datetime.datetime.now(),
                                        'url': item.url})
        else:
            insertsql = "INSERT INTO rt_crawl \
            (city_code, type, start_time, \
            info, url, source, update_time, add_time) \
            VALUES(%(city_code)s, %(type)s, %(start_time)s, " \
            "%(info)s, %(url)s, %(source)s, %(update_time)s, %(add_time)s)"

            self.item_db.execute_update(insertsql, {'city_code': item.city_code,
                    'type': 90004002, 'start_time': item.start_time,
                    'end_time': "",'info': encodestr,'url': item.url,
                    'source': 'mtime','update_time': datetime.datetime.now(),
                    'add_time': datetime.datetime.now()})
