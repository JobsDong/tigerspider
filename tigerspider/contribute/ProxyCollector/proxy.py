#!/usr/bin/python
#-*- coding=utf-8 -*-


"""
Usage:
proxy.py update_proxy [--start=<argument>] [--end=<argument>]
proxy.py validate_proxy

Options:
  --start S  start date YYYY-MM-dd default is today
  --end E    end date YYYY-MM-dd default is today
"""

__author__ = ['"wuyadong" <wuyadong@tigerknows.com>']

import datetime
import docopt
import os
from proxysource import itmop, youdaili
from utils import util, validate
from config import main_config


def validate_proxy():
    """验证代理
    """
    # 获取本地代理
    proxy_dat_file_path = main_config.PROXY_DAT_FILE_PATH
    history_proxys = util.read_proxys(proxy_dat_file_path) if os.path.exists(proxy_dat_file_path) else set()
    print "read history proxy:", len(history_proxys)

    # 验证代理
    proxy_list = list(history_proxys)
    print "start to validate proxys"
    success_pers = validate.validate_proxys(proxy_list, max_clients=main_config.MAX_CLIENTS,
                                            interval=main_config.INTERVAL)
    print "end to validate proxys:", len(proxy_list)

    # 持久化代理
    util.write_proxys([proxy_list[i] for i, success_per in enumerate(success_pers)
                       if success_per >= main_config.PROXY_THRESHOLD],
                      proxy_dat_file_path)
    print "write proxy into file end"


def update_proxy(start_date, end_date):
    """获取最新的代理，并且验证代理
    """
    # itmop
    itmop_proxys = itmop.get_proxys(start_date, end_date)
    print "itmop_proxys update:", len(itmop_proxys)

    # youdaili
    youdaili_proxys = youdaili.get_proxys(start_date, end_date)
    print "youdaili_proxys update:", len(youdaili_proxys)

    # 历史
    proxy_dat_file_path = main_config.PROXY_DAT_FILE_PATH
    history_proxys = util.read_proxys(proxy_dat_file_path) if os.path.exists(proxy_dat_file_path) else set()
    print "read history proxy:", len(history_proxys)

    # 合并
    proxy_list = list(youdaili_proxys.union(history_proxys).union(itmop_proxys))
    print "union history, itmop, youdaili proxys:", len(proxy_list)

    # 验证
    print "start to validate proxys"
    success_pers = validate.validate_proxys(proxy_list, max_clients=main_config.MAX_CLIENTS,
                                            interval=main_config.INTERVAL)
    print "end to validate proxys"

    # 持久化代理
    util.write_proxys([proxy_list[i] for i, success_per in enumerate(success_pers)
                       if success_per >= main_config.PROXY_THRESHOLD],
                      proxy_dat_file_path)
    print "write proxy into file end"


if __name__ == "__main__":
    arguments = docopt.docopt(__doc__, version="proxy collector v1.0")

    if arguments['update_proxy']:
        if arguments['--start'] is None:
            start_date = datetime.datetime.now()
        else:
            start_date = datetime.datetime.strptime(arguments["--start"], "%Y-%m-%d")

        if arguments["--end"] is None:
            end_date = datetime.datetime.now()
        else:
            end_date = datetime.datetime.strptime(arguments['--end'], "%Y-%m-%d")

        update_proxy(start_date, end_date)
    elif arguments['validate_proxy']:
        validate_proxy()
    else:
        print "should be validate_proxy or update_proxy"