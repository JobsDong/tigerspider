#!/usr/bin/python
#-*- coding=utf-8 -*-

__author__ = ['"wuyadong" <wuyadong@tigerknows.com>']

from tornado.httpclient import HTTPRequest

LVYOU_HOST = u"http://www.daodao.com"


def build_next_page_request(next_page_relate_path):
    """构造下一页的request
        Args:
            current_page_url: unicode, current page url
            next_page_relate_path: unicode, relate path
        Returns:
            http_request: HttpRequest, http请求
    """
    url = "%s%s" % (LVYOU_HOST, next_page_relate_path)
    headers = {
        "Accept-Language": "en-US,en;q=0.5",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }
    http_request = HTTPRequest(url, headers=headers, connect_timeout=10,
                               request_timeout=15)
    return http_request


def build_attraction_request(relate_path):
    """构造attraction request
        Args:
            relate_path: unicode, attractino relate path
        Returns:
            attraction_request: HttpRequest
    """
    url = u"%s%s" % (LVYOU_HOST, relate_path)
    headers = {
        "Accept-Language": "en-US,en;q=0.5",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }
    http_request = HTTPRequest(url, headers=headers, connect_timeout=10,
                               request_timeout=15)
    return http_request


def build_description_request(attraction_url, relate_path):
    """构造介绍详情页的request
        Args:
            attraction_url: unicode, 景点详情页url
            relate_path: unicode, 相对路径
        Returns:
            description_request: HttpRequest, http请求
    """
    url = u"%s%s" % (LVYOU_HOST, relate_path)
    headers = {
        "Accept-Language": "en-US,en;q=0.5",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Referer": attraction_url,
    }
    return HTTPRequest(url, headers=headers, connect_timeout=10, request_timeout=15)