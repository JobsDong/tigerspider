#!/usr/bin/python
#-*- coding=utf-8 -*-

__author__ = ['"wuyadong" <wuyadong@tigerknows.com>']

import os.path
from lxml import html
from tornado.httpclient import HTTPRequest
from core.util import flist
from core.datastruct import HttpTask
from core.spider.parser import BaseParser
from spiders.com228.items import ActivityItem, WebItem, PictureItem


DEFAULT_PICTURE_DIR = u"/home/wuyadong/swift_crawler/"
DEFAULT_PICTURE_HOST = u"fruit-pictures/"


class DealParser(BaseParser):
    """用于解析活动列表页面的parser
    """

    def __init__(self, namespace):
        BaseParser.__init__(self, namespace)
        self.logger.info("init Deal Parser finished")

    def parse(self, task, input_file):
        """用于解析列表页面，
            Args:
                task: HttpTask, 任务对象
                input_file: File, 文件对象
            Yields:
                item: Item, 提取的对象
                task: 新的Task
        """
        tree = html.parse(input_file)
        elems = tree.xpath("//dl[@class='search-cont-listdl']")
        for elem in elems:
            info_elem = flist(elem.xpath("dd[@class='search-cont-listdd clearfloat']"))
            url, name, start_time, end_time, address, price, order = _extract_info_elem(info_elem)
            # 存储Activity Item
            tag = task.kwargs.get('tag')
            city_code = task.kwargs.get('city_code')
            yield ActivityItem(order, name, url, start_time, end_time, address,
                               price, "", "", tag, city_code)
            cookie_host = task.kwargs.get('cookie_host')
            cookie_count = task.kwargs.get('cookie_count')
            request = HTTPRequest(url, connect_timeout=2, request_timeout=5)
            task = HttpTask(request, callback="ActivityParser",
                            cookie_host=cookie_host, cookie_count=cookie_count, max_fail_count=3,)
            # 抛出新的Task
            yield task


def _extract_info_elem(info_elem):
    """
        Args:
            info_elem: Element, 节点元数
        Returns:
            url, name, start_time, end_time, address, price: tuple, url 和name
    """
    url = unicode(flist(info_elem.xpath("h2/a/@href"), default=u""))
    name = unicode(flist(info_elem.xpath("h2/a/text()"), default=u""))
    start_end_time = unicode(flist(info_elem.xpath(
        "ul[@class='search-cont-listdd-a']/li[1]/text()"), default=u""))
    s_e = start_end_time.replace(u"时间：", u"").split(u"~")
    if len(s_e) >= 2:
        start_time, end_time = s_e[0], s_e[1]
    else:
        start_time, end_time = s_e[0], None

    address = unicode(flist(info_elem.xpath("ul[@class='search-cont-listdd-a']/li[2]/text()"),
                            default=u"")).replace(u"场馆:", u"")
    price = unicode(flist(info_elem.xpath("ul[@class='search-cont-listdd-a']/li[3]/text()"), default=u""))
    start_index = url.index(u"ticket-")
    end_index = url.index(u".html")
    order = url[start_index + 7: end_index]
    return url, name, start_time, end_time, address, price, order


class ActivityParser(BaseParser):
    """用于解析活动详情页面的解析器
    """
    def __init__(self, namespace, picture_dir=DEFAULT_PICTURE_DIR,
                 picture_host=DEFAULT_PICTURE_HOST):
        BaseParser.__init__(self, namespace)
        self._picture_dir = picture_dir
        self._picture_host = picture_host
        self.logger.info("init Activity Parser finished")

    def parse(self, task, input_file):
        """详情解析器
            Args:
                task, HttpTask, 任务
                input_file: file, 网页文件
            Yields:
                item: WebItem, 数据
                task: HttpTask, 新任务
        """
        tree = html.parse(input_file)
        pic_url = unicode(flist(tree.xpath("//div[@class='product-price-left']/p/img/@src"),
                                default=u""))
        desc_elems = tree.xpath("//div[@class='product-detail-alla-cont']")
        description = _extract_desc_elems(desc_elems)
        date_elems = tree.xpath("//ul[@class='productnew-header-pricea2-ul clearfloat']/li/@d")
        time_infos = []
        for date_elem in date_elems:
            time_infos.append(date_elem)
        time_info = u";".join(time_infos)
        order = task.kwargs.get('order')
        cookie_host = task.kwargs.get('cookie_host')
        cookie_count = task.kwargs.get('cookie_count')
        pictures, pic_task = self._check_and_execute_picture(pic_url, cookie_host, cookie_count)
        # 保存详情信息
        yield WebItem(order, description, pictures, time_info)
        # 抛出picTask
        if pic_task is not None:
            yield pic_task

    def _check_and_execute_picture(self, picture_url, cookie_host, cookie_count):
        """檢查圖片是否存在，並且生成task和改造path
            Args:
                picture_url, str, 圖片的url
            Returns: 二元組, (picture_path, task)
        """
        pictures = []
        if picture_url:
            picture_path = picture_url.replace(u"http://", self._picture_host)\
                .replace(u"\\s+|", "")\
                .replace(u"\\.jpg\\\\.*$", u".jpg")\
                .lower()
            pictures.append(picture_path)

        if len(pictures) >= 1 and not os.path.exists(self._picture_dir + pictures[0]):
            picture_request = HTTPRequest(url=str(picture_url), connect_timeout=10,
                                          request_timeout=60)
            picture_task = HttpTask(picture_request, callback='PictureParser',
                                    cookie_host=cookie_host, cookie_count=cookie_count,
                                    kwargs={'picturepath': self._picture_dir + pictures[0]})
            return pictures, picture_task
        else:
            return pictures, None


def _extract_desc_elems(desc_elems):
    """extract description
        Args:
            desc_elems: list, [Elment]
        Returns:
            description: unicode, description
    """
    texts = []
    for desc_elem in desc_elems:
        for text in desc_elem.itertext():
            texts.append(text.strip())
    return u"".join(texts)


class PictureParser(BaseParser):
    """用于下载图片的Parser
    """
    def __init__(self, namespace):
        BaseParser.__init__(self, namespace)
        self.logger.info("init PictureParser finished")

    def parse(self, task, input_file):
        """解析函数
            Args:
                task: HttpTask, 任务
                input_file: StringIO, 网页文件
        """
        if 'picturepath' in task.kwargs:
            picture_item = PictureItem(input_file.read(), task.kwargs.get('picturepath'))
            yield picture_item