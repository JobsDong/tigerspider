#!/usr/bin/python2.7
#-*- coding=utf-8 -*-

# Copy Rights (c) Beijing TigerKnows Technology Co., Ltd.

"""用于完成额外的操作，但不属于webspider中的功能
"""
from spiders.common.proxy import proxyoperate

__authors__ = ['"wuyadong" <wuyadong@tigerknows.com>']

import logging.config
from tornado.options import define, parse_command_line, options

from spiders.mtime import mtimeoperate

define('operate', default='help', type=str, help="operate:")
define('service', default=None, type=str, help="spider:")

logging.config.fileConfig("logging.conf")

if __name__ == "__main__":
    parse_command_line()

    if options.service == "mtime":
        mtimeoperate.operate(options.operate)

    elif options.service == "proxy":
        proxyoperate.operate(options.operate)

    else:
        print "error service"


