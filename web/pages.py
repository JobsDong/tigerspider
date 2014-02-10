#!/usr/bin/python2.7
#-*- coding=utf-8 -*-

# Copy Rights (c) Beijing TigerKnows Technology Co., Ltd.

"""主要描述抓取系统中的页面控制
"""

__authors__ = ['"wuyadong" <wuyadong@tigerknows.com>']

from core.schedule import get_all_schedule_class
from core.spider.spider import get_all_spider_class
from core.worker import get_all_workers, get_worker_statistic
from core.record import RecorderManager


class page_route(object):
    """将uri对应于某一函数的类
    """

    _page_methods = {}

    def __init__(self, uri):
        self._uri = uri

    def __call__(self, page_method):
        self._page_methods[self._uri] = page_method

    @classmethod
    def get_page_methods(cls):
        """获取所有的page_method
            Returns:
                page_methods:dict, {uri,method}
        """
        return cls._page_methods


@page_route(r"/web/homepage.html")
def get_homepage(params):
    """获取homepage
    """
    return "homepage.html", None


@page_route(r"/web/schedule.html")
def get_schedule(params):
    """获取schedule
        Args:
            params:dict 参数字典
        Returns:
            path, {}: 路径和参数字典
    """
    schedules = get_all_schedule_class()
    return "schedule.html", {'schedules': schedules}

@page_route(r"/web/spider.html")
def get_spider(params):
    """获取spider
        Args:
            params:dict 参数字典
        Returns:
            path, {}: 路径和参数字典
    """
    return "spider.html", {"spiders": get_all_spider_class()}


@page_route(r"/web/statistic.html")
def get_statistic(params):
    """获取统计信息
        Args:
            params:dict 参数字典
        Returns:
            path, {}: 路径和参数字典
    """
    worker_name = params.get('worker_name')

    worker_statistic = get_worker_statistic(worker_name)
    return "statistic.html", {'statistic': worker_statistic,}

@page_route(r"/web/worker.html")
def get_worker(params):
    """获取worker
        Args:
            params:dict 参数字典
        Returns:
            path, {}: 路径和参数字典
    """
    workers = get_all_workers()
    fail_workers = RecorderManager.instance().get_last_fail_worker()
    return "worker.html", {'workers': workers, 'fail_workers': fail_workers}

def not_found(path):
    """表示not found结果
        Args:
            path: str, 路径
        Returns:
            template_path, template_param: 二元组，表示路径和参数
    """
    return "notfound.html", {'path':path}

