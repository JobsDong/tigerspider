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
    'spiders.mtime.spider.MtimeSpider',
    'spiders.ganji.spider.GanjiSpider',
    # 'spiders.baiduoffset.spider.BaiduoffsetSpider',
    # 'spiders.baiduoffset1.spider.BaiduoffsetSpider',
    # 'spiders.baiduoffset2.spider.BaiduoffsetSpider',
    # 'spiders.baiduoffset3.spider.BaiduoffsetSpider',
    # 'spiders.baiduoffset4.spider.BaiduoffsetSpider',
]

schedules = [
    'schedules.schedules.RedisSchedule',
    # 'schedules.nostoreschedule.NostoreSchedule',
]
