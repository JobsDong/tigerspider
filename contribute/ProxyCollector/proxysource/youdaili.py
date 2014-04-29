#!/usr/bin/python
#-*- coding=utf-8 -*-

__author__ = ['"wuyadong" <wuyadong@tigerknows.com>']

import requests
import datetime
from lxml import etree


YOUDAILI_URL = "http://www.youdaili.cn/Daili/guonei"


def get_proxys(start_date=None, end_date=None):
    """更新代理服务器, 只是支持第一页中的start_date和end_date
        Args:
            start_date: datetime, 起始时间
            end_date: datetime, 结束时间
        Returns:
            proxys: set, [(proxy_host, proxy_port)]
    """
    # 1. 获取主页
    print "get youdaili homepage"
    headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;'
                         'q=0.9,*/*;q=0.8',
               'Cookie': '',
               'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:25.0)'
                             ' Gecko/20100101 Firefox/25.0'}
    r_homepage = requests.get(YOUDAILI_URL, headers=headers)
    r_homepage.encoding='utf-8'
    content = r_homepage.text

    # 2. 解析主页，获取所需的日期对应的页面地址
    urls = _extract_entrance_url_from_youdaili(content, start_date, end_date)

    # 3. 获取代理页面，解析出代理
    proxy_set = set()
    for url in urls:
        r_proxy = requests.get(url, headers=headers)
        proxys = _extract_proxy_from_youdaili(r_proxy.text)
        print "get proxys:", len(proxys)
        proxy_set = proxy_set.union(set(proxys))

    return proxy_set


def _extract_entrance_url_from_youdaili(body, start_date, end_date):
    """解析host主页，解析出最新的entrance
        Args:
            body: html文档
            start_date: datetime, 开始时间
            end_date: datetime, 结束时间
        Returns:
            urls: list: [str] 入口地址
    """
    tree = etree.HTML(body)
    new_list = tree.xpath("//ul[@class='newslist_line']/li/a")

    # 获取最新的日期
    def _get_date_strs():
        temp_date = start_date
        date_strs = []
        while temp_date <= end_date:
            date_str = u"%d月%d日" % (temp_date.month, temp_date.day)
            date_strs.append(date_str)
            temp_date = temp_date + datetime.timedelta(days=1)
        return date_strs

    # 判断是否是最新的数据
    def _is__http_proxy_elem(info_elem):
        if info_elem is not None:
            text_all = u"".join(info_elem.itertext())
            if text_all.rfind(u"代理") == -1:
                return False

            date_strs = _get_date_strs()
            for date_str in date_strs:
                if text_all.rfind(date_str) != -1:
                    return True
            else:
                return False
        else:
            return False

    urls = [new_info.attrib['href'] for new_info in new_list
            if _is__http_proxy_elem(new_info)]

    return urls


def _extract_proxy_from_youdaili(body):
    """解析代理列表
        Args:
            body: str, html文档
        Returns:
            proxys: list, [(ip, port)]
    """
    tree = etree.HTML(body)
    proxy_strs = tree.xpath('//div[@class="cont_font"]//p')

    proxy_list = []

    if proxy_strs is not None and len(proxy_strs) >= 1:
        for proxy_str in proxy_strs[0].itertext():
            if proxy_str:
                try:
                    host, port = _extract_str(proxy_str)
                except Exception, e:
                    pass
                else:
                    proxy_list.append((host, port))
    return proxy_list


def _extract_str(proxy_str):
    """从字符串中解析出host和
        Args:
            proxy_str: str, 字符串
        Returns:
            host, port: tuple, (str, int)
    """
    dot = proxy_str.index(u"@HTTP")
    host_and_port = proxy_str[:dot].split(u":")
    if len(host_and_port) == 2:
        port = int(host_and_port[1].strip())
        host = str(host_and_port[0].strip())
        return host, port

if __name__ == "__main__":
    for proxy in get_proxys(datetime.datetime(year=2014, month=2, day=26),
                            datetime.datetime.now()):
        print proxy[0], proxy[1]