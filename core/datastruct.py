#!/usr/bin/python2.7
#-*- coding=utf-8 -*-

# Copy Rights (c) Beijing TigerKnows Technology Co., Ltd.

__author__ = 'wuyadong'

class Task(object):
    '''
    task 中有三类参数：
    一类：request，表明http请求时的参数
    一类: 用于控制流程的控制标签
    '''
    def __init__(self, request, callback, fail_count=0, reason=None, cookie_host=None, cookie_count=20, dns_need=False, kwargs=None):
        if kwargs == None:
            self.kwargs = dict()
        else:
            self.kwargs = dict(kwargs)

        self.request = request
        self.callback = callback
        self.fail_count = fail_count
        self.reason = reason
        self.cookie_host = cookie_host
        self.cookie_count = cookie_count
        self.dns_need = dns_need

class Item(object):
    pass
