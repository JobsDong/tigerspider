#!/usr/bin/python2.7
#-*- coding=utf-8 -*-

"""
所有实现的spider和schedule都必须到这里进行注册，否则无效
"""

__author__ = ['"wuyadong" <wuyadong@tigerknows.com>']


spiders = [
    'spiders.com228.spider.Com228Spider',
    'spiders.intro1.spider.Intro1Spider',
    'spiders.ctrip.spider.CtripSpider',
    'spiders.nuomi.spider.NuomiSpider',
    'spiders.lvyoubaidu.spider.LvYouBaiDuSpider',
    'spiders.lvyoubaidutag.spider.LvYouBaiDuTagSpider',
    'spiders.lvyoudaodao.spider.LvYouDaoDaoSpider',
]

schedules = [
    'schedules.schedules.RedisSchedule',
]
