#!/usr/bin/python2.7
#-*- coding=utf-8 -*-

# Copy Rights (c) Beijing TigerKnows Technology Co., Ltd.

"""主要是描述公共抓取流程的类
    SpiderError: spider发生的内部错误
    BaseSpider: 描述流程的基类
    add_spider_class(): 注册一个spider类
    get_all_spider_class(): 获得所有注册的类
    get_spider_class(): 获得某一个spider类
"""

__authors__ = ['"wuyadong" <wuyadong@tigerknows.com>']

import uuid
import logging

from tigerspider.core.spider.parser import ParserError
from tigerspider.core.spider.pipeline import PipelineError

class SpiderError(Exception):
    """Spider error
    """

class BaseSpider(object):
    """用于描述spider公共流程的类
        Attributes:
            start_tasks: list, 表示最初的种子任务
            parsers: dict, 表示spider对应的所有解析组件
            pipelines: dict, 表示spider对应的所有处理组件
            spider_classes: dict, 表示所有的注册的spider class
    """
    start_tasks = []
    parsers = {}
    pipelines = {}
    spider_classes = {}

    def __init__(self, crawl_schedule, namespace=None, **kwargs):
        """初始化spider
            Args:'
                crawl_schedule: CrawlSchedule, 是策略对象
        """
        self._namespace = str(uuid.uuid4()) if not namespace else namespace
        self.logger = logging.getLogger(self.__class__.__name__)
        self._crawl_schedule = crawl_schedule
        self._is_cleared = False
        self._kwargs = kwargs
        self._clone_parsers = {}
        self._clone_pipelines = {}

        for parser_name, parser_claz in self.parsers.iteritems():
            parser_kwargs =  dict([(arg_name[len(parser_name) + 1:], arg_value)
                              for arg_name, arg_value
                              in kwargs.iteritems()
                              if arg_name.startswith(parser_name + "_")])

            self._clone_parsers[parser_name] = parser_claz(self._namespace, **parser_kwargs)

        for pipeline_name, pipeline_claz in self.pipelines.iteritems():
            pipeline_kwargs =  dict([(arg_name[len(pipeline_name) + 1:], arg_value)
                              for arg_name, arg_value
                              in kwargs.iteritems()
                              if arg_name.startswith(pipeline_name + "_")])
            self._clone_pipelines[pipeline_name] = pipeline_claz(self._namespace, **pipeline_kwargs)

    @property
    def spider_kwargs(self):
        kwargs = self._kwargs
        kwargs.update({'namespace': self._namespace})
        return kwargs

    @property
    def crawl_schedule(self):
        return self._crawl_schedule

    def parse(self, task, input_file):
        """用于解析response的结果
            Args:
                task: Task, 任务的描述
                input_file: File, 文件对象
            Returns:
                iterator: iter，一个迭代器 or None
            Raises:
                error:ParserError,
        """
        if self._is_cleared:
            return None

        if self._clone_parsers.has_key(task.callback):
            try:
                item_or_task_iterator = self._clone_parsers[task.callback].parse(task, input_file)
            except ParserError, e:
                raise e
            except Exception, e:
                raise e
            else:
                return item_or_task_iterator
        else:
            self.logger.error("has no callback:%s" % task.callback)
            raise Exception("parser error:%s, callback:%s" % ("not exists callback", task.callback))


    def handle_item(self, item, kwargs):
        """处理item的函数
            Args:
                item: Item, 表示解析出的结果
                kwargs: dict, 表示额外带的参数字典
            Raises:
                error: PipelineError
        """
        if self._is_cleared:
            return

        if self._clone_pipelines.has_key(item.__class__.__name__):
            try:
                self._clone_pipelines[item.__class__.__name__].process_item(item, kwargs)
            except Exception, e:
                self.logger.error("process item error, %s" % e)
                raise PipelineError("process item error:%s, item:%s" % (e, item))
        else:
            self.logger.error("has not this pipeline:%s" % item.__class__.__name__)
            raise PipelineError("process item error:%s, item:%s" % ("not exists pipeline", item))

    def clear_all(self):
        """释放spider中的资源
        """
        self._is_cleared = True
        for _, parser in self._clone_parsers.iteritems():
            try:
                parser.clear_all()
            except Exception, e:
                self.logger.warn("clear parser:%s resource error:%s" % (parser.__name__, e))

        for _, pipeline in self._clone_pipelines.iteritems():
            try:
                pipeline.clear_all()
            except Exception, e:
                self.logger.warn("clear pipeline:%s resource error:%s" % (pipeline.__name__, e))
        try:
            self._crawl_schedule.clear_all()
        except Exception, e:
            self.logger.warn("clear crawl schedule error:%s" % e)


def add_spider_class(path, clz):
    """增加一个spider类
        Args:
            path, str, class的路径
            clz, ClassType, 类对象
        Raises:
            SpiderError: 当发生错误是产生
    """
    if BaseSpider.spider_classes.has_key(path):
        raise SpiderError("%s has exists" % path)

    BaseSpider.spider_classes[path] = clz

def get_all_spider_class():
    """获取所有的spider类
        Returns
            spiders: list, 类路径列表
    """
    spiders = []
    for key, clz in BaseSpider.spider_classes.iteritems():
        temp_dict = {}
        temp_dict['path'] = key
        temp_dict['description'] = clz.__doc__
        spiders.append(temp_dict)

    return spiders

def get_spider_class(path):
    """获取对应路径的类对象
        Args:
            path: str, 类路径
        Returns:
            clz: ClassType, 对应的类对象
        Raises:
            SpiderError: 当发生错误的时候

    """
    if not BaseSpider.spider_classes.has_key(path):
        raise SpiderError("not exists %s" % path)

    return BaseSpider.spider_classes.get(path)
