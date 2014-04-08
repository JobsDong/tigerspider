#!/usr/bin/python2.7
#-*- coding=utf-8 -*-

"""
所有实现的spider和schedule都必须到这里进行注册，否则无效
"""

__author__ = ['"wuyadong" <wuyadong@tigerknows.com>']


spiders = [
    'spiders.com228.spider.Com228Spider',
    'spiders.intro1.spider.Intro1Spider'
]

schedules = [
    'schedules.schedules.RedisSchedule',
]
