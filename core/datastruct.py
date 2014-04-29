#!/usr/bin/python2.7
#-*- coding=utf-8 -*-


__authors__ = ['"wuyadong" <wuyadong@tigerknows.com>']


class HttpTask(object):
    """
    task 中有三类参数：
    一类：request，表明http请求时的参数
    一类: 用于控制流程的控制标签
    """
    def __init__(self, request, callback, fail_count=0, reason=None,
                 cookie_host=None, cookie_count=20, dns_need=False,
                 proxy_need=False, max_fail_count=2, kwargs=None):
        if kwargs is None:
            self.kwargs = dict()
        else:
            self.kwargs = dict(kwargs)

        self.request = request
        self.callback = callback
        self.fail_count = fail_count
        self.reason = reason
        self.cookie_host = cookie_host
        self.cookie_count = cookie_count
        self.max_fail_count = max_fail_count
        self.dns_need = dns_need
        self.proxy_need = proxy_need


class FileTask(object):
    """file task
    """
    def __init__(self, file_path, callback, fail_count=0,
                 reason=None, max_fail_count=2, kwargs=None):
        """初始化函数
            Args:
                input_file: File, 文件对象
                callback: str, 回调函数
                fail_count: int , 错误次数
                reason: str, 错误原因
                max_fail_count: int, 最大失败次数
                kwargs: dict, 参数字典
        """
        if kwargs is None:
            self.kwargs = dict()
        else:
            self.kwargs = dict(kwargs)

        self.file_path = file_path
        self.callback = callback
        self.fail_count = fail_count
        self.reason = reason
        self.max_fail_count = max_fail_count


class Item(object):
    pass
