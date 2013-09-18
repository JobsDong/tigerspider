#!/usr/bin/python2.7
#-*- coding=utf-8 -*-

# Copy Rights (c) Beijing TigerKnows Technology Co., Ltd.

"""此处定义糯米网解析所需要的解析类
    CityParser: 主要负责解析出city的类
    DealParser: 主要负责解析api文档的类
    PictureParser: 主要负责处理图片的类
"""

__authors__ = ['"wuyadong" <wuyadong@tigerknows.com>']

import os
from tornado.httpclient import HTTPRequest
from lxml import etree

from core.spider.parser import BaseParser
from core.datastruct import Task
from core.util import remove_white

from spiders.nuomi.items import CityItem, DealItem, PictureItem
from spiders.nuomi.util import (get_city_code, build_url_by_city_name,
                                get_subcate_by_category)

DEFAULT_PICTURE_DIR = u"/opt/swift_crawler/"
DEFAULT_PICTURE_HOST = u"fruit-pictures/"

class CityParser(BaseParser):
    """负责从网页中解析出城市列表的类
    """
    def __init__(self, namespace):
        """初始化函数
            Args:
                namespace: str, 这个是spider传下来的名字空间，可以用，也可以不用
        """
        BaseParser.__init__(self, namespace)
        self.logger.debug("init nuomi city parser")

    def parse(self, task, response):
        """解析函数
            Args:
                task:Task, 任务描述
                response:HTTPResponse, http结果
            Yields:
                Item
                Task
        """
        tree = etree.HTML(response.body)
        citys = tree.xpath("//p[@id='citypid']/text()")
        citys = citys[0] if citys is not None and len(citys) > 0 else ""
        for city in citys.split(u","):
            city_english_name = remove_white(city)
            if len(city_english_name) > 0:
                city_item = CityItem("", city_english_name,get_city_code(city_english_name))
                if city_item.english_name and city_item.city_code:
                    yield city_item
                    http_request = HTTPRequest(url=build_url_by_city_name(city_item.english_name),
                                               connect_timeout=20, request_timeout=240)
                    new_task = Task(http_request, callback='DealParser',
                                    kwargs={'citycode':city_item.city_code})
                    yield new_task


class DealParser(BaseParser):
    """负责解析api文档的类
    """
    def __init__(self, namespace, picture_dir=DEFAULT_PICTURE_DIR,
                 picture_host=DEFAULT_PICTURE_HOST):
        """初始化函数
            Args:
                namespace: str， 来自spider的名字空间
                picture_dir: str, 图片存放的绝对路径
                picture_host: str, 图片存放的相对路径
        """
        self._picture_dir = picture_dir
        self._picture_host = picture_host
        BaseParser.__init__(self, namespace)
        self.logger.debug("init nuomi deal parser")

    def parse(self, task, response):
        """解析函数
            Args:
                task:Task, 任务描述
                response:HTTPResponse, http请求结果
        """
        self.logger.debug("deal parse start to parse")
        tree = etree.XML(response.body)
        for data_element in tree.xpath("//data"):
            item_price = data_element.findtext("price").strip()
            item_city_code = task.kwargs.get('citycode')
            item_url = data_element.findtext("url").strip()
            item_dealid = data_element.findtext("dealid").strip()
            item_name = data_element.findtext("title").strip()
            item_discount_type = get_subcate_by_category(data_element.findtext("types/type").strip())
            if not item_discount_type:
                continue
            item_start_time = data_element.findtext("startTime").strip()
            item_end_time = data_element.findtext("endTime").strip()
            item_discount = data_element.findtext("discount").strip()
            item_original_price = data_element.findtext("original_price").strip()
            picture_url = data_element.findtext("pictures/picture").strip()
            item_description = data_element.findtext("description").strip()
            item_deadline = data_element.findtext("deadline").strip()
            item_short_desc = data_element.findtext("short_desc").strip()
            item_content_pic = u""
            item_content_text = self._extract_content_text(data_element)
            item_purchased_number = data_element.findtext("purchased_number").strip()
            item_m_url = data_element.findtext("m_url").strip()
            item_appointment = ""
            item_place = self._extract_place(data_element)
            item_refund = self._extract_refund(data_element)
            item_save = data_element.findtext("save").strip()
            item_remaining = data_element.findtext("remaining").strip()
            item_limit = data_element.findtext("limit").strip()
            item_noticed = data_element.findtext("noticed").replace("\n", "N_Line")
            item_pictures, picture_task = self._check_and_execute_picture(picture_url)
            if picture_task:
                yield picture_task
            deal_item = DealItem(item_price, item_city_code, item_dealid, item_url, item_name,
                                 item_discount, item_start_time, item_end_time, item_discount,
                                 item_original_price, item_noticed, item_pictures, item_description,
                                 item_deadline, item_short_desc, item_content_text, item_content_pic,
                                 item_purchased_number, item_m_url, item_appointment, item_place,
                                 item_save, item_remaining, item_limit, item_refund)
            yield deal_item

    def _check_and_execute_picture(self, picture_url):
        """检查图片信息，生成图片task
            Args:
                picture_url: str, 图片链接
            Returns:
                (picture_path, task): 二元组，（路径，任务）
        """
        pictures = []
        if picture_url:
            picture_path = picture_url.replace(u"http://", self._picture_host)\
                .replace(u"\\s+|", "")\
                .replace(u"\\.jpg\\\\.*$",u".jpg")\
                .lower()
            pictures.append(picture_path)

        if len(pictures) >= 1 and not os.path.exists(pictures[0]):
            picture_request = HTTPRequest(url=str(picture_url), connect_timeout=10,
                                          request_timeout=40)
            picture_task = Task(picture_request, callback='PictureParser',
                                cookie_host='http://www.nuomi.com', cookie_count=15,
                                kwargs={'picturepath':self._picture_dir + pictures[0]})
            return (pictures, picture_task)
        else:
            return (pictures, None)

    def _extract_content_text(self, data_element):
        """用于解析出content_text值
            Args:
                data_element: Element, 节点
            Returns:
                content_text: str, 已处理的str
        """
        content_text = data_element.findtext("content_text")
        content_text = content_text.replace("-", "")\
            .replace("<br />", "N_Line-")\
            .replace("<br/>", "N_Line-")

        tree = etree.HTML(content_text)
        temp_texts = []
        for text in tree.itertext():
            stripped_text = remove_white(text)
            if len(stripped_text) > 0:
                temp_texts.append(stripped_text)

        if len(temp_texts) > 0:
            last_text = temp_texts.pop()
            if last_text.endswith("N_Line-") and len(last_text) > 7:
                temp_texts.append(last_text[:-7])
            else:
                temp_texts.append(last_text)
        if len(temp_texts) > 0:
            temp_texts.append("-")

        return "".join(temp_texts)

    def _extract_place(self, data_element):
        """从api中解析出地址信息列表
            Args:
                tree:Etree, 树节点
            Returns:
                places:List, 地址列表
        """
        places = data_element.xpath("places//place")
        item_places = []
        for place in places:
            place_info = {}
            place_info['place_name'] = remove_white(place.findtext("place_name"))
            place_info['address'] = remove_white(place.findtext("address"))
            place_info['place_phone'] = remove_white(place.findtext("place_phone"))
            place_info['open_time'] = remove_white(place.findtext("open_time"))
            item_places.append(place_info)
        return item_places

    def _extract_refund(self, data_element):
        """提取退款信息
            Args:
                tree:Etree, 节点树
            Returns:
                refund_text: str, 退款信息
        """
        refund_texts = data_element.xpath("refunds//refund/text()")
        is_support_overdue = False
        is_support_seven = False
        for refund_text in refund_texts:
            if refund_text.rfind(u"不支持") != -1 and refund_text.rfind(u"过期退款") != -1:
                is_support_overdue = False
            if refund_text.rfind(u"支持") != -1 and refund_text.rfind(u"过期退款") != -1:
                is_support_overdue = True
            if refund_text.rfind(u"不支持") != -1 and refund_text.rfind(u"7天退款") != -1:
                is_support_seven = False
            if refund_text.rfind(u"支持") != -1 and refund_text.rfind(u"七天退款") != -1:
                is_support_seven = True

        if is_support_overdue and is_support_seven:
            return "支持七天退款，支持过期退款"
        elif is_support_overdue and not is_support_seven:
            return "不支持七天退款，支持过期退款"
        elif not is_support_overdue and is_support_seven:
            return "支持七天退款，不支持过期退款"
        elif not is_support_overdue and not is_support_seven:
            return "不支持七天退款，不支持过期退款"

class PictureParser(BaseParser):
    """用于处理图片下载请求
    """
    def __init__(self, namespace):
        BaseParser.__init__(self, namespace)
        self.logger.debug("init nuomi PictureParser")

    def parse(self, task, response):
        if task.kwargs.has_key('picturepath'):
            picture_item = PictureItem(response.body, task.kwargs.get('picturepath'))
            yield picture_item
