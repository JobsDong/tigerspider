#!/usr/bin/python
#-*- coding=utf-8 -*-

__author__ = ['"wuyadong" <wuyadong@tigerknows.com>']

from core.datastruct import Item


class AttractionItem(Item):
    """用于保存景点的数据结构
    """
    def __init__(self, url, name, play_spend, play_spend_unit, address,
                 tel_phone, open_time,
                 total_score, ticket_info, hot, longitude, latitude,
                 seq_sort, comments, zipcode):
        self.url = url
        self.name = name
        self.play_spend = play_spend
        self.play_spend_unit = play_spend_unit
        self.address = address
        self.tel_phone = tel_phone
        self.open_time = open_time
        self.total_score = total_score
        self.ticket_info = ticket_info
        self.hot = hot
        self.longitude = longitude
        self.latitude = latitude
        self.seq_sort = seq_sort
        self.comments = comments
        self.zipcode = zipcode


class DescriptionItem(Item):
    """详情数据结构
    """
    def __init__(self, url, description):
        self.url = url
        self.description = description


class CommentItem(Item):
    """评论数据结构
    """
    def __init__(self, comment_user, comment_time,
                 comment_score, comment_content):
        self.comment_user = comment_user
        self.comment_time = comment_time
        self.comment_score = comment_score
        self.comment_content = comment_content