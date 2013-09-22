#!/usr/bin/python2.7
#-*- coding=utf-8 -*-

# Copy Rights (c) Beijing TigerKnows Technology Co., Ltd.


__authors__ = ['"wuyadong" <wuyadong@tigerknows.com>']

import json
import cPickle as pickle

class Task(object):
    '''
    task 中有三类参数：
    一类：request，表明http请求时的参数
    一类: 用于控制流程的控制标签
    '''
    def __init__(self, request, callback, fail_count=0, reason=None,
                 cookie_host=None, cookie_count=20, dns_need=False,
                 max_fail_count=2, kwargs=None):
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
        self.max_fail_count = max_fail_count
        self.dns_need = dns_need

    def to_json(self):
        """dumps to a json object

            Returns:
                json: str, json str
        """
        request = pickle.dumps(self.request)
        return json.dumps({"request": request, "callback": self.callback,
                "fail_count": self.fail_count,
                "reason": self.reason,"cookie_host": self.cookie_host,
                "cookie_count": self.cookie_count,
                "dns_need": self.dns_need,})

    @classmethod
    def from_json(cls, json_str):
        temp_dict = json.loads(json_str)
        for key in ["request", "callback", "fail_count", "reason", "cookie_host",
                    "cookie_count", "dns_need"]:
            if not temp_dict.has_key(key):
                raise KeyError("not exist %s" % key)

        new_request = temp_dict.get('request')
        new_request = pickle.loads(new_request)
        return Task(new_request, temp_dict.get('callback'), temp_dict.get('fail_count'),
                    temp_dict.get('reason'), temp_dict.get('cookie_host'),
                    temp_dict.get('cookie_count'), temp_dict.get('dns_need'))

class Item(object):
    pass
