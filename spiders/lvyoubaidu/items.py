#!/usr/bin/python
#-*- coding=utf-8 -*-

__author__ = ['"wuyadong" <wuyadong@tigerknows.com>']

from tigerspider.core.datastruct import Item


class AttractionItem(Item):
    """用于保存景点的数据结构
    """
    def __init__(self, sid, name, play_spend, play_spend_unit, address,
                 tel_phone, open_time,
                 total_score, ticket_info, preview, hot, longitude,
                 latitude, seq_sort, traffic, tips):
        self.sid = sid
        self.name = name
        self.play_spend = play_spend
        self.play_spend_unit = play_spend_unit
        self.address = address
        self.tel_phone = tel_phone
        self.open_time = open_time
        self.total_score = total_score
        self.ticket_info = ticket_info
        self.preview = preview
        self.hot = hot
        self.longitude = longitude
        self.latitude = latitude
        self.seq_sort = seq_sort
        self.traffic = traffic
        self.tips = tips


class CommentListItem(Item):
    """保存一大波评论的数据结构
    """
    def __init__(self, sid, comment_list):
        self.sid = sid
        self.comment_list = comment_list


class CommentItem(Item):
    """保存一个评论的数据结构
    """
    def __init__(self, comment_user, comment_time,
                 comment_score, comment_content):
        self.comment_user = comment_user
        self.comment_time = comment_time
        self.comment_score = comment_score
        self.comment_content = comment_content