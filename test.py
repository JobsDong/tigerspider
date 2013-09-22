#!/usr/bin/python2.7
#-*- coding=utf-8 -*-

# Copy Rights (c) Beijing TigerKnows Technology Co., Ltd.

__authors__ = ['"wuyadong" <wuyadong@tigerknows.com>']

from core.db import DB

import json

if __name__ == "__main__":
    db = DB(host="192.168.11.195", port=5432, database="test",
            user="postgres", password="titps4gg")
    infos = db.execute_query("select info from rt_crawl where source='55tuan'")
    discount_type = {}

    for info in infos:
        temp_dict = json.loads(info[0])
        hello_type = temp_dict.get('discount_type')
        discount_type[hello_type] = 0 if not discount_type.has_key(hello_type) \
            else discount_type.get(hello_type) + 1

    for key, value in discount_type.items():
        print key, value