#!/usr/bin/python
#-*- coding=utf-8 -*-

"""代理模块
"""

__author__ = ['"wuyadong" <wuyadong@tigerknows.com>']

import csv
from tigerspider.core.util import get_project_path


PROXY_FILE_PATH = "data/proxy.dat"


def get_proxy():
    """获取一个可用的代理(简单的轮巡)
        Returns:
            proxy_host: str, proxy host
            proxy_port: int, proxy port
    """
    if not hasattr(get_proxy, "proxy_list"):
        # 初始化proxy_list
        proxys = _read_proxys()
        setattr(get_proxy, "proxy_list", proxys)
        setattr(get_proxy, "proxy_index", 0)

    proxy_list = getattr(get_proxy, "proxy_list")
    proxy_index = getattr(get_proxy, "proxy_index")
    if len(proxy_list) == 0:
        return None, None
    else:
        proxy_host, proxy_port = proxy_list[proxy_index]
        temp_index = (proxy_index + 1) % len(proxy_list)
        setattr(get_proxy, "proxy_index", temp_index)
        return proxy_host, proxy_port


def reload_proxy():
    """重新加载Proxy.dat文件
    """
    # 初始化proxy_list
    proxys = _read_proxys()
    setattr(get_proxy, "proxy_list", proxys)
    setattr(get_proxy, "proxy_index", 0)


def _read_proxys():
    """加载proxy列表
        Returns:
            proxy_list: list, proxy list
    """
    proxys = []

    # 读入代理列表
    with open(get_project_path() + PROXY_FILE_PATH, "rb") as in_file:
        csv_reader = csv.reader(in_file, lineterminator="\n")
        for line in csv_reader:
            if len(line) != 0:
                host, port = line[0], line[1]
                proxys.append((str(host), int(port)))
    return proxys