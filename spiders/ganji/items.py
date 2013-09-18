#!/usr/bin/python
# -*- coding: utf-8 -*-

"""用于赶集网数据抓取的数据结构
    CityItem: 保存城市信息的类
    CommunityItem: 保存小区信息的类
"""

__author__ = ['"wuyadong" <wuyadong@tigerknows.com>',
              '"zhangxuanyi" <zhangxuanyi@tigerknows.com>']

from core.datastruct import Item

class CityItem(Item):
    """保存城市信息的类
    """
    def __init__(self, chinese_name, city_code):
        """初始化函数
            Args:
                chinese_name: str, 中文名
                city_code: str, city code
        """
        self.city_code = city_code
        self.chinese_name = chinese_name

    def __str__(self):
        return "%s:%s" % (self.city_code.encode('utf-8'),
                          self.chinese_name.encode("utf-8"))

class CommunityItem(Item):
    """用于保存小区信息的数据结构
    """
    def __init__(self, city_name, community_name, address):
        """初始化函数
            Args:
                city_name: str, 城市名
                community_name: str, 小区名
                address: str, 小区地址
        """
        self.city = city_name
        self.community = community_name
        self.address = address
