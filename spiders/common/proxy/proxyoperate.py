#!/usr/bin/python2.7
#-*- coding=utf-8 -*-

# Copy Rights (c) Beijing TigerKnows Technology Co., Ltd.

__authors__ = ['"wuyadong" <wuyadong@tigerknows.com>']

import logging
import functools
from tornado.httpclient import HTTPRequest, AsyncHTTPClient
from tornado.gen import coroutine, Task
from tornado.ioloop import IOLoop

from core.redistools import RedisQueue
from core.proxy import Proxy, DEFAULT_PROXY_NAMESPACE

from spiders.common.proxy import it173, itmop

AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient")
proxy_logger = logging.getLogger("spiders-common-proxy")
client = AsyncHTTPClient()

def operate(operate_name="help"):
    """operate command parser for proxy
        Args:
            operate_name: str, operate name
    """
    if operate_name == "help":
        print "--operate operate name for mtime"
        print "   loadtask: load start task for mtime"
    elif operate_name == "update":
        print "update proxy list begin"
        proxy_logger.info("update proxy list begin")
        update_proxys()
        proxy_logger.info("update proxy list end")
        print "update proxy list end"
    else:
        print "error operate for proxy"

def update_proxys():
    # get itmop proxy
    itmop_proxys = []
    try:
        itmop_proxys = itmop.get_proxy_from_itmop()
    except Exception, e:
        proxy_logger.error("itmop proxy error:%s" % e)

    print "itmop proxy:", len(itmop_proxys)

    # get it173 proxy
    it173_proxys = []
    try:
        it173_proxys = it173.get_proxy_from_it173()
    except Exception, e:
        proxy_logger.error("it173 proxy error:%s" % e)

    print "it173 proxy:", len(it173_proxys)

    # get former proxy
    former_proxys = _get_former_proxy_from_redis()

    print "former proxy:", len(former_proxys)

    # union
    proxys = set(former_proxys).union(set(itmop_proxys)).union(set(it173_proxys))

    # test validation
    IOLoop.instance().add_callback(functools.partial(_test_and_put, proxys))
    IOLoop.instance().start()

def _push_proxys_to_redis(proxys, namespace=DEFAULT_PROXY_NAMESPACE, host="localhost", port=6379, db=0):
    try:
        queue = RedisQueue(namespace, host=host, port=port, db=db)
        for proxy in proxys:
            if isinstance(proxy, Proxy):
                queue.push(proxy)
    except Exception, e:
        proxy_logger.error("get former proxys failed:%s" % e)


def _get_former_proxy_from_redis(namespace=DEFAULT_PROXY_NAMESPACE, host="localhost", port=6379, db=0):
    """get former proxys from redis
        Args:
            namespace: str, namespace
            host: str, redis host
            port: int, redis port
            db: int, redis db
        Returns;
            proxys: list, list of proxy
    """
    former_proxys = []
    try:
        queue = RedisQueue(namespace, host=host, port=port, db=db)
        while queue.size() > 0:
            proxy = queue.pop()
            former_proxys.append(proxy)
    except Exception, e:
        proxy_logger.error("get former proxys failed:%s" % e)
    finally:
        return former_proxys

@coroutine
def _test_validation(proxys, max_process=5, interval=100):
    """test validation for proxys

        Args:
            proxys: set, proxy set
            max_process: int, max process
            interval: int, fetch interval

        Returns:
            final_proxys: list, proxy list
    """
    test_requests = [
            HTTPRequest("http://www.mtime.com", connect_timeout=5, request_timeout=10),
            HTTPRequest("http://www.nuomi.com.", connect_timeout=5, request_timeout=10),
            HTTPRequest("http://www.55tuan.com", connect_timeout=5, request_timeout=10),
            HTTPRequest("http://www.meituan.com", connect_timeout=5, request_timeout=10),
            HTTPRequest("http://www.ganji.com", connect_timeout=5, request_timeout=10),
            ]

    final_proxys = []

    for proxy in proxys:
        tasks = []

        print 'test proxy: %s begin' % proxy.host
        for request in test_requests:
            request.proxy_host = proxy.host
            request.proxy_port = proxy.port
            if proxy.username is not None:
                request.proxy_username = proxy.username
                request.proxy_port = proxy.passwd

            tasks.append(Task(client.fetch, request))

        resps = yield tasks
        fail_counter = 0
        for resp in resps:
            if resp.code != 200 and resp.error != None:
                fail_counter += 1
        if fail_counter < len(test_requests) / 2:
            print "valiade proxy:%s, count:%s" % (proxy.host, fail_counter)
            final_proxys.append(proxy)
        else:
            print "invaliade proxy:%s, count:%s" % (proxy.host, fail_counter)

        print "test proxy:%s finished" % proxy.host

    _push_proxys_to_redis(final_proxys)
    print "final proxys:", len(final_proxys)

    IOLoop.instance().stop()


@coroutine
def _test_and_put(proxys):
    print "start testing"
    yield _test_validation(proxys, max_process=10, interval=100)
    print "testing end"
