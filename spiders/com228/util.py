#!/usr/bin/python
#-*- coding=utf-8 -*-

__author__ = ['"wuyadong" <wuyadong@tigerknows.com>']

_entance_city = {
    u"北京": {
        "code": 110000,
        "abbreviation": 'bj',
    },
    u"上海": {
        "code": 310000,
        "abbreviation": 'sh',
    },
    u"广州": {
        "code": 440100,
        "abbreviation": 'gz',
    },
    u"深圳": {
        "code": 440300,
        "abbreviation": 'sz',
    },
    u"天津": {
        "code": 120000,
        "abbreviation": 'tj',
    },
    u"南京": {
        "code": 320100,
        "abbreviation": 'nj',
    },
    u"成都": {
        "code": 510100,
        "abbreviation": 'cd',
    },
    u"重庆": {
        "code": 500000,
        "abbreviation": 'cq',
    },
    u"郑州": {
        "code": 410100,
        "abbreviation": 'zz',
    },
    u"西安": {
        "code": 610100,
        "abbreviation": 'xa',
    },
    u"武汉": {
        "code": 420100,
        "abbreviation": 'wh',
    },
    u"长沙": {
        "code": 430100,
        "abbreviation": 'cs',
    }
}

_type = {
    u"演唱会": 'yanchanghui',
    u"话剧舞台剧": 'huajuwutaiju',
    u"音乐会": 'yinyuehui',
    u"舞蹈芭蕾": 'wudaobalei',
    u"戏曲综艺": 'xiquzongyi',
    u"体育赛事": 'tiyusaishi',
    u"儿童亲子": 'ertongqinzi',
    u"休闲娱乐": 'xiuxianyule',
}

_c

def create_city_type_task():
    """用于创建入口Task的函数
        Returns:
            tasks: list, [CityTypeTask]
    """