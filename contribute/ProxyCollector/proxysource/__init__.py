#!/usr/bin/python
#-*- coding=utf-8 -*-

"""一个proxy来源网站的开发约定：
1. 支持proxy的持久化，内容存储在data文件夹中，且一个文件，文件名是模块名
2. python脚本必须支持这几个功能：获取所有代理，更新代理
必须要实现方法：

get_proxys(): 返回[(host, port),(host, port),...]
update_proxy(start_date=None, end_date=None, threshold=0.7): 用于更新代理列表
例子参见itmop.py
"""

__author__ = ['"wuyadong" <wuyadong@tigerknows.com>']
