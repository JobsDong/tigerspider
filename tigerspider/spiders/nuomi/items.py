#!/usr/bin/python2.7
#-*- coding=utf-8 -*-


"""此处定义了糯米网需要使用的item类
    CityItem: 保存城市的类
    DealItem: 保存deal信息的类
    PictureItem: 保存picture信息的类
"""

__authors__ = ['"wuyadong" <wuyadong@tigerknows.com>']

from tigerspider.core.datastruct import Item


class CityItem(Item):
    """负责保存城市信息的类
    """
    def __init__(self, chinese_name, english_name, city_code):
        """初始化函数
            Args:
                chinese_name: str, 中文名
                english_name: str, 英文名字
                city_code: str, city代码
        """
        self.city_code = city_code
        self.chinese_name = chinese_name
        self.english_name = english_name


class DealItem(Item):
    """负责保存deal信息的类
    """
    def __init__(self, price, city_code, dealid, url, name,
                 discount_type, start_time,
                 end_time, discount, original_price, noticed,
                 pictures, description,
                 deadline, short_desc, content_text, content_pic,
                 purchased_number,
                 m_url, appointment, place, save, remaining, limit,
                 refund, contact, tiny):
        """初始化函数
            Args:
                略
        """
        self.tiny = tiny
        self.save = save
        self.remaining = remaining
        self.limit = limit
        self.refund = refund
        self.price = price
        self.city_code = city_code
        self.dealid = dealid
        self.url = url
        self.name = name
        self.discount_type = discount_type
        self.start_time = start_time
        self.end_time = end_time
        self.discount = discount
        self.original_price = original_price
        self.noticed = noticed
        self.pictures = pictures
        self.description = description
        self.deadline = deadline
        self.short_desc = short_desc
        self.content_text = content_text
        self.content_pic = content_pic
        self.purchased_number = purchased_number
        self.m_url = m_url
        self.appointment = appointment
        self.place = place
        self.contact = contact


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