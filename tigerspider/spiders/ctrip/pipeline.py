#!/usr/bin/python2.7
#-*- coding=utf-8 -*-


"""pipeline for ctrip
    CityItemPipeline: pipeline handle CityItem
    HotelCodeItemPipeline: pipeline handle HotelCodeItem
    HotelInfoItemPipeline: pipeline handle HotelInfoItem
    ImageItemPipeline: pipeline handle ImageItem
    RoomInfoItemPipeline: pipeline handle RoomInfoItem
"""

__authors__ = ['"wuyadong" <wuyadong@tigerknows.com>']

import json
import datetime

from tigerspider.core.spider.pipeline import BasePipeline
from tigerspider.core.db import DB, DBError

from tigerspider.spiders.ctrip.items import (HotelCodeItem, RoomInfoItem,
                                 HotelInfoItem, ImageItem)
from tigerspider.spiders.ctrip.util import (convert_room_info_item_2_dict,
                                convert_hotel_info_item_2_dict,
                                build_hotel_url)


class CityItemPipeline(BasePipeline):
    """pipeline handle city item
    """

    def __init__(self, namespace):
        """init method

            Args:
                namespace: str, namespace
        """
        BasePipeline.__init__(self, namespace)
        self.logger.debug("init city item pipeline")

    def process_item(self, item, kwargs):
        """process CityCodeItem
            Args:
                item: CityItem, item of city
                kwargs: dict, param dict from task
        """
        pass


class HotelCodeItemPipeline(BasePipeline):
    """pipeline handle hotel code item
    """

    def __init__(self, namespace, db_host="127.0.0.1", db_port=5432,
                 db_user="postgres", db_password="titps4gg", db_base="swift"):
        """init method
            Args:
                ignore
        """
        BasePipeline.__init__(self, namespace)
        self.logger.debug("init hotel code item pipeline")
        try:
            self.item_db = DB(host=db_host, port=db_port, user=db_user,
                              password=db_password, database=db_base)
        except DBError, e:
            self.logger.error("db error %s" % e)

    def process_item(self, item, kwargs):
        """process HotelCodeItem

            Args:
                item: HotelCodeItem, item
                kwargs: dict, params dict
        """
        if isinstance(item, HotelCodeItem):
            city_chinese_name = kwargs.get("chinesename")
            # print "hotel code", item.hotel_id, item.city_code,\
            #     city_chinese_name, item.hotel_url
            self._store_item(item, city_chinese_name)

    def _store_item(self, item, city_chinese_name):
        """store hotel code into rthotel_ctrip_urlist

            Args:
                item: HotelCodeItem, item
                city_chinese_name: str, chinese name of city
            Raises:
                e: Exception
        """
        try:
            selectsql = "SELECT * FROM rthotel_ctrip_urllist WHERE shopurl=%(url)s LIMIT 1"
            if len(self.item_db.execute_query(selectsql, {'url': item.hotel_url})) < 1:
                insertsql = """INSERT INTO rthotel_ctrip_urllist
                (cityname, shopurl, addtime)
                VALUES(%(cityname)s, %(shopurl)s, %(addtime)s)"""

                self.item_db.execute_update(insertsql, {'cityname': city_chinese_name,
                                                        'shopurl': item.hotel_url, 'addtime': datetime.datetime.now()})

        except Exception, e:
            self.logger.warn("sql error:%s" % e)
            raise e

    def clear_all(self):
        """release db resource
        """
        try:
            self.item_db.close()
        except Exception, ignore:
            self.logger.warn("clear failed:%s" % ignore)


class RoomInfoItemPipeline(BasePipeline):
    """pipeline hande room info item
    """

    def __init__(self, namespace, db_host="127.0.0.1", db_port=5432,
                 db_user="postgres", db_password="titps4gg", db_base="swift"):
        """pipeline of room info item

            Args:
                ignore
        """
        BasePipeline.__init__(self, namespace)
        self.logger.debug("init room info item pipeline")
        try:
            self.item_db = DB(host=db_host, port=db_port, user=db_user,
                              password=db_password, database=db_base)
        except DBError, e:
            self.logger.error("db error %s" % e)

    def process_item(self, item, kwargs):
        """store room inf into rthotel_ctrip_room

            Args:
                item: RoomInfoItem, item
                kwargs: dict, param dict
        """
        if isinstance(item, RoomInfoItem):
            chinese_name = kwargs.get('chinesename')
            # print "room:", item.hotel_code, item.room_id, chinese_name
            self._store_item(item, chinese_name)

    def _store_item(self, item, city_chinese_name):
        """store hotel code into rthotel_ctrip_urlist

            Args:
                item: RoomInfoItem, item
                city_chinese_name: str, chinese name of city
            Raises:
                e: Exception
        """
        try:
            clone_dict = convert_room_info_item_2_dict(item)
            encodestr = json.dumps(clone_dict, ensure_ascii=False)
            selectsql = "SELECT * FROM rthotel_ctrip_roomlist WHERE hotel_id=%(hotel_id)s " \
                        "and room_id=%(room_id)s LIMIT 1"
            if len(self.item_db.execute_query(
                    selectsql, {'hotel_id': item.hotel_code, 'room_id': item.room_id})) >= 1:
                updatesql = "UPDATE rthotel_ctrip_roomlist \
                            SET cityname=%(cityname)s, hotel_id=%(hotel_id)s, \
                            room_id=%(room_id)s, roominfo=%(roominfo)s, \
                            rateinfo=%(rateinfo)s, addtime=%(addtime)s  \
                            WHERE hotel_id=%(hotel_id)s and room_id=%(room_id)s"

                self.item_db.execute_update(updatesql,
                                            {'cityname': city_chinese_name, 'hotel_id': item.hotel_code,
                                            'room_id': item.room_id, 'roominfo': encodestr,
                                            'rateinfo': "", 'addtime': datetime.datetime.now()})

            else:
                insertsql = "INSERT INTO rthotel_ctrip_roomlist \
                (cityname, hotel_id, room_id, roominfo, \
                rateinfo, addtime) \
                VALUES(%(cityname)s, %(hotel_id)s, %(room_id)s, %(roominfo)s, \
                %(rateinfo)s, %(addtime)s)"

                self.item_db.execute_update(insertsql,
                                            {'cityname': city_chinese_name,
                                             'hotel_id': item.hotel_code,
                                             'room_id': item.room_id,
                                             'roominfo': encodestr,
                                             'rateinfo': "",
                                             'addtime': datetime.datetime.now()})

        except Exception, e:
            self.logger.warn("sql error:%s" % e)
            raise e

    def clear_all(self):
        """释放资源
            关闭数据库连接，清空redis中的数据
        """
        try:
            self.item_db.close()
        except Exception, ignore:
            self.logger.warn("clear failed:%s" % ignore)


class HotelInfoItemPipeline(BasePipeline):
    """pipeline handle hotel info item
    """

    def __init__(self, namespace, db_host="127.0.0.1", db_port=5432,
                 db_user="postgres", db_password="titps4gg", db_base="swift"):
        """init method

            Args:
                ignore
        """
        BasePipeline.__init__(self, namespace)
        self.logger.debug("init hotel info item pipeline")
        try:
            self.item_db = DB(host=db_host, port=db_port, user=db_user,
                              password=db_password, database=db_base)
        except DBError, e:
            self.logger.error("db error %s" % e)

    def process_item(self, item, kwargs):
        """process item

            Args:
                item: Item, item processed
                kwargs: dict, param dict
        """
        if isinstance(item, HotelInfoItem):
            # print "hotel info:", item.hotel_code
            self._store_item(item)

    def _store_item(self, item):
        """store item to database

            Args:
                item: Item
        """
        try:
            clone_dict = convert_hotel_info_item_2_dict(item)
            encodestr = json.dumps(clone_dict, ensure_ascii=False)
            selectsql = "SELECT * FROM rthotel_ctrip_hotel WHERE url=%(url)s LIMIT 1"
            if len(self.item_db.execute_query(
                    selectsql, {'url': build_hotel_url(item.hotel_code), })) >= 1:
                updatesql = "UPDATE rthotel_ctrip_hotel \
                            SET city_code=%(city_code)s, hotel_id=%(hotel_id)s, \
                            url=%(url)s, info=%(info)s, \
                            add_time=%(add_time)s  \
                            WHERE url=%(url)s"

                self.item_db.execute_update(updatesql, {'city_code': item.city_code,
                                                        'hotel_id': item.hotel_code,
                                                        'url': build_hotel_url(item.hotel_code),
                                                        'info': encodestr,
                                                        'add_time': datetime.datetime.now()})

            else:
                insertsql = "INSERT INTO rthotel_ctrip_hotel \
                (city_code, hotel_id, url, info, add_time) \
                VALUES(%(city_code)s, %(hotel_id)s, %(url)s, %(info)s, \
                %(add_time)s)"

                self.item_db.execute_update(insertsql,
                                            {'city_code': item.city_code, 'hotel_id': item.hotel_code,
                                             'url': build_hotel_url(item.hotel_code),
                                             'info': encodestr, 'add_time': datetime.datetime.now()})
        except Exception, e:
            self.logger.warn("sql error:%s" % e)
            raise e

    def clear_all(self):
        """释放资源
            关闭数据库连接，清空redis中的数据
        """
        try:
            self.item_db.close()
        except Exception, ignore:
            self.logger.warn("clear failed:%s" % ignore)


class ImageItemPipeline(BasePipeline):

    def __init__(self, namespace, db_host="127.0.0.1", db_port=5432, db_user="postgres",
                 db_password="titps4gg", db_base="swift"):
        BasePipeline.__init__(self, namespace)
        self.logger.debug("init image item pipeline")
        try:
            self.item_db = DB(host=db_host, port=db_port, user=db_user,
                              password=db_password, database=db_base)
        except DBError, e:
            self.logger.error("db error %s" % e)

    def process_item(self, item, kwargs):
        if isinstance(item, ImageItem):
            self._store_item(item)

    def _store_item(self, item):
        try:
            selectsql = """SELECT * FROM rthotel_ctrip_image WHERE
                image_url=%(image_url)s LIMIT 1"""
            if len(self.item_db.execute_query(selectsql, {'image_url': item.image_url})) < 1:
                insertsql = """INSERT INTO rthotel_ctrip_image
                (siteid, image_type, image_text, image_url, addtime)
                VALUES(%(siteid)s, %(image_type)s, %(image_text)s, %(image_url)s, %(addtime)s)"""

                self.item_db.execute_update(insertsql, {'siteid': item.hotel_code, 'image_type': item.image_type,
                                                        'image_text': item.image_text, 'image_url': item.image_url,
                                                        'addtime': datetime.datetime.now()})

        except Exception, e:
            self.logger.warn("sql error:%s" % e)
            raise e