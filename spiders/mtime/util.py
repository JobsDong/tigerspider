#!/usr/bin/python2.7
#-*- coding=utf-8 -*-

# Copy Rights (c) Beijing TigerKnows Technology Co., Ltd.

__authors__ = ['"wuyadong" <wuyadong@tigerknows.com>']

def item2dict(item):
    """讲item转换层dict
        Args:
            item:Item, item对象
        Returns:
            clone_dict:dict, 字典
    """
    clone_dict = {}
    for key, value in item.__dict__.items():
        if key != "url" and key != "city_code" and key != "start_time":
            clone_dict[key] = value if not isinstance(value, unicode) \
                else value.encode("utf-8")

    return clone_dict
