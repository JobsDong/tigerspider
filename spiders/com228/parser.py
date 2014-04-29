#!/usr/bin/python
#-*- coding=utf-8 -*-

__author__ = ['"wuyadong" <wuyadong@tigerknows.com>']

import os.path
import datetime
import json
from lxml import html
from tornado.httpclient import HTTPRequest
from core.util import flist
from core.datastruct import HttpTask
from core.spider.parser import BaseParser
from spiders.com228.items import ActivityItem, WebItem, PictureItem
from spiders.com228.util import (create_product_url,
                                 create_city_type_task)


DEFAULT_PICTURE_DIR = u"/opt/swift_crawler/"
DEFAULT_PICTURE_HOST = u"fruit-pictures/"
COM228_HOST = u"http://www.228.com.cn"


class DealParser(BaseParser):
    """用于解析活动列表页面的parser
    """

    def __init__(self, namespace):
        BaseParser.__init__(self, namespace)
        self.logger.info("init Deal Parser finished")

    def parse(self, task, input_file):
        """用于解析列表页面(json数据)，
            Args:
                task: HttpTask, 任务对象
                input_file: File, 文件对象
            Yields:
                item: Item, 提取的对象
                task: 新的Task
        """
        # 获取json数据
        self.logger.info("deal parser start to handle")
        json_data = json.load(input_file)
        elems = json_data.get('products')
        page_size = json_data.get('pageSize', 1)
        # 获取传递的参数
        city_name = task.kwargs.get('city_name')
        tag = task.kwargs.get('tag')
        current_page = task.kwargs.get('current_page')
        city_code = task.kwargs.get('city_code')
        _type = task.kwargs.get('type')
        abbreviation = task.kwargs.get('abbreviation')
        cookie_host = task.kwargs.get('cookie_host')
        cookie_count = task.kwargs.get('cookie_count')
        if elems is not None:
            for elem in elems:
                try:
                    url, name, start_time, end_time, place_name = \
                        _extract_elem(elem)

                    # 存储Activity Item
                    yield ActivityItem(name, url, start_time,
                                       end_time, place_name,
                                       tag, city_code)
                    # 发起item请求
                    request = HTTPRequest(url, connect_timeout=10,
                                          request_timeout=15)
                    task = HttpTask(request, callback="ActivityParser",
                                    cookie_host=cookie_host,
                                    cookie_count=cookie_count,
                                    max_fail_count=3,
                                    kwargs={"url": url,
                                            "cookie_host": cookie_host,
                                            "cookie_count": cookie_count})
                    yield task
                except Exception, e:
                    self.logger.warn("extract one element failed error:%s" % e)

            # 发起下一页请求
            if current_page < int(page_size):
                next_page_task = create_city_type_task(city_name, city_code,
                                                       abbreviation, _type,
                                                       tag,
                                                       page=current_page + 1)
                yield next_page_task
        else:
            self.logger.warn("products is None, request url:%s" %
                             task.request.url)


def _extract_elem(json_elem):
    """解析json element的函数
        Args:
            json_elem: json, 节点元数
        Returns:
            url, name, start_time, end_time, place_name : tuple
    """
    product_id = json_elem.get('productid', '')
    name = json_elem.get('name', '')
    start_time = json_elem.get('begindate', '')
    end_time = json_elem.get('enddate', '')
    place_name = json_elem.get('vname', '')
    url = create_product_url(product_id) if len(product_id.strip()) != 0 else ''

    return url, name, start_time, end_time, place_name


def _extract_time(start_end_time):
    """用于解析出时间
        Args:
            start_end_time: str, 开始结束时间的字符串
        Returns:
            start_time, end_time: tuple, 开始和结束日期(datetime, datetime)
    """
    s_e = start_end_time.split(u"~")
    if len(s_e) >= 2:
        start_time_unicode, end_time_unicode = s_e[0].strip(), s_e[1].strip()
    else:
        start_time_unicode, end_time_unicode = s_e[0].strip(), s_e[0].strip()

    try:
        start_time = datetime.datetime.strptime(start_time_unicode, "%Y-%m-%d")
    except ValueError:
        start_time = None
    try:
        end_time = datetime.datetime.strptime(end_time_unicode, "%Y-%m-%d")
    except ValueError:
        end_time = None

    return start_time, end_time


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
        pic_url = unicode(flist(tree.xpath("//div[@class='product-price-left']"
                                           "/p/img/@src"),
                                default=u""))
        desc_elems = tree.xpath("//div[@class='product-detail-alla-cont']")
        description = _extract_desc_elems(desc_elems)
        date_elems = tree.xpath("//ul[@class='productnew-header-pricea2-ul"
                                " clearfloat']/li/@d")
        telephone = flist(tree.xpath("//div[@class='top-w']//li[@class='tel']"
                                     "/span/text()"), default=u"")
        telephone = telephone.replace(u"-", u"")
        if len(telephone) == 0:
            telephone = u"4006228228"
        price_elems = tree.xpath("//ul[@class='productnew-header-pricec2-ul "
                                 "productnew-"
                                 "header-pricec3-ul productnew-header-"
                                 "pricec2-cq']/li/@title")
        price_infos = list()
        for price_elem in price_elems:
            if unicode(price_elem) not in price_infos:
                price_infos.append(unicode(price_elem))
        price_info = u"/".join(price_infos)
        time_infos = []
        for date_elem in date_elems:
            time_infos.append(date_elem)
        time_info = u";".join(time_infos)
        url = task.kwargs.get('url')
        cookie_host = task.kwargs.get('cookie_host')
        cookie_count = task.kwargs.get('cookie_count')
        pictures, pic_task = self._check_and_execute_picture(pic_url,
                                                             cookie_host,
                                                             cookie_count)
        # 保存详情信息
        yield WebItem(url, telephone, description, pictures, time_info,
                      price_info, u"")
        # 抛出picTask
        if pic_task is not None:
            yield pic_task

    def _check_and_execute_picture(self, picture_url, cookie_host,
                                   cookie_count):
        """檢查圖片是否存在，並且生成task和改造path
            Args:
                picture_url, str, 圖片的url
            Returns: 二元組, (picture_path, task)
        """
        picture_path = u""
        if picture_url:
            picture_path = picture_url.replace(u"http://", self._picture_host)\
                .replace(u"\\s+|", "")\
                .replace(u"\\.jpg\\\\.*$", u".jpg")\
                .lower()

        if len(picture_path) > 0 and not os.path.exists(
                        self._picture_dir + picture_path):
            picture_request = HTTPRequest(url=str(picture_url),
                                          connect_timeout=10,
                                          request_timeout=60)
            picture_task = HttpTask(picture_request, callback='PictureParser',
                                    cookie_host=cookie_host,
                                    cookie_count=cookie_count,
                                    max_fail_count=2,
                                    kwargs={
                                        'picturepath':
                                         self._picture_dir + picture_path})
            return picture_path, picture_task
        else:
            return picture_path, None


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
            picture_item = PictureItem(input_file.read(),
                                       task.kwargs.get('picturepath'))
            yield picture_item