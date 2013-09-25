#!/usr/bin/python
# -*- coding: utf-8 -*-

"""定义了baiduoffset中的所有解析的類
    OffsetParser: 解析城市列表的類
    WebParser: 解析網頁的類
"""
import json
import csv
from base64 import decodestring
import urlparse
from tornado.httpclient import HTTPRequest

from core.spider.parser import BaseParser
from core.datastruct import Task
from spiders.baiduoffset.items import CityItem
from spiders.baiduoffset.util import build_url
from spiders.baiduoffset.items import CoordItem

eps = 0.001


class OffsetParser(BaseParser):
    """发起offset任务
    """

    def __init__(self, namespace):
        BaseParser.__init__(self, namespace)
        self.logger.debug("init baiduoffset.OffsetParser")

    def parse(self, task, response):
        """读取文件，发起offset任务
            Args:
                task: Task, 任務描述
                response: HttpResponse, 網頁結果
        """
        self.logger.debug("OffsetParser start")
        try:
            file = csv.reader(open('./newkey.csv'))
            #print 'csv read'
            for line in file:
                #xylist = line[:-1].split(',')
                (x, y) = (float(line[0]), float(line[1]))
                print 'key', int(x), int(y)
                city_item = CityItem(int(x), int(y))
                yield city_item

                y = y + eps
                if y-int(city_item.y) >= 1.0:
                    x += eps
                    y = int(city_item.y)
                if x-int(city_item.x) < 1.0:
                    xstr, ystr = build_xystr(x, y)
                    http_request = HTTPRequest(url=build_url(xstr, ystr),
                                               connect_timeout=5,
                                               request_timeout=10)
                    new_task = Task(http_request, callback='CoordParser',
                                    kwargs={'xstr': xstr,
                                            'ystr': ystr,
                                            'key': city_item.key})
                    yield new_task
        except Exception, e:
            self.logger.error("city parse extract error:%s " % e)
        finally:
            self.logger.debug("city parse end to parse")


def build_xystr(x, y):
    xstr = str(x)
    ystr = str(y)
    for i in range(19):
        y += eps
        if y % 1 == 0.0:
            break
        xstr = xstr + ',' + str(x)
        ystr = ystr + ',' + str(y)
    return xstr, ystr


def replace_url_path(url, path):
    """将某个url中的路径进行修改
        Args:
            url: str, url
            path: str，目标路径
        Returns:
            url: str, 新的url
    """
    schema, host, _, _, _ = urlparse.urlsplit(url)
    return urlparse.urlunsplit((schema, host, path, "", ""))


class CoordParser(BaseParser):
    """用于解析小区信息"""
    def parse(self, task, response):
        """解析函数
            task:Task, 任务描述
            response:HTTPResponse, 下载的结果
        """
        orig_x = task.kwargs['xstr'].split(',')
        orig_y = task.kwargs['ystr'].split(',')
        key = task.kwargs['key']
        city_x, city_y = key.split('_')
        city_x = float(city_x)
        city_y = float(city_y)
        try:
            coordlist = json.loads(response.body)
            count = -1
            x = []
            y = []
            for elem in coordlist:
                if elem['error'] == 0:
                    count += 1
                    x.append(decodestring(elem['x']))
                    y.append(decodestring(elem['y']))
                else:
                    self.logger.error("orig_x: %s, orig_y: %s, elem: %s" %
                                      (orig_x[count], orig_y[count], elem))
            yield CoordItem(x, y, orig_x, orig_y, key)
        except:
            self.logger.error("json loads error xstr %s" % task.kwargs['xstr'])
            self.logger.error("json loads error ystr %s" % task.kwargs['ystr'])
            self.logger.error("json loads error body %s" % response.body)
        #print 'new task',
        fx = float(orig_x[-1])
        fy = float(orig_y[-1]) + eps
        if fy-city_y >= 1.0:
            fx += eps
            fy = city_y
            #print fx, fy
        xstr, ystr = build_xystr(fx, fy)

        if fx-city_x < 1.0:
            http_request = HTTPRequest(
                url=build_url(xstr, ystr),
                connect_timeout=5,
                request_timeout=10)
            new_task = Task(http_request,
                            callback='CoordParser',
                            kwargs={'xstr': xstr,
                                    'ystr': ystr,
                                    'key':  key})
            yield new_task
