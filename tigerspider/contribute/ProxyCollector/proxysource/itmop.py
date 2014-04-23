#!/usr/bin/python
#-*- coding=utf-8 -*-

__author__ = ['"wuyadong" <wuyadong@tigerknows.com>']

import datetime
import requests
from lxml import html, etree
from StringIO import StringIO

ITMOP_URL = "http://www.56ads.com/proxyip/"
ITMOP_HOST = "http://www.56ads.com"


def get_proxys(start_date=None, end_date=None):
    """获取代理服务器, 只是支持第一页中的start_date和end_date
        Args:
            start_date: datetime, 起始时间
            end_date: datetime, 结束时间
        Returns:
            proxys: list,[(proxy_host, proxy_port)
    """
    # 1. 获取主页
    print "get itmop homepage"
    headers = {'Accept': 'text/html,application/xhtml+xml,'
                         'application/xml;q=0.9,*/*;q=0.8',
               'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux '
                             'x86_64; rv:25.0) Gecko/20100101 Firefox/25.0',
               'Host': 'www.56ads.com'}
    r_homepage = requests.get(ITMOP_URL, headers=headers)
    r_homepage.encoding = 'gb2312'
    content = r_homepage.text

    # 2. 解析主页，获取所需的日期对应的页面地址
    urls = _extract_entrance_url_from_itmop(content, start_date, end_date)

    # 3. 获取代理页面，解析出代理
    proxy_set = set()
    for url in urls:
        r_proxy = requests.get(url, headers=headers)
        r_proxy.encoding = 'gb2312'
        proxys = _extract_proxy_from_itmop(r_proxy.text)
        print "get proxys:", len(proxys)
        proxy_set = proxy_set.union(set(proxys))

    return proxy_set


def _extract_entrance_url_from_itmop(body, start_date, end_date):
    """解析host主页，解析出最新的entrance
        Args:
            body: html文档
            start_date: datetime, 开始时间
            end_date: datetime, 结束时间
        Returns:
            urls: list: [str] 入口地址
    """
    tree = html.parse(StringIO(body))
    new_list = tree.xpath('//div[@class="listbox"]//ul/li/a')

    # 获取最新的日期
    def _get_date_strs():
        temp_date = start_date
        date_strs = []
        while temp_date <= end_date:
            date_str = u"%d年%d月%d日" % (temp_date.year,
                                         temp_date.month,
                                         temp_date.day)
            date_str2 = u"%d.%d.%d" % (temp_date.year,
                                       temp_date.month,
                                       temp_date.day)
            date_strs.append(date_str)
            date_strs.append(date_str2)
            temp_date = temp_date + datetime.timedelta(days=1)
        return date_strs

    # 判断是否是最新的数据
    def _is__http_proxy_elem(info_elem):
        if info_elem is not None:
            if info_elem.text.find(u"代理") == -1:
                return False
            date_strs = _get_date_strs()
            for date_str in date_strs:
                if info_elem.text.find(date_str) != -1:
                    return True
            else:
                return False
        else:
            return False
    urls = [new_info.attrib['href'] for new_info in new_list
            if _is__http_proxy_elem(new_info)]
    urls = [ITMOP_HOST+path for path in urls]

    return urls


def _extract_proxy_from_itmop(body):
    """解析代理列表
        Args:
            body: str, html文档
        Returns:
            proxys: list, [(ip, port)]
    """
    tree = html.parse(StringIO(body))
    proxy_elems = tree.xpath('//div[@class="content"]//br')

    proxy_list = []

    for proxy_elem in proxy_elems:
        proxy_str = etree.tounicode(proxy_elem, method='html')\
            .replace(u"<br />", u"")\
            .replace(u"<br/>", u"")\
            .replace(u"<br>", u"")
        if proxy_str:
            print proxy_str
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
    start_dot = proxy_str.index(u";")
    host_and_port = proxy_str[start_dot+1:dot].split(u":")
    if len(host_and_port) == 2:
        port = int(host_and_port[1].strip())
        host = str(host_and_port[0].strip())
        return host, port

if __name__ == "__main__":
    for proxy in get_proxys(datetime.datetime.now(),
                            datetime.datetime.now()):
        print proxy[0], proxy[1]