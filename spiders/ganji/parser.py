#!/usr/bin/python
# -*- coding: utf-8 -*-

"""定义了ganji中的所有解析的類
    CityParser: 解析城市入口地址的类
    CommunityParser: 解析小区信息的类
    replace_url_path: url合并函数
"""

import urlparse
from lxml import etree
from tornado.httpclient import HTTPRequest

from core.spider.parser import BaseParser
from core.datastruct import Task

from spiders.ganji.items import CityItem
from spiders.ganji.util import (build_url, get_city_code)
from spiders.ganji.items import CommunityItem
from core.util import remove_white


class CityParser(BaseParser):
    """用於解析城市列表的類
    """

    def __init__(self, namespace):
        """构造函数
            Args:
                namespace: str, 这是上层传递的名字空间
        """
        BaseParser.__init__(self, namespace)
        self.logger.debug("init ganji CityParser")

    def parse(self, task, response):
        """用於解析城市的html
            Args:
                task: Task, 任務描述
                response: HttpResponse, 網頁結果
            Yields:
                city_item: CityItem， 保存城市信息的类
                task: Task: 新的任务
        """
        self.logger.debug("CityParser start")
        try:
            tree = etree.HTML(response.body)
            elements = tree.xpath("//div[@class='all-city']//a")

            for city_element in elements:
                city_item = CityItem(city_element.text,
                                     get_city_code(city_element.text))
                if city_item.chinese_name and city_item.city_code:
                    yield city_item
                    #print city_element.attrib['href']

                    http_request = HTTPRequest(url=build_url(
                                               city_element.attrib['href']),
                                               connect_timeout=20,
                                               request_timeout=240)
                    new_task = Task(http_request, callback='CommunityParser',
                                    cookie_host='http://www.ganji.com/index.htm',
                                    cookie_count=15,
                                    kwargs={'cityname': city_item.city_code})
                    print city_element.attrib['href']

                    http_request = HTTPRequest(url=build_url(
                                               city_element.attrib['href']),
                                               connect_timeout=5,
                                               request_timeout=10)
                    new_task = Task(http_request, callback='CommunityParser',
                                    cookie_host=city_element.attrib['href'],
                                    cookie_count=15,
                                    kwargs={'citycode': city_item.city_code})
                    yield new_task
                else:
                    self.logger.warn("this item's property is none(chinese:%s,"
                                     " citycode:%s)" %
                                     (city_item.chinese_name,
                                      city_item.city_code))

        finally:
            self.logger.debug("city parse end to parse")


def replace_url_path(url, path):
    """将某个url中的路径进行修改
        Args:
            url: str, url
            path: str，目标路径
        Returns:
            url: str, 新的url
    """
    schema, host, _, _, _ = urlparse.urlsplit(url)
    return urlparse.urlunsplit((schema, host, path, "", ""))


class CommunityParser(BaseParser):
    """用于解析小区信息
    """
    def parse(self, task, response):
        """解析函数
            task:Task, 任务描述
            response:HTTPResponse, 下载的结果
        """
        tree = etree.HTML(response.body)
        if '下面的验证码' in response.body:
            print '遇到验证码了'
        elems = tree.xpath("//div[@class='listBox']//dl[@class='list-xq']")
        for elem in elems:
            community_name = elem.xpath("dd[@class='xq-detail']/p[1]/a/text()")
            community_name = remove_white(community_name[0]) \
                if len(community_name) > 0 else ""
            city_name = task.kwargs['citycode']
            address = elem.xpath("dd[@class='xq-detail']"
                                 "/p[@class='xiaoqu-street']/text()")
            address = address[0] if len(address) > 0 else ""
            address = remove_white(address.replace(u"地址:", ""))
            yield CommunityItem(city_name, community_name, address)

        next_url_path = tree.xpath("//div[@class='pageBox']//a[@class='next']/@href")
        if len(next_url_path) > 0:
            next_url_path = next_url_path[0]
            host = replace_url_path(task.request.url, next_url_path)
            http_request = HTTPRequest(host, connect_timeout=5, request_timeout=10)
            next_task = Task(http_request, callback="CommunityParser",
                             cookie_host="http://www.ganji.com", cookie_count=15,
                             kwargs={'cityname': task.kwargs['cityname']})
            yield next_task
