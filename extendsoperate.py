#!/usr/bin/python2.7
#-*- coding=utf-8 -*-

# Copy Rights (c) Beijing TigerKnows Technology Co., Ltd.

"""用于完成额外的操作，但不属于webspider中的功能
"""
__authors__ = ['"wuyadong" <wuyadong@tigerknows.com>']

import logging.config
from tornado.options import define, parse_command_line, options

from spiders.mtime import mtimeoperate

define('operate', default='help', type=str, help="operate:")
define('service', default=None, type=str, help="spider:")

# proxy
define('host', default="127.0.0.1", type=str, help="host:")
define('port', default='8087', type=str, help="port:")
define('score', default=10, type=int, help="score:")

logging.config.fileConfig("logging.conf")

if __name__ == "__main__":
    parse_command_line()

    if options.service == "mtime":
        mtimeoperate.operate(options.operate)

    else:
        print "error service"


