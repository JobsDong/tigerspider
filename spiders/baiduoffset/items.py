#!/usr/bin/python
# -*- coding: utf-8 -*-

from core.datastruct import Item


class CityItem(Item):
    '''coordinate'''

    def __init__(self, x, y):
        self.x = x
        self.y = y[:-1]
        self.key = self.x+'_'+self.y

    def __str__(self):
        return (self.x+':'+self.y).encode('utf8')


class CoordItem(Item):
    """用于保存小区信息的数据结构
    """
    def __init__(self, x, y, orig_x, orig_y, key):
        self.x = x
        self.y = y
        self.key = key
        self.orig_x = orig_x
        self.orig_y = orig_y
        self.offset_x = float(orig_x) - float(x)
        self.offset_y = float(orig_y) - float(y)
