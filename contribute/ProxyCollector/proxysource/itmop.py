#!/usr/bin/python
#-*- coding=utf-8 -*-

__author__ = ['"wuyadong" <wuyadong@tigerknows.com>']

import os.path
import csv
import datetime
import requests
from lxml import etree
from config import main_config
from validate import validate_proxys

ITMOP_URL = "http://www.itmop.com/proxy/"
ITMOP_FILE = "itmop"


def get_proxys():
    """获取所有的代理
        Returns:
            proxys: list, [(host, port)]
    """
    # 读取itmop的proxy
    proxy_dat_path = main_config.PROXY_DAT_FILE_PATH
    if not os.path.exists(proxy_dat_path):
        return []
    else:
        proxys = _read_proxys(proxy_dat_path)
        return list(proxys)


def update_proxy(start_date=None, end_date=None, threshold=0.7):
    """更新代理服务器, 只是支持第一页中的start_date和end_date
        Args:
            start_date: datetime, 起始时间
            end_date: datetime, 结束时间
            threshold: float, 最小成功率
        Returns:
            is_ok: boolean, 描述是否成功
    """
    # 1. 获取主页
    print "get itmop homepage"
    headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
               'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:25.0) Gecko/20100101 Firefox/25.0',
               'Host': 'www.itmop.com'}
    r_homepage = requests.get(ITMOP_URL, headers=headers)
    content = r_homepage.text

    # 2. 解析主页，获取所需的日期对应的页面地址
    urls = _extract_entrance_url_from_itmop(content, start_date, end_date)

    # 3. 获取代理页面，解析出代理
    proxy_set = set()
    for url in urls:
        r_proxy = requests.get(url, headers=headers)
        proxys = _extract_proxy_from_itmop(r_proxy.text)
        print "get proxys:", len(proxys)
        proxy_set = proxy_set.union(set(proxys))

    # 4. 更新持久化的proxy
    proxy_dat_file_path = main_config.PROXY_DAT_FILE_PATH
    history_proxys = _read_proxys(proxy_dat_file_path) if os.path.exists(proxy_dat_file_path) else set()
    print "read history proxy:", len(history_proxys)

    # 5. 验证有效性
    proxy_list = list(proxy_set.union(history_proxys))
    print "start to validate proxys"
    success_pers = validate_proxys(proxy_list, max_clients=main_config.MAX_CLIENTS,
                                   interval=main_config.INTERVAL)
    print "end to validate proxys"

    _write_proxys([proxy_list[i] for i, success_per in enumerate(success_pers) if success_per >= threshold],
                  proxy_dat_file_path)
    print "write proxy into file end"

    return True


def _extract_entrance_url_from_itmop(body, start_date, end_date):
    """解析host主页，解析出最新的entrance
        Args:
            body: html文档
            start_date: datetime, 开始时间
            end_date: datetime, 结束时间
        Returns:
            urls: list: [str] 入口地址
    """
    tree = etree.HTML(body)
    new_list = tree.xpath('//div[@id="NEW_INFO_LIST"]//dt/a')

    # 获取最新的日期
    def _get_date_strs():
        temp_date = start_date
        date_strs = []
        while temp_date <= end_date:
            date_str = u"%d年%d月%d日" % (temp_date.year, temp_date.month, temp_date.day)
            date_str2 = u"%d.%d.%d" % (temp_date.year, temp_date.month, temp_date.day)
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

    return urls


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


def _write_proxys(proxys, dat_path):
    """将proxys写入dat_path文件中
        Args:
            proxys: set, [(host, port)]
            dat_path: str, dat文件路径
    """
    with open(dat_path, "wb") as out_file:
        csv_writer = csv.writer(out_file, lineterminator="\n")
        for host, port in proxys:
            csv_writer.writerow([host.encode('utf-8'), port])


def _read_proxys(dat_path):
    """将proxy读入
        Args:
            dat_path: str, dat文件路径
        Returns:
            proxy_set: set, proxy集合
    """
    proxy_set = set()
    with open(dat_path, "rb") as in_file:
        csv_reader = csv.reader(in_file, lineterminator="\n")
        for line in csv_reader:
            host, port = line[0], line[1]
            proxy_set.add((str(host), int(port)))
    return proxy_set


if __name__ == "__main__":
    print update_proxy(datetime.datetime(year=2014, month=1, day=1), datetime.datetime.now())