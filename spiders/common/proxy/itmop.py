#!/usr/bin/python2.7
#-*- coding=utf-8 -*-

# Copy Rights (c) Beijing TigerKnows Technology Co., Ltd.

__authors__ = ['"wuyadong" <wuyadong@tigerknows.com>']

import datetime
import logging
from lxml import etree
from tornado.httpclient import HTTPClient

from core.util import remove_white
from core.proxy import Proxy

ITMOP_URL = "http://www.itmop.com/proxy/"

itmop_logger = logging.getLogger("spiders-common-proxy-itmop")

def _get_lastest_proxy_entrance_url_from_itmop(url):
    """获取最新的proxy入口地址
        Returns:
            url: str, 如果正确获取就返回url否则是None
    """
    http_client = HTTPClient()
    resp = http_client.fetch(url, connect_timeout=5, request_timeout=10)
    if resp.code != 200 and resp.error is not None:
        itmop_logger.warn("get lastes proxy entrance url failed, url:%s erro:%s" %
                          (url, resp.error))
        return None
    else:
        try:
            url = _extract_entrance_url_from_itmop(resp.body)
        except Exception, e:
            itmop_logger.warn("parse itmop.com failed: error:%s" % e)
            return None
        else:
            return url

def _extract_entrance_url_from_itmop(body):
    """解析host主页，解析出最新的entrance
        Args:
            body: html文档
        Returns:
            url: str 入口地址
    """
    tree = etree.HTML(body)
    new_list = tree.xpath('//div[@id="NEW_INFO_LIST"]//dt/a')

    # 获取最新的日期
    def _get_date():
        date_str = u"%d年%d月%d日" % (datetime.datetime.now().year,
                                datetime.datetime.now().month,
                                datetime.datetime.now().day)
        return date_str

    # 判断是否是最新的数据
    def _is_lastest_http_proxy_elem(info_elem):
        if info_elem is not None:
            if info_elem.text.find(_get_date()) != -1 and\
                info_elem.text.find(u"代理"):
                return True
            else:
                return False
        else:
            return False

    for new_info in new_list:
        if _is_lastest_http_proxy_elem(new_info):
            return new_info.attrib['href']

def _get_proxys_from_itmop_proxy(url):
    """获取itmop/proxy中的proxy列表
    """
    http_client = HTTPClient()
    resp = http_client.fetch(url, connect_timeout=5, request_timeout=10)
    if resp.error:
        itmop_logger.warn("get proxys from itmop proxy failed.url:%s error:%s" %
                          (url, resp.error))
        return []
    else:
        try:
            proxys = _extract_proxy_from_itmop(resp.body)
        except Exception, e:
            itmop_logger.warn("parse itmop proxy list failed:%s" % e)
            return []
        else:
            return proxys

def _extract_proxy_from_itmop(body):
    """解析代理列表
        Args:
            body: str, html文档
        Returns:
            proxys: list, [(ip, port)]
    """
    tree = etree.HTML(body)
    proxy_strs = tree.xpath('//div[@class="NEW_CONTENT LEFT"]//p')

    proxy_list = []
    if proxy_strs is not None and len(proxy_strs) >= 1:
        for proxy_str in proxy_strs[0].itertext():
            if proxy_str:
                try:
                    host, port = extract_str(proxy_str)
                except Exception, e:
                    pass
                else:
                    proxy_list.append(Proxy(str(host), port))

    return proxy_list

# 从字符串中提取ip和port
def extract_str(proxy_str):
    dot = proxy_str.index(u"@HTTP")
    host_and_port = proxy_str[:dot].split(u":")
    if len(host_and_port) == 2:
        port = int(remove_white(host_and_port[1]))
        host = remove_white(host_and_port[0])
        return (host, port)

def get_proxy_from_itmop():
    entrance_url = _get_lastest_proxy_entrance_url_from_itmop(ITMOP_URL)
    if entrance_url:
        return _get_proxys_from_itmop_proxy(entrance_url)
    else:
        return []

