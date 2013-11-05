#!/usr/bin/python2.7
#-*- coding=utf-8 -*-

# Copy Rights (c) Beijing TigerKnows Technology Co., Ltd.

"""用于窝窝团购中的解析器
    CityParser: 用于解析城市列表的parser
    DealParser: 用于解析api文档的parser
    WebParser: 用于解析网页数据的parser
    PictureParser: 用于解析图片的parser
"""

__author__ = ['"wuyadong" <wuyadong@tigerknows.com>']


import os
from lxml import etree, html
from tornado.httpclient import HTTPRequest

from core.spider.parser import BaseParser
from core.datastruct import HttpTask
from core.util import remove_white
from spiders.tuan55.items import DealItem, WebItem, PictureItem
from spiders.tuan55.util import (get_city_code_from_chinese,
                                 get_subcate_by_category,
                                  extract_dl, extract_table)

DEFAULT_PICTURE_DIR = u"/home/wuyadong/swift_crawler/"
DEFAULT_PICTURE_HOST = u"fruit-pictures/"

# class CityParser(BaseParser):
#     """用于解析城市api文档的parser
#     """
#     def __init__(self, namespace):
#         """初始化函数
#             Args:
#                 namespace: str, 这个是spider传下来的名字空间，可以用，也可以不用
#         """
#         BaseParser.__init__(self, namespace)
#         self.logger.debug("init tuan55 city parser")
#
#     def parse(self, task, response):
#         """解析函数
#             Args:
#                 task:Task, 任务描述
#                 response:HTTPResonse, 下载的结果
#             Yields:
#                 new_task:Task, 新任务描述
#                 item: Item, 提取出来的结果
#         """
#         self.logger.debug("start to city parse")
#
#         tree = etree.XML(response.body)
#         city_elems = tree.xpath("//division")
#         for city_elem in city_elems:
#             item = CityItem(city_elem[1].text, city_elem[0].text,
#                                 get_city_code(city_elem[0].text))
#             if item.chinese_name and item.english_name and item.city_code:
#                 yield item
#                 http_request = HTTPRequest(url=build_url_by_city_name(item.english_name),
#                                                connect_timeout=20, request_timeout=360)
#                 new_task = Task(http_request, callback='DealParser',
#                                 max_fail_count=5, kwargs={'citycode':item.city_code})
#                 yield new_task
#             else:
#                 self.logger.warn("city item's property is empty chinese:%s, english:%s,"
#                                      " city_code:%s" % (item.chinese_name, item.english_name,
#                                                         item.city_code))


# class DealParser(BaseParser):
#     """用于解析团购信息的parser
#     """
#     def __init__(self, namespace, picture_dir=DEFAULT_PICTURE_DIR,
#                  picture_host=DEFAULT_PICTURE_HOST):
#         """初始化函数
#             Args:
#                 namespace: str， 来自spider的名字空间
#                 picture_dir: str, 图片存放的绝对路径
#                 picture_host: str, 图片存放的相对路径
#         """
#         self._picture_dir = picture_dir
#         self._picture_host = picture_host
#         BaseParser.__init__(self, namespace)
#         self.logger.debug("init tuan55 deal parser")
#
#     def parse(self, task, response):
#         self.logger.debug("deal parse start to parse")
#
#         tree = etree.XML(response.body)
#         for date_element in tree.xpath("//url"):
#             item_price = date_element.findtext("data/display/price").strip()
#             item_city_code = task.kwargs.get('citycode')
#             item_url = date_element.findtext("loc").strip()
#             item_dealid = extract_id_from_url(item_url)
#             item_name = u""
#             item_discount_type = u""
#             item_start_time = date_element.findtext("data/display/startTime").strip()
#             item_end_time = date_element.findtext("data/display/endTime").strip()
#             item_discount = date_element.findtext("data/display/rebate").strip()
#             item_original_price = date_element.findtext("data/display/value").strip()
#             picture_url = date_element.findtext("data/display/image")
#             item_description = u""
#             item_deadline = ""
#             item_short_desc = u""
#             item_content_pic = u""
#             item_content_text = u""
#             item_purchased_number = date_element.findtext("data/display/bought").strip()
#             item_m_url = convert_to_m_url(item_url)
#             item_appointment = u""
#             item_place = u""
#             item_refund = u""
#             item_save = u""
#             item_remaining = u""
#             item_limit = u""
#             item_noticed = u""
#             item_contact = u""
#             item_pictures, picture_task = self._check_and_execute_picture(picture_url)
#
#             deal_item = DealItem(item_price, item_city_code, item_dealid,
#                                      item_url, item_name, item_discount_type,
#                                      item_start_time, item_end_time, item_discount,
#                                      item_original_price, item_noticed,
#                                      item_pictures, item_description, item_deadline,
#                                      item_short_desc, item_content_text,
#                                      item_content_pic, item_purchased_number, item_m_url,
#                                      item_appointment, item_place,
#                                      item_save, item_remaining, item_limit, item_refund,
#                                      item_contact)
#             yield deal_item
#             http_request = HTTPRequest(url=deal_item.url, connect_timeout=5,
#                                            request_timeout=10)
#             new_task = Task(http_request, callback='WebParser',
#                                 cookie_host='http://www.55tuan.com', cookie_count=10,
#                                 kwargs={'url': deal_item.url})
#             yield new_task
#             if picture_task:
#                 yield picture_task
#
#     def _check_and_execute_picture(self, picture_url):
#         """檢查圖片是否存在，並且生成task和改造path
#             Args:
#                 picture_url, str, 圖片的url
#             Returns: 二元組, (picture_path, task)
#         """
#         pictures = []
#         if picture_url:
#             picture_path = picture_url.replace(u"http://", self._picture_host)\
#                 .replace(u"\\s+|", "")\
#                 .replace(u"\\.jpg\\\\.*$",u".jpg")\
#                 .lower()
#             pictures.append(picture_path)
#
#         if len(pictures) >= 1 and not os.path.exists(self._picture_dir + pictures[0]):
#             picture_request = HTTPRequest(url=str(picture_url), connect_timeout=10,
#                                           request_timeout=60)
#             picture_task = Task(picture_request, callback='PictureParser',
#                                 cookie_host='http://www.55tuan.com', cookie_count=20,
#                                 kwargs={'picturepath':self._picture_dir + pictures[0]})
#             return (pictures, picture_task)
#         else:
#             return (pictures, None)


class DealParser(BaseParser):
    """用于解析api文档的parser

    """
    def __init__(self, namespace, picture_dir=DEFAULT_PICTURE_DIR,
                 picture_host=DEFAULT_PICTURE_HOST):
        """初始化
            Args:
                namespace: str, 来自spider的名字空间
        """
        self._picture_dir = picture_dir
        self._picture_host = picture_host
        BaseParser.__init__(self, namespace)
        self.logger.debug("init tuan55 deal parser")

    def parse(self, task, input_file):
        """解析api文档的函数
            Args:
                task: Task, 任务描述
                input_file: File, 文件对象
            Yields:
                task: Task, new_task
                item: Item, 结果
        """
        self.logger.debug("deal parse start to parse")
        context = etree.iterparse(input_file, events=('end',), tag='deal')

        for _, data_elem in context:
            item_price = data_elem.findtext("price").strip()
            item_city_code = get_city_code_from_chinese(
                data_elem.findtext("division_name").strip())
            if not item_city_code:
                continue
            item_url = data_elem.findtext("deal_web_url").strip()
            item_dealid = data_elem.findtext("id").strip()
            item_name = u""
            item_discount_type = u""
            item_start_time = data_elem.findtext("start_date").strip()
            item_end_time = data_elem.findtext("end_date").strip()
            item_discount = data_elem.findtext("discount_percent").strip()
            item_original_price = data_elem.findtext("value").strip()
            picture_url = data_elem.findtext("large_image_url")
            item_description = u""
            item_deadline = ""
            item_short_desc = u""
            item_content_pic = u""
            item_content_text = u""
            item_purchased_number = data_elem.findtext("quantity_sold").strip()
            item_m_url = data_elem.findtext("deal_url").strip()
            item_appointment = u""
            item_place = u""
            item_refund = u""
            item_save = u""
            item_remaining = u""
            item_limit = u""
            item_noticed = u""
            item_contact = u""
            item_pictures, picture_task = self._check_and_execute_picture(picture_url)

            deal_item = DealItem(item_price, item_city_code, item_dealid,
                                item_url, item_name, item_discount_type,
                                item_start_time, item_end_time, item_discount,
                                item_original_price, item_noticed,
                                item_pictures, item_description, item_deadline,
                                item_short_desc, item_content_text,
                                item_content_pic, item_purchased_number, item_m_url,
                                item_appointment, item_place,
                                item_save, item_remaining, item_limit, item_refund,
                                item_contact)
            yield deal_item
            http_request = HTTPRequest(url=deal_item.url, connect_timeout=5,
                                           request_timeout=10)
            new_task = HttpTask(http_request, callback='WebParser',
                                cookie_host='http://www.55tuan.com', cookie_count=10,
                                kwargs={'url': deal_item.url})
            yield new_task
            if picture_task:
                yield picture_task

            data_elem.clear()


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
            picture_task = HttpTask(picture_request, callback='PictureParser',
                                cookie_host='http://www.55tuan.com', cookie_count=20,
                                kwargs={'picturepath':self._picture_dir + pictures[0]})
            return (pictures, picture_task)
        else:
            return (pictures, None)



class WebParser(BaseParser):
    """用于解析网页的parser
    """
    def __init__(self, namespace):
        """初始化
            Args:
                namespace: str, 来自spider的名字空间
        """
        BaseParser.__init__(self, namespace)
        self.logger.debug("init tuan55 WebParser")

    def parse(self, task, input_file):
        """解析网页函数
            Args:
                "http://www.55tuan.com/goods-ada26875586dae46.html"
                task:Task, 任务描述
                input_file: File, 文件对象
            Yields:
                item: Item, 解析结果
        """
        print 'wori'
        self.logger.debug("web parse start to parse")
        tree = html.parse(input_file)
        names = tree.xpath("//*[@id='content']/div[4]/div[@class='con_left clearfix']/p/text()[last()]")
        item_name = remove_white(names[0].replace(">", "")) if names else ""
        saves = tree.xpath("//li[@class='shopprice']/span[6]/text()")
        item_save = remove_white(saves[0].replace(u"¥", "")) if saves else ""
        item_description = self._extract_description(tree)
        item_short_desc = item_description
        item_place = self._extract_place(tree)
        item_refund = self._extract_refund(tree)
        item_noticed = self._extract_noticed(tree)
        item_content_pic = u""
        item_deadline = self._extract_deadline(tree, item_noticed)
        item_content_text = self._extract_content_text(tree)
        category_texts = tree.xpath("//p[@class='Crumbs']/a/text()")
        item_discount_type = get_subcate_by_category(category_texts)
        web_item = WebItem(item_name, item_noticed, item_description, item_short_desc,
                               item_content_text, item_content_pic, item_refund, item_save,
                               item_place, item_deadline, item_discount_type)
        yield web_item

    def _extract_deadline(self, tree, notice):
        """解析出deadline信息
            Args:
                tree, Etree, 树节点
            Returns:
                deadline：str, 截止信息
        """
        if notice.rfind(u"有效期：") != -1 or notice.rfind(u"有效日期") != -1:
            return ""
        else:
            deadlines = tree.xpath(u"//*/text()[contains(., '窝窝券有效期')]")
            deadline = remove_white(deadlines[0]).replace(u"窝窝券有效期：", "")\
                if len(deadlines) > 0 else ""
            return deadline

    def _extract_description(self, tree):
        """解析description值
            Args:
                tree:Etree, 树节点
            Returns:
                description: str, 提取的内容

        """
        # type one web page
        descriptions = tree.xpath("//p[@class='details-p']/text()")
        description = remove_white(descriptions[0]) if len(descriptions) > 0 else ""
        # type two web page
        if len(description) <= 0:
            descriptions = tree.xpath("//div[@class='details-ui clearfix']"
                                      "/h2[@class='details-h2old']/text()")
            description = remove_white(descriptions[0]) if len(descriptions) > 0 else ""
        return description

    def _extract_content_text(self, tree):
        """解析出content_text值
            Args:
                tree:Etree, 树节点
            Returns:
                content_text, str, 提取出来的内容
        """
        goods_elems = tree.xpath("//div[@id='goodsAll_info_div']//div[@class='xqtext-table']")
        temp_texts = []
        if goods_elems is not None and len(goods_elems) > 0:
            for good_elem in goods_elems:
                for child_elem in good_elem:
                    if child_elem.tag == "table":
                        extract_table(child_elem, temp_texts)
                    else:
                        for text in child_elem.itertext():
                            stripped_text = remove_white(text)
                            if len(stripped_text) > 0:
                                temp_texts.append("-")
                                temp_texts.append(" " + stripped_text)
                                temp_texts.append("N_line")

        if len(temp_texts) > 1:
            temp_texts.pop()
        content_text = u"".join(temp_texts)
        return content_text

    def _extract_refund(self, tree):
        """解析出refund
            Args:
                tree:Etree, 树节点
            Returns:
                content:str, refund值
        """
        contents = tree.xpath(u"//a[@title='支持未消费退款' or @title='不支持未消费退款']/@title")
        content = remove_white(contents[0]) if contents else ""
        if content == u"不支持未消费退款":
            content = u"不支持退款"
        return content

    def _extract_place(self, tree):
        """解析出地址
            Args:
                tree:Etree, 节点
            Returns:
                places:list, 地址列表
        """
        elem = tree.xpath('//div[@class="sp_list"]//li')
        places = []
        for li_elem in elem:
            a_place = {}
            place_names = li_elem.xpath("h3/a/text()")
            a_place['place_name'] = remove_white(place_names[0]) if place_names else ""
            place_address = li_elem.xpath("p/span[1]/text()")
            a_place['address'] = remove_white(place_address[0]) if place_address else ""
            place_phones = li_elem.xpath("p/span[2]/text()")
            a_place['place_phone'] = remove_white(place_phones[0]) if place_phones else ""
            a_place['longitude'] = u""
            a_place['latitude'] = u""
            open_times = li_elem.xpath("p/span[3]/text()")
            a_place['open_time'] = remove_white(open_times[0]) if open_times else ""
            places.append(a_place)
        return places

    def _extract_noticed(self, tree):
        """从网页中解析出notice
            特殊情况没有处理55tuan.com/goods-ca3c096c967ddc87.html
            http://changsha.55tuan.com/goods-21150d55e8496018.html
            http://www.55tuan.com/goods-ada26875586dae46.html
            Args:
                tree: Etree
            Returns:
                text: str,
        """
        text_splits = []
        noticed_elem = tree.xpath("//div[@class='xqtext_clue']")
        extract_dl(noticed_elem, text_splits)

        if len(text_splits) < 1:
            elems = tree.xpath("//div[@id='goodsAll_info_div']/p|div")
            for elem in elems:
                extract_help(elem, text_splits)

            elems_more = tree.xpath("//div[@id='goodsAll_info_div']/div//div")
            for elem in elems_more:
                extract_help(elem, text_splits)

        if len(text_splits) > 1:
            text_splits.pop()
        notice_content = u"".join(text_splits)
        return notice_content

def extract_help(elem, text_splits):
    """解析notice文档
        Args:
            elem, Element, 元素节点
            text_splits, list, 数组列表
    """
    temp_texts = []
    is_noticed_text = False

    for text in elem.itertext():
        stripped_text = remove_white(text)
        if len(stripped_text) > 1 :
            temp_texts.append(" " + stripped_text)
            temp_texts.append("N_line")
            if stripped_text.rfind(u"小编紧箍咒") != -1 or \
                stripped_text.rfind(u"小编碎碎念") != -1 or \
                stripped_text.rfind(u"窝窝温馨提示") != -1 or \
                stripped_text.rfind(u"窝窝小贴士") != -1 or \
                stripped_text.rfind(u"有话要说") != -1 or \
                stripped_text.rfind(u"窝窝提示") != -1 or \
                stripped_text.rfind(u"小编提示") != -1 or \
                stripped_text.rfind(u"温馨提示") != -1 or \
                stripped_text.rfind(u"小编絮叨ING") != -1 or \
                stripped_text.rfind(u"小编紧箍咒") != -1 :
                is_noticed_text = True

    if is_noticed_text:
        text_splits.extend(temp_texts)

class PictureParser(BaseParser):
    """用于处理图片下载请求
    """
    def __init__(self, namespace):
        BaseParser.__init__(self, namespace)
        self.logger.debug("init PictureParser")

    def parse(self, task, input_file):
        if task.kwargs.has_key('picturepath'):
            picture_item = PictureItem(input_file.read(), task.kwargs.get('picturepath'))
            yield picture_item
