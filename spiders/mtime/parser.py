#!/usr/bin/python2.7
#-*- coding=utf-8 -*-

# Copy Rights (c) Beijing TigerKnows Technology Co., Ltd.

"""针对mtime的解析模块
    RealInfoParser: 用于解析影讯信息的类
"""

__authors__ = ['"wuyadong" <wuyadong@tigerknows.com>']

from lxml import etree
from tornado.httpclient import HTTPRequest


from core.spider.parser import BaseParser
from core.util import remove_white
from core.datastruct import Task


from spiders.mtime.items import RealInfoItem

class RealInfoParser(BaseParser):
    """用于解析影片资讯信息的类
    """

    def parse(self, task, response):
        """解析函数，
            Args:
                task:Task, 任务描述
                response:HTTPResponse, http访问的结果
            Yields:
                ...
                ...
        """
        cinema_id = task.kwargs.get('cinemaid')

        tree = etree.HTML(response.body)

        day_elems = tree.xpath("//div[@id='fixel' and @class='clearfix']//ul//li")
        if len(day_elems) >= 2:
            new_url = day_elems[1].xpath("a/@href")
            new_url = new_url[0] if len(new_url) > 0 else new_url
            if new_url != task.request.url:
                http_request = HTTPRequest(str(new_url), connect_timeout=10, request_timeout=20)
                new_task = Task(http_request, callback='RealInfoParser',
                            kwargs={'citycode':task.kwargs.get('citycode'), 'cinemaid':cinema_id})
                yield new_task

        fruits = tree.xpath("//dl[@class='s_cinamelist']/node()")
        for fruit in fruits:
            if fruit.tag == "a":
                movie_id = fruit.attrib['name']
            if fruit.tag == "dd":
                movie_running_time = fruit.xpath("div//span[@class='fr mt6']/text()")
                movie_running_time = remove_white(movie_running_time[0])\
                    .replace(u"片长", "").replace(u"分钟", "") \
                    if len(movie_running_time) > 0 else ""
                movie_language = fruit.xpath("div//span[@language]/a/text()")
                movie_language = movie_language[0] if len(movie_language) > 0 else ""
                movie_version = fruit.xpath("div//span[@version and @method='versionfilter']/a/text()")
                movie_version = movie_version[0] if len(movie_version) > 0 else ""
                movie_tag = ""
                show_infos = fruit.xpath("div//li[@showtimeid]")

                for show_info in show_infos:
                    show_id = show_info.attrib['showtimeid']
                    show_price = show_info.xpath("a/em/text()")
                    show_price = show_price[0] if len(show_price) > 0 else ""
                    show_start_time = show_info.attrib['time'].replace("/", "-")
                    show_url = _build_url(task.request.url,movie_id, show_id)

                    real_info_item = RealInfoItem(
                        show_id, movie_id, cinema_id, movie_tag, show_price, movie_version,
                        movie_language, movie_running_time,
                        show_url, task.kwargs['citycode'], show_start_time)

                    yield real_info_item

def _build_url(task_url, movie_id, show_id):
    """构造movie对应的url
        Args:
            task_url: str, task中带的url
            movie_id: str, movie 的id号
            show_id: str, show的id号
        Returns:
            url: str, 构造出来的movie的url
    """
    return "%sshowtime.html?m=%s&s=%s" % (task_url, movie_id, show_id)

