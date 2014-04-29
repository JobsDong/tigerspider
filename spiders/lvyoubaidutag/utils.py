#!/usr/bin/python
#-*- coding=utf-8 -*-

__author__ = ['"wuyadong" <wuyadong@tigerknows.com>']


import time
from tornado.httpclient import HTTPRequest
from core.datastruct import HttpTask


LVYOU_HOST = u"http://lvyou.baidu.com"
EVERY_PAGE_SCENE_COUNT = 16
TAGS = {
    u"500": u"城市",
    u"501": u"古镇乡村",
    u"502": u"海岛",
    u"503": u"自然景观",
    u"504": u"人文景观",
    u"505": u"展馆",
    # u"506": u"购物娱乐",
    u"507": u"休闲度假",
    u"508": u"其他",
}


def build_tag_tasks():
    """生成所有的tag任务
        Returns:
            tasks: list, [HttpTask]
    """
    tasks = []
    for key, value in TAGS.iteritems():
        task = HttpTask(build_next_tag_page_request(key, 1, "shanghai"),
                        callback="TagListParser", max_fail_count=5,
                        cookie_host=LVYOU_HOST, kwargs={"tag": value})
        tasks.append(task)
    return tasks


def build_next_tag_page_request(cid, page, city_name):
    """生成下一页的tag request
        Args:
            tag: str, 标签
            page: int, current page index
        Returns:
            next_tag_request: HTTPRequest, 下一页任务请求
    """
    next_tag_page_request = HTTPRequest(build_tag_list_ajax_url(cid, page, city_name),
                                        connect_timeout=5, request_timeout=10,
                                        headers=build_next_page_header(city_name))
    return next_tag_page_request


def build_tag_list_ajax_url(tag, page, city_name):
    """生成下一页的tag标签url
        Args:
            tag: str, 标签
            page: int, current page index
            city_name: str, 城市名
        Returns:
            url: str, 下一页的url
    """
    timestamp = str(int(time.time())) + "000"
    return "%s/destination/ajax/allview?surl=%s&format=ajax&cid=%s&pn=%s&t=%s" \
           % (LVYOU_HOST, city_name, tag, page, timestamp)


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
