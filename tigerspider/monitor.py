#!/usr/bin/python2.7
#-*- coding=utf-8 -*-

""" webspider的入口程序
"""

__author__ = ['"wuyadong" <wuyadong@tigerknows.com>']

import logging.config
import sys

from tigerspider.core.util import walk_settings
from tigerspider.web.service import WebService


logging.config.fileConfig(sys.path[0] + "/logging.conf")

if __name__ == "__main__":
    walk_settings()
    web_service = WebService()
    web_service.start(1235)
