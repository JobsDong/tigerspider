#!/usr/bin/python
#-*- coding=utf-8 -*-

__author__ = ['"wuyadong" <wuyadong@tigerknows.com>']


from tornado.httpclient import HTTPRequest
from core.datastruct import HttpTask

_entrance_city = {
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

_types = {
    u"演唱会": 'yanchanghui',
    u"话剧舞台剧": 'huajuwutaiju',
    u"音乐会": 'yinyuehui',
    u"舞蹈芭蕾": 'wudaobalei',
    u"戏曲综艺": 'xiquzongyi',
    u"体育赛事": 'tiyusaishi',
    u"儿童亲子": 'ertongqinzi',
    u"休闲娱乐": 'xiuxianyule',
}


def create_City_Type_task(city_name, city_code, abbreviation, _type, tag):
    """根据参数构建CityTypeTask
        Args:
            city_name: str, 城市中文名
            city_code: int, 城市code
            abbreviation: str, 城市拼音缩写
            _type: str, 类型名
            tag: str, 标签
        Returns:
            task: HttpTask, 任务
    """
    url = "http://www.228.com.cn/s/%s-%s/" % (abbreviation, _type)
    cookie_host = "http://www.228.com.cn/%s/" % abbreviation
    http_request = HTTPRequest(url=url, connect_timeout=2, request_timeout=5)
    task = HttpTask(http_request, callback="DealParser", max_fail_count=8,
                    cookie_host=cookie_host, cookie_count=20, kwargs={'city_code': city_code,
                                                                      'city_name': city_name,
                                                                      'tag': tag,
                                                                      'cookie_host': cookie_host,
                                                                      'cookie_count': 20})
    return task


def create_city_type_tasks(city_names=None):
    """用于创建入口Task的函数
        Args:
            city_names: list, 城市中文名的列表
        Returns:
            tasks: list, [CityTypeTask]
    """
    if city_names is None:
        city_names = _entrance_city.keys()

    tasks = []
    for city_name in city_names:
        if city_name in _entrance_city:
            code, abbre = _entrance_city[city_name]['code'], _entrance_city[city_name]['abbreviation']
            for tag, _type in _types.iteritems():
                task = create_City_Type_task(city_name, code, abbre, _type, tag)
                tasks.append(task)

    return tasks