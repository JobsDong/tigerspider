#!/usr/bin/python2.7
#-*- coding=utf-8 -*-

# Copy Rights (c) Beijing TigerKnows Technology Co., Ltd.

"""
    此处处理包括cookie刷新，dnscache, 下载等问题
"""

__authors__ = ['"wuyadong" <wuyadong@tigerknows.com>']

import socket
import logging

from tornado import gen, httpclient
from tornado.httpclient import HTTPRequest

from core.util import coroutine_wrap
from core.datastruct import HttpTask
from core.resolver import DNSResolver, ResolveError

httpclient.AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient")

client = httpclient.AsyncHTTPClient()

_host_cookies = {"http://www.meituan.com": r"SID=id05a52uecv601av123577nmr3; ci=1; "
                r"abt=1378729480.0%7CBDF; rvct=1; rvd=8190998;"
                r" rus=1; uuid=32d702eebe3d05dd1ae5.1378729480.0.0.0;"
                r" __utma=1.580685477.1378729555.1378729555.1378729555.1;"
                r" __utmb=1.5.9.1378729597349; __utmc=1;"
                r" __utmz=1.1378729555.1.1.utmcsr=(direct)|"
                r"utmccn=(direct)|utmcmd=(none);"
                r" __utmv=1.|1=city=beijing=1;"
                r" __t=1378729597368.0.1378729597368.Bsanlitun.Ashoppingmall"}
_cookie_used_counts = {"http://www.meituan.com": 0}
_cookie_is_buildings = set()

logger = logging.getLogger(__name__)


DEFAULT_USER_AGENT = r"Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.116 Safari/537.36"
DEFAULT_ACCEPT_ENCODING = r"gzip,deflate,sdch"
DEFAULT_ACCEPT = r"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"

class GetPageError(Exception):
    '''
    get page exeception
    '''

@gen.coroutine
def fetch(http_task):
    """根据任务要求进行下载
        注意这个操作时异步的
        Args:
            http_task:http_task , 任务描述
        Returns:
            resp:Response, 下载的HTTP结果
    """
    http_request = http_task.request
    # get cookie if needed
    if http_task.cookie_host:
        cookie = yield coroutine_wrap(get_cookie_sy,
                                      http_task.cookie_host,
                                      http_task.cookie_count)
        if cookie:
            http_request.headers = {"Cookie": cookie} if not http_request.headers \
                else http_request.update({"Cookie": cookie})

    # client
    if not http_task.request.headers.has_key('User-Agent'):
        http_task.request.headers['User-Agent'] = DEFAULT_USER_AGENT
    if not http_task.request.headers.has_key('Accept-Encoding'):
        http_task.request.headers['Accept-Encoding'] = DEFAULT_ACCEPT_ENCODING
    if not http_task.request.headers.has_key('Accept'):
        http_task.request.headers['Accept'] = DEFAULT_ACCEPT

    # 使用dns resolver
    if http_task.dns_need:
        try:
            ip_addr = DNSResolver.instance().resolve(http_request.url)
        except ResolveError, e:
            logger.warn("dns error:%s, error:%s" % (http_request.host, e))
        else:
            http_request.url = ip_addr

    resp = yield gen.Task(client.fetch, http_request)
    raise gen.Return(resp)

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

