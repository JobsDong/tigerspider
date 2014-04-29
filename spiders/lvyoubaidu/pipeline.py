#!/usr/bin/python
#-*- coding=utf-8 -*-

__author__ = ['"wuyadong" <wuyadong@tigerknows.com>']

import csv
import datetime
import json
from core.spider.pipeline import BasePipeline
from core.redistools import RedisDict, RedisError
from spiders.lvyoubaidu.items import AttractionItem, CommentListItem


class AttractionItemPipeline(BasePipeline):
    """处理景点信息的pipeline
    """
    def __init__(self, namespace, redis_host="127.0.0.1",
                 redis_port=6379, redis_db=0):
        BasePipeline.__init__(self, namespace)
        try:
            temp_namespace = "%s:%s" % (namespace, "temp")
            self.temp_item_dict = RedisDict(temp_namespace,
                                            host=redis_host,
                                            port=redis_port, db=redis_db)
        except RedisError, e:
            self.logger.error("redis error %s" % e)

        self.logger.info("init AttractionItemPipeline")

    def process_item(self, item, kwargs):
        """处理函数
        """
        if isinstance(item, AttractionItem):
            self.temp_item_dict.set(item.sid, item)

    def clear_all(self):
        pass


class CommentListItemPipeline(BasePipeline):
    """处理景点评论的pipeline
    """
    def __init__(self, namespace, redis_host='127.0.0.1', redis_port=6379,
                 redis_db=0, csv_file_path="/tmp/baidu.csv"):
        BasePipeline.__init__(self, namespace)
        self._out_file = open(csv_file_path, "wb")
        self._csv_writer = csv.writer(self._out_file, delimiter=',', quotechar='"',
                                      quoting=csv.QUOTE_ALL, lineterminator='\n')
        # 写标题拦
        self._csv_writer.writerow(["Sid", "Name", "BLon", "BLat",
                                   "PlaySpend", "PlaySpendUnit", "Address",
                                   "Tel", "OpenTime", "Rating", "TicketInfo",
                                   "ZipCode", "Description", "Comments",
                                   "CommentsNumber", "SortSequence",
                                   "Traffic", "Tips"])

        try:
            temp_namespace = "%s:%s" % (namespace, "temp")
            self.temp_item_dict = RedisDict(temp_namespace, host=redis_host,
                                            port=redis_port, db=redis_db)
        except RedisError, e:
            self.logger.error("redis error %s" % e)
            raise e

        self.logger.info("init Comment list item pipeline")

    def process_item(self, item, kwargs):
        """处理函数
        """
        if isinstance(item, CommentListItem):
            if not self.temp_item_dict.has_key(item.sid):
                self.logger.error("redis not has this item:%s" % item.sid)
            else:
                attraction_item = self.temp_item_dict.get(item.sid)
                if attraction_item is not None:
                    self.temp_item_dict.delete(item.sid)
                    self._store_item(attraction_item, item)
                else:
                    self.logger.warn("attraction item is none sid:%s" % item.sid)

    def _store_item(self, attraction_item, comment_list_item):
        """用于保存item到csv文件中
            Args:
                attraction_item: AttractionItem
                comment_list_item: CommentListItem
        """
        comments = []
        for comment_item in comment_list_item.comment_list:
            comment_dict = {
                "user": comment_item.comment_user.encode('utf-8'),
                "time": datetime.datetime.
                fromtimestamp(comment_item.comment_time).
                strftime("%Y-%m-%d %H:%M:%S"),
                "score": comment_item.comment_score,
                "content": comment_item.comment_content.encode('utf-8'),
            }
            comments.append(comment_dict)

        row = [attraction_item.sid, attraction_item.name,
               attraction_item.longitude, attraction_item.latitude,
               attraction_item.play_spend,
               attraction_item.play_spend_unit,
               attraction_item.address, attraction_item.tel_phone,
               attraction_item.open_time,
               attraction_item.total_score, attraction_item.ticket_info,
               "", attraction_item.preview,
               json.dumps(comments, ensure_ascii=False),
               attraction_item.hot, attraction_item.seq_sort,
               attraction_item.traffic, attraction_item.tips,
               ]

        row = [item_str.encode('utf-8') if isinstance(item_str, unicode)
               else item_str for item_str in row]
        self._csv_writer.writerow(row)

    def clear_all(self):
        self._out_file.close()