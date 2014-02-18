#!/usr/bin/python
#-*- coding=utf-8 -*-

"""Proxy Collector的配置文件
"""

__author__ = ['"wuyadong" <wuyadong@tigerknows.com>']

# 测试网页的url
TEST_WEBS = (
    {'url': "http://www.baidu.com", 'connect_timeout': 2, 'request_timeout': 5},
    {'url': "http://www.meituan.com", 'connect_timeout': 2, 'request_timeout': 10},
    {'url': "http://www.55tuan.com", 'connect_timeout': 2, 'request_timeout': 10},
    {'url': "http://www.nuomi.com", 'connect_timeout': 2, 'request_timeout': 10},
    {'url': "http://www.ctrip.com", 'connect_timeout': 2, 'request_timeout': 10},
    {'url': "http://www.sina.com.cn", 'connect_timeout': 2, 'request_timeout': 10},
    {'url': "http://www.qq.com", 'connect_timeout': 2, 'request_timeout': 10},
    {'url': "http://www.sohu.com", 'connect_timeout': 2, 'request_timeout': 10},
    {'url': "http://www.163.com", 'connect_timeout': 2, 'request_timeout': 10},
    {'url': "http://www.taobao.com", 'connect_timeout': 2, 'request_timeout': 10}
)

# 默认headers
DEFAULT_HEADER = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "en-US,en;q=0.5",
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:25.0) Gecko/20100101 Firefox/25.0",
}

# 最大连接数
MAX_CLIENTS = 20
# 最大访问间隔
INTERVAL = 500
# 更新的文件路径
PROXY_DAT_FILE_PATH = "/home/wuyadong/git/tigerknows-spider/data/proxy.dat"