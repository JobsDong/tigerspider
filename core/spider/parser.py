#!/usr/bin/python2.7
#-*- coding=utf-8 -*-

# Copy Rights (c) Beijing TigerKnows Technology Co., Ltd.

"""用于描述解析的过程的组件
    BaseParser: 解析的基类
"""

__authors__ = ['"wuyadong" <wuyadong@tigerknows.com>']

from core.util import logging

class BaseParser(object):
    """用于描述解析的基类
    """

    def __init__(self, namespace):
        self.logger = logging.getLogger(self.__class__.__name__)

    def parse(self, task, response):
        """解析的方法
            Args:
                task:Task, 描述任务的对象
                response:HTTPResponse, 描述网页结果
        """
        raise NotImplementedError

    def clear_all(self):
        """释放资源的操作
        """
        pass
