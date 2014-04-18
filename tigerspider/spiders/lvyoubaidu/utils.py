#!/usr/bin/python
#-*- coding=utf-8 -*-

__author__ = ['"wuyadong" <wuyadong@tigerknows.com>']

import time
from tornado.httpclient import HTTPRequest


LVYOU_HOST = u"http://lvyou.baidu.com"
EVERY_PAGE_SCENE_COUNT = 16


def build_scene_url(scene):
    """构造景点的url
        Args:
            lvyou_host: 百度旅游的主页
            city_name: 城市名
            scene: 景点名
        Returns:
            scene_url: unicode, 景点的url
    """
    return "%s/%s/" % (LVYOU_HOST, scene)


def build_attraction_list_ajax_url(city_name, page=1):
    """生成ajax_url
        Args:
            city_name: unicode, 城市名
            page: int, 页面index
    """
    timestamp = str(int(time.time())) + "000"
    return "%s/destination/ajax/allview?surl=%s&format=ajax&cid=0&pn=%d&t=%s" % \
           (LVYOU_HOST, city_name, page, timestamp)


def build_comment_list_ajax_url(sid, num=10):
    """生成comment list 的ajax_url
        Args:
            sid: unicode, attracition's sid
            num: int, comment number
        Return:
            ajax_url: unicode, ajax_url
    """
    timestamp = str(int(time.time())) + "000"
    return "%s/user/ajax/remark/getsceneremarklist?xid=%s&score=0&pn=0&rn=%s&format=ajax&t=%s&style=hot" % \
           (LVYOU_HOST, sid, num, timestamp)


def build_comment_list_header(scene_relate_path):
    """生成comment list 的http header
        Args:
            scene_relate_path: unicode, 景点的相对路径
        Returns:
            headers: dict, http header
    """
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Referer": "%s/%s" % (LVYOU_HOST, scene_relate_path),
        "X-Requested-With": "XMLHttpRequest",
    }
    return headers


def build_next_page_header(city_name):
    """生成ajax 的header
        Args:
            lvyou_host: unicode, 旅游主页
            city_name: unicode, 城市名
    """
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Referer": "%s/%s/jingdian/" % (LVYOU_HOST, city_name),
        "X-Requested-With": "XMLHttpRequest",
    }
    return headers


def build_next_page_request(city_name, page):
    """构造下一页的HTTPREQUEST
        Args:
            lvyou_host: unicode, 旅游主页
            city_name: unicode, 城市名
            page: int, current page index
        Returns:
            next_page_request: HTTPRequest, 下一页任务请求
    """
    next_page_request = HTTPRequest(build_attraction_list_ajax_url(city_name, page),
                                    connect_timeout=5, request_timeout=10,
                                    headers=build_next_page_header(city_name))
    return next_page_request


def build_comment_list_request(sid, scene_relate_path):
    """生成comment list的http request
        Args:
            sid: unicode, scene's sid
            scene_relate_path: unicode, scene's relate path
        Returns:
            http_request: HttpRequest,
    """
    comment_list_request = HTTPRequest(build_comment_list_ajax_url(sid, 10),
                                       connect_timeout=5, request_timeout=10,
                                       headers=build_comment_list_header(scene_relate_path))
    return comment_list_request