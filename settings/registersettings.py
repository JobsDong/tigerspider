#!/usr/bin/python2.7
#-*- coding=utf-8 -*-

# Copy Rights (c) Beijing TigerKnows Technology Co., Ltd.

'''
所有实现的spider和schedule都必须到这里进行注册，否则无效
'''

__author__ = ['"wuyadong" <wuyadong@tigerknows.com>']


spiders = [
    'spiders.meituan.spider.MeituanSpider',
    'spiders.tuan55.spider.Tuan55Spider',
    'spiders.nuomi.spider.NuomiSpider',
    'spiders.ganji.spider.GanjiSpider',
    'spiders.mtime.spider.MtimeSpider',
]

schedules = [
    'schedules.schedules.RedisSchedule',
]
