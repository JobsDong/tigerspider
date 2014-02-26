#!/usr/bin/python
#-*- coding=utf-8 -*-


"""
Usage:
proxy.py update_proxy [--start=<argument>] [--end=<argument>]

Options:
  --start S  start date YYYY-MM-dd default is today
  --end E    end date YYYY-MM-dd default is today
"""
from tigerspider.contribute.ProxyCollector.config import main_config
from tigerspider.contribute.ProxyCollector.proxysource import itmop, youdaili

__author__ = ['"wuyadong" <wuyadong@tigerknows.com>']

import datetime
import docopt
import os
from tigerspider.contribute.ProxyCollector.utils import util, validate


def update_proxy(start_date, end_date):
    """ 更新代理
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
    avaliable_proxy_list = [proxy_list[i] for i, success_per in enumerate(success_pers)
                            if success_per >= main_config.PROXY_THRESHOLD]
    print "avaliable proxys:", len(avaliable_proxy_list)

    util.write_proxys(avaliable_proxy_list, proxy_dat_file_path)
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
    else:
        print "should be get_proxy or update_proxy"