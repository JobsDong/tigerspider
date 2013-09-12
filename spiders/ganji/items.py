#!/usr/bin/python
# -*- coding: utf-8 -*-

from core.datastruct import Item


class CityItem(Item):
    '''保存城市'''

    def __init__(self, chinese_name, city_code):
        self.city_code = city_code
        self.chinese_name = chinese_name

    def __str__(self):
        return (self.city_code+':'+self.chinese_name).encode('utf8')


class CommunityItem(Item):
    """用于保存小区信息的数据结构
    """
    def __init__(self, city_name, community_name, address):
        self.city = city_name
        self.community = community_name
        self.address = address
