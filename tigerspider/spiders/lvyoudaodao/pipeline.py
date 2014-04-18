#!/usr/bin/python
#-*- coding=utf-8 -*-

__author__ = ['"wuyadong" <wuyadong@tigerknows.com>']

import csv
import json
from tigerspider.core.spider.pipeline import BasePipeline
from tigerspider.core.redistools import RedisDict, RedisError

from tigerspider.spiders.lvyoudaodao.items import AttractionItem, DescriptionItem


class AttractionItemPipeline(BasePipeline):
    """景点信息的处理流水线
    """
    def __init__(self, namespace, redis_host='127.0.0.1', redis_port=6379, redis_db=1):
        BasePipeline.__init__(self, namespace)
        try:
            temp_namespace = "%s:%s" % (namespace, "temp")
            self.temp_item_dict = RedisDict(temp_namespace, host=redis_host, port=redis_port, db=redis_db)
        except RedisError, e:
            self.logger.error("redis error %s" % e)

        self.logger.info("init attraction pipeline finish")

    def process_item(self, item, kwargs):
        """处理函数
            Args:
                item: item
        """
        if isinstance(item, AttractionItem):
            self.temp_item_dict.set(item.url, item)


class DescriptionItemPipeline(BasePipeline):
    """介绍详情
    """
    def __init__(self, namespace, redis_host='127.0.0.1', redis_port=6379,
                 redis_db=1, csv_file_path="/tmp/daodao.csv"):
        BasePipeline.__init__(self, namespace)
        self._out_file = open(csv_file_path, "wb")
        self._csv_writer = csv.writer(self._out_file, delimiter=',', quotechar='"',
                                      quoting=csv.QUOTE_ALL, lineterminator='\n')
        # 写标题拦
        self._csv_writer.writerow(["Name", "BLon", "BLat", "PlaySpend", "PlaySpendUnit", "Address",
                                   "Tel", "OpenTime", "Rating", "TicketInfo", "ZipCode", "Description", "Comments",
                                   "CommentsNumber", "SortSequence"])
        try:
            temp_namespace = "%s:%s" % (namespace, "temp")
            self.temp_item_dict = RedisDict(temp_namespace, host=redis_host, port=redis_port, db=redis_db)
        except RedisError, e:
            self.logger.error("redis error %s" % e)

        self.logger.info("init description item pipeline")

    def process_item(self, item, kwargs):
        """处理函数
            Args:
                item: item
        """
        if isinstance(item, DescriptionItem):
            if not self.temp_item_dict.has_key(item.url):
                self.logger.error("redis not has this item:%s" % item.url)
            else:
                attraction_item = self.temp_item_dict.get(item.url)
                if attraction_item is not None:
                    self.temp_item_dict.delete(item.url)
                    self._store_item(attraction_item, item)
                else:
                    self.logger.warn("attraction item is none sid:%s" % item.url)

    def _store_item(self, attraction_item, description_item):
        comments = []
        for comment_item in attraction_item.comments:
            comment_dict = {
                "user": comment_item.comment_user.encode('utf-8'),
                "time": comment_item.comment_time.encode('utf-8'),
                "score": comment_item.comment_score.encode('utf-8'),
                "content": comment_item.comment_content.encode('utf-8'),
            }
            comments.append(comment_dict)

        row = [attraction_item.name, attraction_item.longitude, attraction_item.latitude,
               attraction_item.play_spend,
               attraction_item.play_spend_unit,
               attraction_item.address, attraction_item.tel_phone, attraction_item.open_time,
               attraction_item.total_score, attraction_item.ticket_info,
               attraction_item.zipcode, description_item.description,
               json.dumps(comments, ensure_ascii=False),
               attraction_item.hot, attraction_item.seq_sort,
               ]

        row = [item_str.encode('utf-8') if isinstance(item_str, unicode) else item_str for item_str in row]
        self._csv_writer.writerow(row)

    def clear_all(self):
        self._out_file.close()