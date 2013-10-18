#!/usr/bin/python2.7
#-*- coding=utf-8 -*-

# Copy Rights (c) Beijing TigerKnows Technology Co., Ltd.

""" webspider的入口程序
"""

__author__ = ['"wuyadong" <wuyadong@tigerknows.com>']

import logging.config
from core.util import walk_settings
from web.service import WebService

logging.config.fileConfig("logging.conf")

if __name__ == "__main__":
    walk_settings()
    web_service = WebService()
    web_service.start(1235)
