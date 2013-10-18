#!/usr/bin/python2.7
#-*- coding=utf-8 -*-

# Copy Rights (c) Beijing TigerKnows Technology Co., Ltd.

"""Proxy resource manager
"""

__authors__ = ['"wuyadong" <wuyadong@tigerknows.com>']

import threading
import logging
from core.redistools import RedisQueue, RedisError

DEFAULT_PROXY_NAMESPACE = "system:proxys"

proxy_logger = logging.getLogger("proxy-logger")

class ProxyError(Exception):
    """error about proxy
    """

class Proxy(object):
    """proxy class
    """

    def __init__(self, host, port, username=None, passwd=None):
        """init proxy

            Args:
                host: str, proxy host
                port: int, proxy port
                username: str, proxy username
                passwd: str, proxy password
        """
        self.host = host
        self.port = port
        self.username = username
        self.passwd = passwd
        self._is_need_passwd = True if username is not None else False

    @property
    def is_need_passwd(self):
        return self._is_need_passwd

    def __eq__(self, other):
        if isinstance(other, Proxy):
            return other.host == self.host and \
                other.port == self.port and \
                other.username == self.username and \
                other.passwd == self.passwd
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
            self._proxy_queue = RedisQueue(
                DEFAULT_PROXY_NAMESPACE, host="localhost", port=6379, db=0)
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
            proxy = self._proxy_queue.pop()
        except RedisError, e:
            raise ProxyError(e)
        else:
            self._proxy_queue.push(proxy)
            return proxy

    def flag_proxy_not_avaliable(self, proxy, url):
        """flag proxy not avaliable
        """
        proxy_logger.info("fail-proxy, host:%s, port:%s, url:%s" %
                          (proxy.host, proxy.port, url))

    def flag_proxy_avaliable(self, proxy, url):
        proxy_logger.info("success-proxy, host:%s, port:%s, url:%s" %
                          (proxy.host, proxy.port, url))