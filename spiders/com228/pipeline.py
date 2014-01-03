#!/usr/bin/python
#-*- coding=utf-8 -*-

__author__ = ['"wuyadong" <wuyadong@tigerknows.com>']

import os
import json
import datetime
from core.redistools import RedisDict, RedisError
from core.db import DB, DBError
from core.spider.pipeline import BasePipeline
from spiders.com228.items import PictureItem, ActivityItem, WebItem


class ActivityItemPipeline(BasePipeline):
    """用于处理ActivityItem的pipeline
    """
    def __init__(self, namesapce, redis_host, redis_port, redis_db):
        BasePipeline.__init__(self, namesapce)
        self.logger.info("init activity item pipline finished")
        try:
            redis_namespace = "%s:%s" % (namesapce, "temp")
            self.temp_item_dict = RedisDict(redis_namespace, host=redis_host,
                                            port=redis_port, db=redis_db)
        except RedisError, e:
            self.logger.error("redis error %s" % e)
            raise e

    def process_item(self, item, kwargs):
        """处理方法
            Args:
                item: ActivityItem, 解析的结果
                kwargs: dict, 参数字典
        """
        if isinstance(item, ActivityItem):
            self.temp_item_dict.set(item.order, item)

    def clear_all(self):
        pass


class WebItemPipeline(BasePipeline):
    """WebItem处理器
    """
    def __init__(self, namespace, redis_host, redis_port, redis_db, db_host, db_port, db_user,
                 db_password, db_base):
        BasePipeline.__init__(self, namespace)
        try:
            redis_namespace = "%s:%s" % (namespace, "temp")
            self._temp_redis_dict = RedisDict(redis_namespace, host=redis_host, port=redis_port, db=redis_db)
            self._db = DB(host=db_host, port=db_port, user=db_user, password=db_password, database=db_base)
        except RedisError, e:
            self.logger.error("init redis dict failed error:%s" % e)
            raise e
        except DBError, e:
            self.logger.error("init db failed error:%s" % e)
            raise e

        self.logger.info("init web item pipeline finished")

    def process_item(self, item, kwargs):
        """处理item的函数
            Args:
                item: WebItem, 解析后的结果
                kwargs: dict, 参数字典
        """
        if isinstance(item, WebItem):
            if self._temp_redis_dict.has_key(item.order):
                # 合并数据，并保存到数据库中
                activity_item = self._temp_redis_dict.get(item.order)
                if activity_item is not None:
                    self._temp_redis_dict.delete(item.order)
                    self._store_complete_item(activity_item, item)

            else:
                self.logger.warn("redis dict not has activity item order:%s" % item.order)

    def _store_complete_item(self, activity_item, web_item):
        """用于保存完整的item到数据库中
            Args:
                activity_item: ActivityItem, 活动内容
                web_item: WebItem: 活动详情内容
        """
        #  转换格式
        start_time, end_time, city_code, info, _type, url = _convert(activity_item, web_item)
        #  完整性验证
        if _check(info, start_time, url):
            # 存储
            try:
                self._store(url, city_code, start_time, end_time, info, _type)
            except DBError, e:
                self.logger.error("db error:%s" % e)
        else:
            self.logger.warn("invalidate item info:%s, start_time:%s, url:%s" % (info, start_time, url))

    def _store(self, url, city_code, start_time, end_time, info, _type):
        """保存数据
            Args:
                url: str, url
                city_code: int, city code
                start_time: datetime
                end_time: datetime
                info: dict
                _type: str
            Raise:
                DBError
        """
        selectsql = "SELECT * FROM rt_crawl WHERE url=%(url)s and source=%(source)s LIMIT 1"
        info_str = json.dumps(info, ensure_ascii=True)
        if len(self._db.execute_query(selectsql, {'url': url, 'source': '228com'})) >= 1:
            # update
            updatesql = "UPDATE rt_crawl SET city_code=%(city_code)s, type=%(type)s," \
                        " start_time=%(start_time)s, end_time=%(end_time)s, info=%(info)s," \
                        " source=%(source)s, update_time=%(update_time)s WHERE url=%(url)s"

            self._db.execute_update(updatesql, {'city_code': city_code, 'type': _type,
                                                'start_time': start_time,
                                                'end_time': end_time,
                                                'info': info_str, 'source': '228com',
                                                'update_time': datetime.datetime.now(),
                                                'url': url})
        else:
            insertsql = "INSERT INTO rt_crawl \
            (city_code, type, start_time, end_time, \
            info, url, source, update_time, add_time) \
            VALUES(%(city_code)s, %(type)s, %(start_time)s, %(end_time)s, " \
                        "%(info)s, %(url)s, %(source)s, %(update_time)s, %(add_time)s)"

            self._db.execute_update(insertsql,
                                    {'city_code': city_code, 'type': _type,
                                     'start_time': start_time,
                                     'end_time': end_time,
                                     'info': info_str, 'url': url,
                                     'source': '228com', 'update_time': datetime.datetime.now(),
                                     'add_time': datetime.datetime.now()})

    def clear_all(self):
        """释放资源
            关闭数据库连接，清空redis中的数据
        """
        try:
            self._db.close()
            self._temp_redis_dict.clear()
        except Exception, ignore:
            self.logger.warn("clear failed:%s" % ignore)


def _convert(activity_item, web_item):
    """转换格式
        Args:
            activity_item: ActivityItem, 活动Item
            web_item: WebItem, WebItem
        Returns:
            start_time, end_time, city_code, info, _type, url: 元组
    """
    city_code = activity_item.city_code
    start_time = activity_item.start_time
    end_time = activity_item.end_time
    _type = "90003001"
    url = activity_item.url.encode('utf-8')
    info = {
        "name": activity_item.name,
        "place": [{"place_name": activity_item.place_name, "address": ""}],
        "tag": activity_item.tag,
        "pictures": [web_item.picture_path.encode('utf-8')],
        "description": web_item.description.encode('utf-8'),
        "longitude": "",
        "latitude": "",
        "price": activity_item.price.encode("utf-8"),
        "order": activity_item.order.encode('utf-8'),
        "contact": "",
        "organizer_class": "",
        "organizer_name": "",
        "interested_user": "",
        "joined_user": "",
        "time_info": web_item.time_info.encode('utf-8'),
    }
    return start_time, end_time, city_code, info, _type, url


def _check(info, start_time, url):
    """检查item中，所需的字段是否符合规定
        Args:
            info: dict, 字典
            start_time: datetime, 开始时间
            url: str, 链接
        Returns:
            is_validate: boolean, true or false
    """
    if len(info['name']) <= 0:
        return False
    if len(info['description']) <= 0:
        return False
    if len(info['order']) <= 0:
        return False
    if start_time is None:
        return False
    if len(url) <= 0:
        return False

    return True


class PictureItemPipeline(BasePipeline):
    """对应于PictureItem的处理类
    """
    def __init__(self, namespace):
        BasePipeline.__init__(self, namespace)
        self.logger.debug("init 228com PictureItemPipeline")

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
