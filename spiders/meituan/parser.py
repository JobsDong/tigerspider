#!/usr/bin/python2.7
#-*- coding=utf-8 -*-

# Copy Rights (c) Beijing TigerKnows Technology Co., Ltd.

"""定義了meituan中的所有解析的類
    CityParser: 解析城市列表的類
    DealParser: 解析xml文件的列表
    WebParser: 解析網頁的類
    PictureParser: 圖片下載的類
"""

__authors__ = ['"wuyadong" <wuyadong@tigerknows.com>']

import os

from lxml import etree, html
from tornado.httpclient import HTTPRequest

from core.spider.parser import BaseParser
from core.datastruct import HttpTask
from core.util import remove_white

from spiders.meituan.items import DealItem, WebItem, CityItem, PictureItem
from spiders.meituan.util import (build_url_by_city_name, get_subcate_by_category,
                                  get_city_code,extract_deal_menu_summary,
                                  extract_list, extract_room_status_w,
                                    extract_table, )


DEFAULT_PICTURE_DIR = u"/home/wuyadong/swift_crawler/"
DEFAULT_PICTURE_HOST = u"fruit-pictures/"

class CityParser(BaseParser):
    """用於解析城市列表的類
    """

    def __init__(self, namespace):
        BaseParser.__init__(self, namespace)
        self.logger.debug("init meituan.CityParser")

    def parse(self, task, input_file):
        """用於解析城市的xml
            Args:
                task: Task, 任務描述
                response: HttpResponse, 網頁結果
        """
        self.logger.debug("CityParser start")
        try:
            tree = etree.parse(input_file)
            elements = tree.xpath("//division")

            for city_element in elements:
                english_name = city_element[0].text
                city_item = CityItem(city_element[1].text,
                                get_city_code(city_element[1].text))
                if city_item.chinese_name and city_item.city_code and english_name:
                    yield city_item
                    http_request = HTTPRequest(url=build_url_by_city_name(english_name)
                        , connect_timeout=20, request_timeout=240)
                    new_task = HttpTask(http_request, callback='DealParser', max_fail_count=5,
                                        kwargs={'citycode':city_item.city_code})
                    yield new_task
                else:
                    self.logger.warn("this item's property is none(chinese:%s, "
                                     "english:%s, citycode:%s)" %
                                     (city_item.chinese_name, english_name,
                                      city_item.city_code))

        except Exception, e:
            self.logger.error("city parse extract error:%s " % e)
        finally:
            self.logger.debug("city parse end to parse")


class DealParser(BaseParser):
    """用於解析xml文件的parser
    """

    def __init__(self, namespace, picture_dir=DEFAULT_PICTURE_DIR,
                 picture_host=DEFAULT_PICTURE_HOST):
        self._picture_dir = picture_dir
        self._picture_host = picture_host
        self._category_set = set()
        BaseParser.__init__(self, namespace)
        self.logger.debug("init meituan.DealParser")

    def parse(self, task, input_file):
        """解析文件的parser
            Args:
                task:Task, 任務的描述
                input_file:File, 文件对象
        """
        self.logger.debug("deal parse start to parse")
        try:
            tree = etree.parse(input_file)
            for date_element in tree.xpath("//data"):
                item_price = date_element.findtext("deal/price").strip()
                item_city_code = task.kwargs.get("citycode")
                item_dealid = date_element.findtext("deal/deal_id").strip()
                item_url = date_element.findtext("deal/deal_url").strip()
                item_name = remove_white(date_element.findtext("deal/deal_seller"))
                deal_category = date_element.findtext("deal/deal_subcate").strip()
                item_discount_type = get_subcate_by_category(deal_category)
                if deal_category not in self._category_set:
                    self._category_set.add(deal_category)

                if not item_discount_type:
                    continue
                item_start_time = date_element.findtext("deal/start_time").strip()
                item_end_time = date_element.findtext("deal/end_time").strip()
                item_discount = date_element.findtext("deal/rebate").strip()
                item_original_price = date_element.findtext("deal/value").strip()
                item_noticed = remove_white(date_element.findtext("deal/deal_tips"))
                picture_url = date_element.findtext("deal/deal_img").\
                    replace("275.168", "440.267")
                item_description = remove_white(date_element.findtext("deal/deal_desc"))
                item_deadline = date_element.findtext("deal/coupon_end_time").strip()
                item_short_desc = remove_white(date_element.findtext("deal/deal_name"))
                item_content_pic = u""
                item_purchased_number = date_element.findtext("deal/sales_num").strip()
                item_m_url = date_element.findtext("deal/deal_wap_url").strip()
                item_appointment = date_element.findtext("deal/reservation").strip()
                item_place = [{'place_name': remove_white(shop_element.findtext("shop_name")),
                          'address': remove_white(shop_element.findtext("shop_addr")),
                          'longitude': shop_element.findtext("shop_long").strip(),
                          'latitude': shop_element.findtext("shop_lat").strip(),
                          'place_phone': shop_element.findtext("shop_tel").strip(),
                          'open_time': u""}
                         for shop_element in date_element.xpath("shops//shop")]
                item_refund = u""
                item_save = u""
                item_remaining = u""
                item_limit = u""
                item_contact = u""

                item_pictures, picture_task = self._check_and_execute_picture(picture_url)

                deal_item = DealItem(item_price, item_city_code, item_dealid, item_url,
                                     item_name, item_discount_type, item_start_time,
                                     item_end_time, item_discount, item_original_price,
                                     item_noticed, item_pictures, item_description, item_deadline,
                                     item_short_desc, item_content_pic, item_purchased_number,item_m_url,
                                     item_appointment, item_place, item_save, item_remaining, item_limit,
                                     item_refund, item_contact)
                yield deal_item

                http_request = HTTPRequest(url=deal_item.url, connect_timeout=5, request_timeout=10)
                web_task = HttpTask(http_request, callback='WebParser', cookie_host='http://www.meituan.com',
                                cookie_count=20, max_fail_count=2, kwargs={'url': deal_item.url})
                yield web_task

                if picture_task:
                    yield picture_task

        except Exception, e:
            self.logger.error("deal parse extract error:%s, city_code:%s" %
                              (e, task.kwargs))
        finally:
            self.logger.debug("deal parse end")

    def _check_and_execute_picture(self, picture_url):
        """檢查圖片是否存在，並且生成task和改造path
            Args:
                picture_url, str, 圖片的url
            Returns: 二元組, (picture_path, task)
        """
        pictures = []
        if picture_url:
            picture_path = picture_url.replace(u"http://", self._picture_host)\
                .replace(u"\\s+|", "")\
                .replace(u"\\.jpg\\\\.*$",u".jpg")\
                .lower()
            pictures.append(picture_path)

        if len(pictures) >= 1 and not os.path.exists(self._picture_dir + pictures[0]):
            picture_request = HTTPRequest(url=str(picture_url), connect_timeout=10,
                                          request_timeout=60)
            picture_task = HttpTask(picture_request, callback='PictureParser', dns_need=False,
                                cookie_host='http://www.meituan.com', cookie_count=20,
                                max_fail_count=2,
                                kwargs={'picturepath':self._picture_dir + pictures[0]})
            return (pictures, picture_task)
        else:
            return (pictures, None)

    def clear_all(self):
        with open("/home/wuyadong/Documents/meituan/all_category.dat", "wb") as out_file:
            for category in self._category_set:
                out_file.write(category + "\n")


class WebParser(BaseParser):
    """用於解析網頁的parser
    """

    def __init__(self, namespace):
        BaseParser.__init__(self, namespace)
        self.logger.debug("init meituan.WebParser")

    def parse(self, task, input_file):
        """解析網頁
            Args:
                task:Task 任務的描述
                input_file: File, 文件对象
        """
        self.logger.debug("web parse start to parse")
        try:
            tree = html.parse(input_file)
            item_refund = self._extract_refund(tree)
            item_content_text = self._extract_content_text(tree)
            web_item = WebItem(item_refund, item_content_text)
        except Exception, e:
            self.logger.error("web parse extract error:%s, url:%s" % (e, task.kwargs))
        else:
            yield web_item
        finally:
            self.logger.debug("WebSpider end to parse")

    def _extract_refund(self, tree):
        elements = tree.xpath("//ul[@class='consumer-protection']//li")
        anytime = u"支持随时退款" if \
            elements[0].attrib["class"] == "protect-item protect-item--anytime" \
            else None
        expire = u"支持过期退款" if \
            elements[1].attrib["class"] == "protect-item protect-item--expire" \
            else None

        if anytime and expire:
            return anytime + u"，" + expire
        elif anytime:
            return anytime
        elif expire:
            return expire
        else:
            return u"不支持退款"

    def _extract_content_text(self, tree):
        text_splits = []
        blk_details = tree.xpath("//div[@class='blk detail']")
        for blk_detail in blk_details:
            for child_elem in blk_detail:
                if child_elem.tag == "table" and child_elem.attrib.has_key('class') \
                    and child_elem.attrib['class'] == "deal-menu":
                    extract_table(child_elem, text_splits)
                if child_elem.tag == "table" and child_elem.attrib.has_key('class') \
                    and child_elem.attrib['class'] == "ktv-table":
                    extract_table(child_elem, text_splits)
                if child_elem.tag == "p" and child_elem.attrib.has_key('class') \
                    and child_elem.attrib['class'] == "deal-menu-summary":
                    extract_deal_menu_summary(child_elem, text_splits)
                if child_elem.tag == "ul" and child_elem.attrib.has_key('class') \
                    and child_elem.attrib['class'] == "list" and \
                    child_elem.getprevious().attrib.has_key('class') \
                    and child_elem.getprevious().attrib['class'] == 'deal-menu-summary':
                    extract_list(child_elem, text_splits)
                if child_elem.tag == "div" and child_elem.attrib.has_key('class') \
                    and child_elem.attrib['class'] == "room-status-w":
                    extract_room_status_w(child_elem, text_splits)

        # 去除最后一个N_line
        if len(text_splits) >= 1:
            text_splits.pop()
        content_text = u"".join(text_splits)
        return content_text


class PictureParser(BaseParser):
    """用於處理下載picture的請求
    """
    def __init__(self, namespace):
        BaseParser.__init__(self, namespace)
        self.logger.debug("init PictureParser")

    def parse(self, task, input_file):
        if task.kwargs.has_key('picturepath'):
            picture_item = PictureItem(input_file.read(), task.kwargs.get('picturepath'))
            yield picture_item