#!/usr/bin/python
#-*- coding=utf-8 -*-

__author__ = ['"wuyadong" <wuyadong@tigerknows.com>']

from tigerspider.core.datastruct import Item


class TagItem(Item):
    """用于保存标签的数据结构
    """
    def __init__(self, tag, cid, sid):
        self.tag = tag
        self.sid = sid
        self.cid = cid
