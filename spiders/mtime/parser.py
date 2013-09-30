#!/usr/bin/python2.7
#-*- coding=utf-8 -*-

# Copy Rights (c) Beijing TigerKnows Technology Co., Ltd.

"""针对mtime的解析模块
    RealInfoParser: 用于解析影讯信息的类
"""

__authors__ = ['"wuyadong" <wuyadong@tigerknows.com>']

from lxml import html
import StringIO
import datetime
from tornado.httpclient import HTTPRequest
import urllib

from core.spider.parser import BaseParser, ParserError
from core.util import remove_white
from core.datastruct import HttpTask

from spiders.mtime.items import RealInfoItem, MovieInfoItem

class RealInfoParser(BaseParser):
    """用于解析影片资讯信息的类
    """

    def __init__(self, namespace):
        BaseParser.__init__(self, namespace)
        self.logger.debug("init RealInfoParser")


    def parse(self, task, input_file):
        """解析函数，
            Args:
                task:Task, 任务描述
                input_file: File, 文件对象
            Yields:
                ...
                ...
        """
        cinema_id = task.kwargs.get('cinemaid')
        district_str = task.kwargs.get('district')
        request_url = task.kwargs.get('requesturl')
        if task.request.url.startswith("http://service"):
            content = input_file.read()
            content = content.replace("\\\"", "\"")
            tree = html.parse(StringIO.StringIO(content))
        else:
            tree = html.parse(input_file)

        day_elems = tree.xpath("//div[@id='fixel']//ul//li")
        if len(day_elems) >= 2:
            new_url = day_elems[1].xpath("a/@href")
            new_url = new_url[0] if len(new_url) > 0 else new_url
            if new_url != task.request.url:
                date = _filter_date_from_url(new_url)
                headers = {'Accept-Language': r'en-US,en;q=0.5','Accept': r'*/*'}
                http_request = HTTPRequest(_build_ajax_url(cinema_id, district_str, date, new_url),
                                           connect_timeout=10, request_timeout=20, headers=headers)
                new_task = HttpTask(http_request, callback='JSParser', max_fail_count=4, proxy_need=True,
                            kwargs={'citycode':task.kwargs.get('citycode'),
                                    'cinemaid':cinema_id,
                                    'district': task.kwargs.get('district'),
                                    'requesturl': task.kwargs.get('requesturl')})
                yield new_task

        fruits = tree.xpath("//dl[@class='s_cinamelist']/node()")
        for fruit in fruits:
            if fruit.tag == "a":
                movie_id = fruit.attrib['name']
            if fruit.tag == "dd":
                movie_running_time = fruit.xpath("div//span[@class='fr mt6']/text()")
                movie_running_time = remove_white(movie_running_time[0])\
                    .replace(u"片长", "").replace(u"分钟", "") \
                    if len(movie_running_time) > 0 else ""
                movie_language = fruit.xpath("div//span[@language]/a/text()")
                movie_language = movie_language[0] if len(movie_language) > 0 else ""
                movie_version = fruit.xpath("div//span[@version and @method='versionfilter']/a/text()")
                movie_version = movie_version[0] if len(movie_version) > 0 else ""
                movie_tag = ""
                movie_info_item = MovieInfoItem(_build_shop_url(movie_id))
                yield movie_info_item

                show_infos = fruit.xpath("div//li[@showtimeid]")

                for show_info in show_infos:
                    show_id = show_info.attrib['showtimeid']
                    show_price = show_info.xpath("a/em/text()")
                    show_price = show_price[0] if len(show_price) > 0 else ""
                    show_start_time = show_info.attrib['time'].replace("/", "-")
                    show_url = _build_show_url(request_url, movie_id, show_id)

                    real_info_item = RealInfoItem(
                        show_id, movie_id, cinema_id, movie_tag, show_price, movie_version,
                        movie_language, movie_running_time,
                        show_url, task.kwargs['citycode'], show_start_time)
                    yield real_info_item

class JSParser(BaseParser):
    """用于解析javasricpt的parser

    """
    def __init__(self, namespace):
        BaseParser.__init__(self, namespace)
        self.logger.debug("init JSParser success")


    def parse(self, task, input_file):
        """解析函数

            Args:
                task:Task, 任务描述
                input_file:File, 文件对象
            Yields:
                item: RealInfoItem, 结果

        """
        cinema_id = task.kwargs.get('cinemaid')
        request_url = task.kwargs.get('requesturl')

        content = input_file.read()
        if isinstance(content, str):
            content = unicode(content, encoding="utf-8")
        content = content.replace(ur'\"', ur'"')
        tree = html.parse(StringIO.StringIO(content))
        fruits = tree.xpath("//dl[@class='s_cinamelist']/node()")

        if len(fruits) <= 0 and content.rfind(u"showtimeList") == -1:
            self.logger.error("WARN: %s %s" % (task.request.url, content))
            raise ParserError("not exists showtimelist")

        for fruit in fruits:
            if fruit.tag == "a":
                movie_id = fruit.attrib['name']
            if fruit.tag == "dd":
                movie_running_time = fruit.xpath("div//span[@class='fr mt6']/text()")
                movie_running_time = movie_running_time[0] if len(movie_running_time) > 0 else ""

                movie_running_time = remove_white(movie_running_time)\
                    .replace(u"片长", "").replace(u"分钟", "")
                movie_language = fruit.xpath("div//span[@language]/a/text()")

                movie_language = movie_language[0] if len(movie_language) > 0 else ""

                movie_version = fruit.xpath("div//span[@version and @method='versionfilter']/a/text()")
                movie_version = movie_version[0] if len(movie_version) > 0 else ""
                movie_tag = ""
                movie_info_item = MovieInfoItem(_build_shop_url(movie_id))
                yield movie_info_item

                show_infos = fruit.xpath("div//li[@showtimeid]")
                for show_info in show_infos:
                    show_id = show_info.attrib['showtimeid']
                    show_price = show_info.xpath("a/em/text()")

                    show_price = show_price[0] if len(show_price) > 0 else ""
                    show_start_time = show_info.attrib['time'].replace("/", "-")
                    show_url = _build_show_url(request_url, movie_id, show_id)

                    real_info_item = RealInfoItem(
                        show_id, movie_id, cinema_id, movie_tag, show_price, movie_version,
                        movie_language, movie_running_time,
                        show_url, task.kwargs['citycode'], show_start_time)

                    yield real_info_item

def _build_shop_url(movie_id):
    """build movie url
        Args:
            movie_id: str, movie id
        Returns:
            shopurl: str, shop url
    """
    return "%s/%s/" % ("http://movie.mtime.com", movie_id)


def _build_show_url(url, movie_id, show_id):
    """build show url

        Args:
            url: str, Url
            movie_id: str, movie id
            show_id: str, show_id
        Returns:
            show_url: str, show url

    """
    return "%sshowtime.html?m=%s&s=%s" % (url, movie_id, show_id)

def _filter_date_from_url(url):
    """filter date from url

        Args;
            url: str, url
        Returns:
            date: str, date string
    """
    try:
        dot = url.rindex("d=")
    except ValueError:
        pass
    else:
        date = url[dot+2:]
        return "%s-%s-%s 00:00" % (date[0:4], date[4:6], date[6:8])


def _build_ajax_url(cinema_id, path, date, request_url):
    """build ajax url

        Args:
            cinema_id: str, cinema id
            path: str, district
            date: str, date string
            request_url: str, url
        Returns:
            ajax_url: str, ajax url

    """
    now = datetime.datetime.now()
    param_str = urllib.urlencode({'Ajax_CallBack': 'true', 'Ajax_CallBackArgument0': 1,
                      'Ajax_CallBackArgument1': cinema_id, 'Ajax_CallBackArgument10': 1,
                      'Ajax_CallBackArgument2': path, 'Ajax_CallBackArgument3': '',
                      'Ajax_CallBackArgument4': 0, 'Ajax_CallBackArgument5': date,
                      'Ajax_CallBackArgument6': 8, 'Ajax_CallBackArgument7':0,
                      'Ajax_CallBackArgument8': 31, 'Ajax_CallBackArgument9':59,
                      'Ajax_CallBackMethod': 'GetTheaterDateShowtimes',
                      'Ajax_CallBackType': 'Mtime.Showtime.Pages.ShowtimeService',
                      'Ajax_CrossDomain': 1, 'Ajax_RequestUrl': request_url,
                      't': "%s%s%s%s%s%s" %
                           (now.year, now.month, now.day, now.hour, now.minute, now.microsecond)
                      })
    return "http://service.theater.mtime.com/service/showtime.ms?" + param_str
