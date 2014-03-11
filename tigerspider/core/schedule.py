#!/usr/bin/python2.7
#-*- coding=utf-8 -*-


"""定义schedule，及控制抓取策略的模块
    ScheduleError: 描述schedule发生内部错误
    BaseSchedule: schedule的基类

    add_schedule_class: 将schedule的类加入

"""

__author__ = ['"wuyadong" <wuyadong@tigerknows.com>']

import inspect
import logging

UUID_INDEPENDENT = 1
UUID_SHARE = 2

logger = logging.getLogger(__name__)

class ScheduleError(Exception):
    """schedule内部的错误类
    """
    pass

class BaseSchedule(object):
    """Schedule的基类，主要负责控制抓取策略的类

        Attributes:
            schedule_classes: 字典，key是路径，value是类对象

    """

    schedule_classes = {}

    def __init__(self, interval=30, max_number=15):
        """ 初始化schedule对象
            Args:
                interval: int 抓取的间隙
                max_number: int 最大抓取并发度
                schedule_type: int 标志是否独享，值可能是：
                    uuid_independent, uuid_share

        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self._interval = interval
        self._max_number = max_number

    @property
    def interval(self):
        return self._interval

    @property
    def max_number(self):
        return self._max_number

    def pop_task(self):
        """取出一个可用的Task
            Returns:
                task Task, 可以使用的task，也有可能为None
        """
        raise NotImplementedError

    def push_new_task(self, task):
        """压入一个新的Task
            Args:
                task Task 任务

        """
        raise NotImplementedError

    def flag_url_haven_done(self, url):
        """标记某一个url已经抓取过
            Args:
                url str 表示一个已经抓取的url

        """
        raise NotImplementedError

    def handle_error_task(self, task):
        """handle error task
            Args:
                task:Task, task
            Returns:
                is_failed:bool, whether is push into fail queue
        """
        raise NotImplementedError


    def fail_task_size(self):
        """get fail task size
            Returns:
                size: int, fail task size
        """
        raise NotImplementedError


    def dumps_all_fail_task(self):
        """dumps all fail task

            Yields:
                task:Task, fail task
        """
        raise NotImplementedError


    def clear_all(self):
        """清空所有的状态

        """
        raise NotImplementedError

def add_schedule_class(path, claz):
    """增加一个schedule类
        Args:
            path: str, 类路径
            claz: ClassType, 类对象

        Raises:
            ScheduleError: 如果schedule以存在
    """
    if BaseSchedule.schedule_classes.has_key(path):
        raise ScheduleError("%s has exists" % path)

    BaseSchedule.schedule_classes[path] = claz

def get_schedule_class(path):
    """获得路径对应的schedule类对象
        Args:
            path: str, 类路径

        Returns:
            schedule: ClassType, 类对象

        Raise:
            ScheduleError: 不存在对应的schedule

    """
    if not BaseSchedule.schedule_classes.has_key(path):
        raise ScheduleError("not exists %s" % path)
    return BaseSchedule.schedule_classes.get(path)

def get_all_schedule_class():
    """ 返回所有schedule的类路径
        Returns:
            schedules:list, [{'path': path, 'description':description, 'args':{...}}]
    """
    schedules = []
    for key, value in BaseSchedule.schedule_classes.iteritems():
        temp_dict = {}
        temp_dict['path'] = key
        temp_dict['description'] = value.__doc__
        temp_dict['args'] = {}
        try:
            args = inspect.getargspec(value.__init__)
            for index in xrange(len(args.defaults)):
                temp_dict['args'][args.args[index + 1]] = args.defaults[index]
        except Exception, e:
            logger.warn("get_all_schedule_class error:%s" % e)
        else:
            schedules.append(temp_dict)
    return schedules
