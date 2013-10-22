#!/usr/bin/python2.7
#-*- coding=utf-8 -*-

# Copy Rights (c) Beijing TigerKnows Technology Co., Ltd.

"""Proxy resource manager
"""

__authors__ = ['"wuyadong" <wuyadong@tigerknows.com>']

import threading
import logging

from core.redistools import RedisPriorityQueue, RedisError
from core.util import lcm

DEFAULT_PROXY_NAMESPACE = "system:proxys"

proxy_logger = logging.getLogger("proxy-logger")

class ProxyError(Exception):
    """error about proxy
    """

class Proxy(object):
    """proxy class
    """

    def __init__(self, host, port, username=None, password=None, score=10):
        """init proxy

            Args:
                host: str, proxy host
                port: int, proxy port
                username: str, proxy username
                password: str, proxy password
                score: float, proxy score
        """
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.score = score
        self.is_need_passwd = True if username is not None else False

    def __eq__(self, other):
        if isinstance(other, Proxy):
            return other.host == self.host and \
                other.port == self.port and \
                other.username == self.username and \
                other.password == self.password and \
                other.is_need_passwd == self.is_need_passwd
        else:
            return False


class ProxyManager(object):
    """proxy manager class
    """

    _instance_lock = threading.Lock()

    @staticmethod
    def instance():
        if not hasattr(ProxyManager, '_instance'):
            with ProxyManager._instance_lock:
                setattr(ProxyManager, '_instance', ProxyManager())

        return getattr(ProxyManager, '_instance')

    def __init__(self):
        """init
            load proxy list from redis queue
        """
        try:
            self._proxy_queue = RedisPriorityQueue(
                DEFAULT_PROXY_NAMESPACE, host="localhost", port=6379, db=0)
            self._lcm = self._count_proxys_lcm()
        except RedisError, e:
            raise ProxyError("init proxy queue failed, error:%s" % e)

    def get_an_avaliable_proxy(self):
        """get an avaliable proxy

            Returns:
                proxy: Proxy, proxy instance if not has proxy return None
            Raises:
                error:ProxyError, proxy error
        """
        try:
            proxy, dynamic_score = self._proxy_queue.pop()
        except RedisError, e:
            raise ProxyError(e)
        else:
            if proxy is not None:
                self._proxy_queue.push(proxy,
                    self._score_dynamic_change(dynamic_score, proxy.score, self._lcm))
            return proxy

    def flag_proxy_not_avaliable(self, proxy, url):
        """flag proxy not avaliable
        """
        #proxy_logger.info("fail-proxy, host:%s, port:%s, url:%s" %
        #                  (proxy.host, proxy.port, url))

    def flag_proxy_avaliable(self, proxy, url):
        """flag proxy avaliable
        """
        #proxy_logger.info("success-proxy, host:%s, port:%s, url:%s" %
        #                  (proxy.host, proxy.port, url))

    def _score_dynamic_change(self, dynamic, score, gab):
        print dynamic, score, gab
        return dynamic - gab / score

    def _count_proxys_lcm(self):
        """count lcm of all proxys

            Returns:
                lcm of scores
        """
        temp_proxys = list()
        temp_scores = list()
        while self._proxy_queue.size() > 0:
            proxy, dynamic_score = self._proxy_queue.pop()
            temp_proxys.append((proxy, dynamic_score))
            temp_scores.append(proxy.score)

        for (proxy, dynamic_score) in temp_proxys:
            self._proxy_queue.push(proxy, dynamic_score)

        return lcm(*temp_scores)
