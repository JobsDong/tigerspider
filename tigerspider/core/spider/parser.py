#!/usr/bin/python2.7
#-*- coding=utf-8 -*-


"""用于描述解析的过程的组件
    ParserError: 与Parser有关的错误
    BaseParser: Parser的基类
"""

__authors__ = ['"wuyadong" <wuyadong@tigerknows.com>']

import logging

class ParserError(Exception):
    """Parser error
    """

class BaseParser(object):
    """用于描述解析的基类
    """

    def __init__(self, namespace):
        self.logger = logging.getLogger(self.__class__.__name__)

    def parse(self, task, input_file):
        """解析的方法
            Args:
                task:Task, 描述任务的对象
                input_file: File, 文件对象（可以是网络文件，也可以是本地文件对象）
        """
        raise NotImplementedError

    def clear_all(self):
        """释放资源的操作
        """
        pass

