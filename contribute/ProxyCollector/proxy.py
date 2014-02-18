#!/usr/bin/python
#-*- coding=utf-8 -*-


"""
Usage:
proxy.py update_proxy [--start=<argument>] [--end=<argument>]

Options:
  --start S  start date YYYY-MM-dd default is today
  --end E    end date YYYY-MM-dd default is today
"""

__author__ = ['"wuyadong" <wuyadong@tigerknows.com>']

import datetime
import docopt
from proxysource import itmop

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

        # itmop
        itmop.update_proxy(start_date, end_date)
    else:
        print "should be get_proxy or update_proxy"