#!/usr/bin/python
#-*- coding=utf-8 -*-

__author__ = ['"wuyadong" <wuyadong@tigerknows.com>']

from tigerspider.core.datastruct import Item


class WebItem(Item):
    """描述活动详情页提取出来的数据
    """
    def __init__(self, url, order, description,
                 time_info, price, name):
        self.url = url
        self.order = order
        self.description = description
        self.time_info = time_info
        self.price = price
        self.name = name
