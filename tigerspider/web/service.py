#!/usr/bin/python2.7
#-*- coding=utf-8 -*-

# Copy Rights (c) Beijing TigerKnows Technology Co., Ltd.
from tigerspider.web import apis, pages


__authors__ = ['"wuyadong" <wuyadong@tigerknows.com>']

import threading
import json
import os
from tornado import ioloop, web

from tigerspider.core.util import unicode2str_for_dict


class WebService(object):
    _instance_lock = threading.Lock()

    @staticmethod
    def instance():
        if not hasattr(WebService, "_instance"):
            with WebService._instance_lock:
                setattr(WebService, "_instance", WebService())
        return getattr(WebService, "_instance")

    def __init__(self):
        self._handlers = [(r"/api/(.*)", ApiHandler),
                            (r"/web/(.*)", WebHandler)]
        self._settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), "template"),
            static_path=os.path.join(os.path.dirname(__file__), "static"))

    def start(self, port=3333):
        self.application = web.Application(self._handlers, **self._settings)
        self.application.listen(port)
        ioloop.IOLoop.instance().start()

class WebHandler(web.RequestHandler):
    """用于web界面的处理器
    """
    def get(self, *args, **kwargs):
        return self.post(*args, **kwargs)

    def post(self, *args, **kwargs):
        path = self.request.path
        if not pages.page_route.get_page_methods().has_key(path):
            template_path, template_param = pages.not_found(path)
        else:  # 专注于注册过的页面
            web_method = pages.page_route.get_page_methods().get(path)
            params = build_params(self.request.arguments, self.request.body)
            template_path, template_param = web_method(params)

        if template_param:
            self.render(template_path, **template_param)
        else:
            self.render(template_path)


class ApiHandler(web.RequestHandler):
    def get(self, *args, **kwargs):
        return self.post(*args, **kwargs)

    def post(self, *args, **kwargs):
        path = self.request.path
        if not apis.api_route.get_api_routes().has_key(path):
            result = apis.not_found(path)
        else:
            method = apis.api_route.get_api_routes()[path]
            params = build_params(self.request.arguments, self.request.body)
            result = method(params)
        self.set_header("Content-Type", "application/json; charset=utf8")
        self.write(result)

def build_params(arguments, body):
    """从url，query和body中获取参数
        Args:
            arguments:dict,query上的参数字典
            body:str,body中带的字符串
        Returns:
            params:dict, 完整的参数字典
    """
    params = {}
    if arguments:
        for key, value in arguments.items():
            key = key if not isinstance(key, unicode) else str(key)
            value = value if not isinstance(value, unicode) else str(value)
            params[key] = value[0]

    if body:
        jsonParam = json.loads(body)
        params.update(unicode2str_for_dict(jsonParam))
    return params
