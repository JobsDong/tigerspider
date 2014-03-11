#!/usr/bin/python2.7
#-*- coding=utf-8 -*-


"""本地dns解析模块
    ResovleError: 解析错误类
    LRUCache: 基于LRU算法的cache
    DNSResolver: dns解析类
"""

__authors__ = ['"wuyadong" <wuyadong@tigerknows.com>']

import threading
import socket
import urlparse
from collections import deque

class ResolveError(Exception):
    """
        域名解析错误
    """

class LRUCache(object):
    """一个基于LRU算法的cache
    """
    def __init__(self, limit=1000):
        """初始化cache
            Args:
                limit: int 最大长度
        """
        self._max_size = limit
        self._heap = deque()
        self._dict = dict()

    def __getitem__(self, item):
        if not self._dict.has_key(item):
            raise KeyError("not has this item:%s" % item)
        else:
            self._heap.remove(item)
            self._heap.appendleft(item)
            return self._dict.get(item)

    def __setitem__(self, key, value):
        if self._dict.has_key(key):
            self._dict[key] = value
            self._heap.remove(key)
        else:
            self._dict[key] = value
            if len(self._dict) > self._max_size:
                del self._dict[self._heap.pop()]

        self._heap.appendleft(key)

    def __len__(self):
        return len(self._dict)

    def __contains__(self, item):
        return self._dict.has_key(item)

    def __delitem__(self, key):
        if not self._dict.has_key(key):
            raise KeyError("not contains this key:%s" % key)
        self._heap.remove(key)
        obj = self._dict.get(key)
        del self._dict[key]
        return obj

class DNSResolver(object):
    """DNSResolver是一个用于解析域名的类
    """
    _lock = threading.Lock()

    def __init__(self):
        self._cache = LRUCache(100)

    @staticmethod
    def instance():
        """获取一个dnsresolver实例
            单例模式
            Returns:
                resolver, DNSResolver 实例
        """
        if not hasattr(DNSResolver, '_instance'):
            with DNSResolver._lock:
                setattr(DNSResolver, '_instance', DNSResolver())
        return getattr(DNSResolver, "_instance")

    def resolve(self, host, port=80):
        """解析域名的函
            阻塞式的
            Args:
                host: str，域名
                port: int, 端口
            Returns:
                ip: str, ip地址
            Raises:
                ResolveError: 当解析失败的时候
        """
        schema, url, path, query, _ = urlparse.urlsplit(host)

        key = "%s:%s" % (url, port)
        if key not in self._cache:
            try:
                addr_info = socket.getaddrinfo(url, port, 0, 0, socket.SOL_TCP)
                _, _, _, _, sockaddr = addr_info[0]
                self._cache[key] = sockaddr[0]
            except Exception, e:
                raise ResolveError("dns resovel failed,host:%s, port:%s error:%s"
                                   % (host, port, e,))
        return urlparse.urlunsplit((schema, self._cache[key], path, query, ''))

    def close(self):
        """关闭操作，释放资源
        """
        del self._cache
