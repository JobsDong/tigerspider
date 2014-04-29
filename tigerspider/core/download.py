#!/usr/bin/python2.7
#-*- coding=utf-8 -*-


"""
    此处处理包括cookie刷新，dnscache, 下载等问题
"""

__authors__ = ['"wuyadong" <wuyadong@tigerknows.com>']

import socket
import logging

from tornado import gen, httpclient
from tornado.httpclient import HTTPRequest

from tigerspider.core.datastruct import HttpTask
from tigerspider.core.resolver import DNSResolver, ResolveError
from tigerspider.core.proxy import get_proxy

httpclient.AsyncHTTPClient.configure(
    "tornado.curl_httpclient.CurlAsyncHTTPClient", max_clients=50)

_host_cookies = {}
_cookie_used_counts = {}
_cookie_is_buildings = set()
_host_ip_cache = {}

logger = logging.getLogger(__name__)

DEFAULT_USER_AGENT = r"Mozilla/5.0 (Windows NT 5.1)"
DEFAULT_ACCEPT_ENCODING = r"gzip,deflate,sdch"
DEFAULT_ACCEPT = r"text/html,application/xhtml+xml," \
                 r"application/xml;q=0.9,*/*;q=0.8"


class GetPageError(Exception):
    """get page exception
    """


@gen.coroutine
def fetch(http_task):
    """根据任务要求进行下载
        注意这个操作时异步的
        Args:
            http_task:http_task , 任务描述
        Returns:
            resp:Response, 下载的HTTP结果
    """
    try:
        http_request = http_task.request

        # get cookie if needed
        if http_task.cookie_host:
            add_cookie_for_request(http_request, http_task.cookie_host,
                                   http_task.cookie_count)

        # client
        add_universal_headers_for_request(http_request)

        # 使用dns resolver
        if http_task.dns_need:
            resovle_dns_for_request(http_request)

        # 使用proxy
        if http_task.proxy_need:
            add_proxy_for_request(http_request)

    except Exception, e:
        resp = e
        logger.error("fetch method error:%s" % e)
    else:
        client = httpclient.AsyncHTTPClient()
        resp = yield gen.Task(client.fetch, http_request)

    raise gen.Return(resp)


def add_cookie_for_request(http_request, cookie_host, cookie_count):
    """add cookie for request
        Args:
            http_request:HttpRequest, request
            cookie_host: str, cookie_host
    """
    cookie = get_cookie_sy(cookie_host, cookie_count)
    if cookie:
        http_request.headers = {"Cookie": cookie} if not http_request.headers \
            else http_request.headers.update({"Cookie": cookie})


def add_universal_headers_for_request(http_request):
    """add universal headers for request
        Args:
            http_reques:HttpRequest, request
    """
    if http_request.headers is None:
        http_request.headers = {}
    if not http_request.headers.has_key('User-Agent'):
        http_request.headers['User-Agent'] = DEFAULT_USER_AGENT
    if not http_request.headers.has_key('Accept-Encoding'):
        http_request.headers['Accept-Encoding'] = DEFAULT_ACCEPT_ENCODING
    if not http_request.headers.has_key('Accept'):
        http_request.headers['Accept'] = DEFAULT_ACCEPT


def resovle_dns_for_request(http_request):
    """resolve dns for request
        Args:
            http_request:HttpRequest, request
    """
    try:
        ip_addr = DNSResolver.instance().resolve(http_request.url)
    except ResolveError, e:
        logger.warn("dns error:%s, error:%s" % (http_request.host, e))
    else:
        http_request.url = ip_addr


def add_proxy_for_request(http_request):
    """add proxy for request
        Args:
            http_request:HttpRequest, request
    """
    # 获取一个proxy
    proxy_host, proxy_port = get_proxy()

    if proxy_host is not None:
        http_request.proxy_host = proxy_host
        http_request.proxy_port = proxy_port


def _get_page_sy(http_task, cookie):
    """以同步方式获取网页内容
        Args:
            task:HttpTask, 任务描述
            cookie: str, cookie
        Returns:
            resp: HTTPResponse, 结果
        Raises:
            error:GetPageError 错误
    """
    headers = {"User-Agent": DEFAULT_USER_AGENT,
               "Accept-Encoding": DEFAULT_ACCEPT_ENCODING,
               "Accept": DEFAULT_ACCEPT}
    if cookie:
        headers.update({"Cookie": cookie})
    if http_task.request.headers:
        http_task.request.headers.update(headers)
    else:
        http_task.request.headers = headers

    # dns resovler
    if http_task.dns_need:
        try:
            addr = DNSResolver.instance().resolve(http_task.request.url)
        except ResolveError, e:
            logger.warn("dns %s error:%s" % (http_task.request.url, e))
        else:
            http_task.request.url = addr

    try:
        client = httpclient.HTTPClient()
        resp = client.fetch(http_task.request)
    except Exception, e:
        logger.warn("get page failed error: %s" % e)
        resp = GetPageError(e)
    return resp


def get_ip_by_host(host):
    """获取ip，根据host
        Args:
            host: str, 域名
        Returns:
            ip: str, ip地址
    """
    global _host_ip_cache
    if not _host_ip_cache.has_key(host):
        # get ip
        addrinfo = socket.getaddrinfo(host, 80, 0, 0, socket.SOL_TCP)
        _, _, _, _, sockaddr = addrinfo[0]
        _host_ip_cache[host] = sockaddr[0]
    else:
        return _host_ip_cache[host]


def _build_cookie_sy(host):
    """访问主页，获取cookie
        Args:
            host: str, 主页地址
    """
    global _host_cookies
    global _cookie_used_counts

    cookie_http_task = HttpTask(HTTPRequest(host), callback="None")
    cookie = None if not _host_cookies.has_key(host) else _host_cookies[host]

    resp = _get_page_sy(cookie_http_task, cookie)
    if not resp or isinstance(resp, Exception):
        logger.warn("get cookie failed, error:%s" % resp)
        new_cookie = None
    else:
        headers = resp.headers
        if headers and headers.has_key("Set-Cookie"):
            new_cookie = headers["Set-Cookie"]
            logger.debug("cookie flushed for host:%s" % host)
        else:
            new_cookie = None
            logger.warn("cookie flushed failed for host:%s" % host)

    _host_cookies[host] = new_cookie
    _cookie_used_counts[host] = 0


def get_cookie_sy(host, flushcount=20):
    """获得可用的cookie，采用的事同步方式
        每隔flushcount次，cookie会自动刷新

        Args:
            host: str, 域名
            flushcount:int, 刷新间隔
        Returns:
            cookie: str, cookie字符串 （如果失败返回None）
    """
    global _host_cookies
    global _cookie_used_counts

    if not _host_cookies.has_key(host):
        _build_cookie_sy(host)
    else:
        if _cookie_used_counts.get(host) > flushcount:
            _build_cookie_sy(host)

    if _host_cookies.has_key(host):
        _cookie_used_counts[host] += 1
        return _host_cookies.get(host)
    else:
        return None
