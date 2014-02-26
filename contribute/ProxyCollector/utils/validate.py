#!/usr/bin/python
#-*- coding=utf-8 -*-

"""用于测试proxy的有效性的模块
"""

from __future__ import absolute_import

__author__ = ['"wuyadong" <wuyadong@tigerknows.com>']

import requests
import functools
from collections import defaultdict
import datetime
from config import main_config
from tornado import httpclient
from tornado import ioloop, gen

httpclient.AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient")


def validate_proxy(host, port):
    """验证代理，计算成功率
        Args:
            host: str, proxy host
            port: int, proxy int
        Returns:
            success_perc: float, 成功率
    """
    # 1. 访问网页
    fail_count = success_count = 0
    proxy = {"http": "http://%s:%d" % (host, port)}
    for test_web in main_config.TEST_WEBS:
        url = test_web['url']
        connect_timeout = test_web['connect_timeout']

        try:
            r = requests.get(url, timeout=connect_timeout, proxies=proxy)
        except requests.RequestException, e:
            print e
            fail_count += 1
        else:
            if r.status_code == 200:
                success_count += 1
            else:
                fail_count += 1

    # 2. 统计结果
    success_percent = float(success_count) / (success_count + fail_count)
    return success_percent


def validate_proxys(proxys=None, max_clients=50, interval=500):
    """验证许多代理，是否有效, 进行过优化， 效率会很高
        Args:
            proxys: list, proxy list
            max_clients: int, 最大并发度
            interval: int, 访问间隔
        Returns:
            success_perc: list, [success_percentage]
    """
    # 生成http_request列表
    if proxys is None:
        proxys = list()
    http_requests = _build_request_list(proxys)
    http_request_length = len(http_requests)
    # 计数器
    counters = {
        "current_client": 0,
        "current_request_index": 0,
    }
    # 结果集
    results = defaultdict(functools.partial(defaultdict, int))

    @gen.coroutine
    def _fetch():
        if counters['current_request_index'] < http_request_length:
            # 当最大并发度还没有饱和
            if counters['current_client'] < max_clients:
                # 获取http请求
                http_request = http_requests[counters['current_request_index']]
                counters['current_request_index'] += 1
                client = httpclient.AsyncHTTPClient()

                def _handle_response(response):
                    print response.request.url, response.code, response.error
                    if response.code == 200 and response.error is None:
                        results[(http_request.proxy_host, http_request.proxy_port)]['success'] += 1
                    else:
                        results[(http_request.proxy_host, http_request.proxy_port)]['fail'] += 1
                    counters['current_client'] -= 1

                # 访问网页
                counters['current_client'] += 1
                try:
                    client.fetch(http_request, callback=_handle_response)
                except Exception, e:
                    print e
                # 加入下一次循环
                ioloop.IOLoop.instance().add_timeout(datetime.timedelta(milliseconds=interval), _fetch)

            # 当最大并发度已经饱和了
            else:
                ioloop.IOLoop.instance().add_timeout(datetime.timedelta(milliseconds=interval), _fetch)

        else:
            print counters['current_client']
            if counters['current_client'] > 0:
                ioloop.IOLoop.instance().add_timeout(datetime.timedelta(milliseconds=interval), _fetch)
            else:
                ioloop.IOLoop.instance().stop()

    # 开始并发访问
    ioloop.IOLoop.instance().add_callback(_fetch)
    ioloop.IOLoop.instance().start()

    # 解析结果
    success_percentages = []
    for proxy_host, proxy_port in proxys:
        result = results[(proxy_host, proxy_port)]
        success_percentage = float(result['success']) / (result['success'] + result['fail'])
        success_percentages.append(success_percentage)

    return success_percentages


def _build_request_list(proxys):
    """够找request列表
        Args:
            proxys: list, [proxy]
        Returns:
            requests: list, [request]
    """
    http_requests = []

    for proxy in proxys:
        proxy_host = proxy[0]
        proxy_port = proxy[1]
        for test_web in main_config.TEST_WEBS:
            url = test_web['url']
            connect_timeout = test_web['connect_timeout']
            request_timeout = test_web['request_timeout']
            headers = main_config.DEFAULT_HEADER
            http_request = httpclient.HTTPRequest(url, proxy_host=proxy_host, proxy_port=proxy_port,
                                                  connect_timeout=connect_timeout, request_timeout=request_timeout,
                                                  headers=headers)
            http_requests.append(http_request)

    return http_requests


if __name__ == "__main__":
    print validate_proxy("120.202.249.230", 80)
    print validate_proxy("123.150.105.12", 8080)
    print validate_proxys([("120.202.249.230", 80)])