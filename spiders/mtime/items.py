#!/usr/bin/python2.7
#-*- coding=utf-8 -*-

# Copy Rights (c) Beijing TigerKnows Technology Co., Ltd.

"""描述mtime解析中所要使用到的数据结构
"""

__authors__ = ['"wuyadong" <wuyadong@tigerknows.com>']

from core.datastruct import Item

class RealInfoItem(Item):
    """定义RealInfo的数据结构
    """
    def __init__(self, show_id, movie_id, cinema_id, tag,
                 price, version, language, running_time,
                 url, city_code, start_time):
        """初始化函数
            Args:
                略
        """
        self.show_id = show_id
        self.movie_id = movie_id
        self.cinema_id = cinema_id
        self.tag = tag
        self.price = price
        self.version = version
        self.language = language
        self.running_time = running_time
        self.url = url
        self.city_code = city_code
        self.start_time = start_time