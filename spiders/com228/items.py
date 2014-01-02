#!/usr/bin/python
#-*- coding=utf-8 -*-

__author__ = ['"wuyadong" <wuyadong@tigerknows.com>']


from core.datastruct import Item


class ActivityItem(Item):
    """描述活动的Item
    """
    def __init__(self, order, name, url, start_time, end_time, address, price,
                 pic_url, description, tag, city_code):
        self.order = order
        self.name = name
        self.url = url
        self.start_time = start_time
        self.end_time = end_time
        self.address = address
        self.price = price
        self.pic_url = pic_url
        self.description = description
        self.tag = tag
        self.city_code = city_code


class WebItem(Item):
    """描述活动详情页提取出来的数据
    """
    def __init__(self, order, description, pic_url, time_info):
        self.order = order
        self.description = description
        self.pic_url = pic_url
        self.time_info = time_info


class PictureItem(Item):
    """用于保存图片信息的item
    """
    def __init__(self, picture, path):
        """初始化函数
            Args:
                picture: 二进制，图片内容
                path: str, 图片路径
        """
        self.picture = picture
        self.path = path