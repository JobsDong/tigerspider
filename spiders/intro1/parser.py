#!/usr/bin/python
#-*- coding=utf-8 -*-

__author__ = ['"wuyadong" <wuyadong@tigerknows.com>']

from lxml import html

from core.util import flist
from core.spider.parser import BaseParser
from spiders.intro1.items import WebItem


class ActivityParser(BaseParser):
    """用于解析活动详情页面的解析器
    """
    def __init__(self, namespace):
        BaseParser.__init__(self, namespace)
        self.logger.info(u"init Activity Parser finished")

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
        name = flist(tree.xpath(u"//div["
                                u"@clas='product-price-titleul']/h1/text()"))
        desc_elems = tree.xpath(u"//div[@class='product-detail-alla-cont']")
        description = _extract_desc_elems(desc_elems)
        date_elems = tree.xpath(
            u"//ul[@class='productnew-header-pricea2-ul clearfloat']/li/@d")
        telephone = flist(tree.xpath(
            u"//div[@class='top-w']//li[@class='tel']/span/text()"))
        telephone = telephone.replace(u"-", u"")
        if len(telephone) == 0:
            telephone = u"4006228228"
        price_elems = tree.xpath(
            u"//ul[@class='productnew-header-pricec2-ul productnew-"
            u"header-pricec3-ul productnew-header-pricec2-cq']/li/@title")
        price_infos = list()
        for price_elem in price_elems:
            if unicode(price_elem) not in price_infos:
                price_infos.append(unicode(price_elem))
        price_info = u"/".join(price_infos)
        time_infos = []
        for date_elem in date_elems:
            time_infos.append(date_elem)
        time_info = u";".join(time_infos)
        url = task.request.url

        # 保存详情信息
        yield WebItem(url, telephone, description,
                      time_info, price_info, name)


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