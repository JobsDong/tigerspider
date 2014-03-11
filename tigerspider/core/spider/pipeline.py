#!/usr/bin/python2.7
#-*- coding=utf-8 -*-


"""用于描述item处理逻辑的组件
    PipelineError: 与pipeline有关的错误
    BasePipeline: 处理item的基类
    EmptyPipeline: 不做任何处理的pipeline
"""

__authors__ = ['"wuyadong" <wuyadong@tigerknows.com>']

import logging

class PipelineError(Exception):
    """Pipeline error
    """

class BasePipeline(object):
    """处理item的基类
    """

    def __init__(self, namespace):
        self.logger = logging.getLogger(self.__class__.__name__)

    def process_item(self, item, kwargs):
        """处理方法
            Args:
                item: Item, 被处理的item对象
                kwargs: dict, 额外需要的参数字典
        """
        raise NotImplementedError

    def clear_all(self):
        """资源释放的方法
        """
        pass


class EmptyPipeline(BasePipeline):
    """什么也不做的pipeline
    """

    def process_item(self, item, kwargs):
        pass

    def clear_all(self):
        pass
