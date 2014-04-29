#!/usr/bin/python
#-*- coding=utf-8 -*-

"""百度旅游的解析类
"""

__author__ = ['"wuyadong" <wuyadong@tigerknows.com>']

import json
from lxml import html
import traceback
from tornado.httpclient import HTTPRequest

from core.spider.parser import BaseParser
from core.datastruct import HttpTask
from core.util import flist

from spiders.lvyoubaidu.items import (AttractionItem,
                                      CommentItem, CommentListItem)
from spiders.lvyoubaidu.utils import (build_scene_url,
                                      build_next_page_request,
                                      build_comment_list_request,
                                      LVYOU_HOST,
                                      EVERY_PAGE_SCENE_COUNT)


class AttractionListParser(BaseParser):
    """用于解析景点列表的解析类
    """

    def __init__(self, namespace):
        BaseParser.__init__(self, namespace)
        self.logger.info("init attraction list parser finished")

    def parse(self, task, input_file):
        """解析函数
            Args:
                task: HttpTask, 请求任务
                input_file: StringIO, 网页StringIO
            Yields:
                task: HttpTask, 任务
                item: Item, 解析结果
        """
        self.logger.debug("start parse attraction list page")
        try:
            json_data = json.load(input_file)
            city_name = json_data['data']['surl']
            current_page = int(json_data['data']['current_page'])
            scene_list = json_data['data']['scene_list']
            total_scene = int(json_data['data']['scene_total'])
            for index, scene in enumerate(scene_list):
                relate_path = scene['surl']
                sid = scene['sid']
                map_info = scene['ext']['map_info']
                seq_sort = \
                    (current_page - 1) * EVERY_PAGE_SCENE_COUNT + index + 1
                # 生成景点request
                http_request = HTTPRequest(build_scene_url(relate_path),
                                           connect_timeout=5, request_timeout=10)
                scene_task = HttpTask(
                    http_request, callback="AttractionParser", max_fail_count=3,
                    cookie_host=LVYOU_HOST, kwargs={"map_info": map_info,
                                                    "seq_sort": seq_sort,
                                                    "sid": sid,
                                                    "relate_path":
                                                        relate_path})
                yield scene_task

            # 生成 下一页任务
            if current_page * EVERY_PAGE_SCENE_COUNT < total_scene:
                # 有下一页, 生成下一个request请求
                next_request = build_next_page_request(
                    city_name, current_page + 1)
                next_page_task = HttpTask(next_request,
                                          callback="AttractionListParser",
                                          max_fail_count=5,
                                          cookie_host=LVYOU_HOST)
                yield next_page_task

        except Exception, e:
            self.logger.info("json dumps error:%s for url:%s" % (e, task.request.url))
            raise e


class AttractionParser(BaseParser):
    """解析景点的解析类
    """
    def __init__(self, namespace):
        BaseParser.__init__(self, namespace)
        self.logger.info("init AttractionParser finished")

    def parse(self, task, input_file):
        """解析函数
            Args:
                task: HTTPTask, 任务
                input_file: StringIO, 网页信息
            Yields:
                task: HTTPTask, 任务
                item: Item, 解析的结果
        """
        self.logger.debug("attraction parser start to parse")
        parser = html.HTMLParser(encoding='utf-8')
        tree = html.parse(input_file, parser)
        try:
            name = flist(tree.xpath("//header[@class='title-head']/a/p/text()"), u"")
            play_spend, play_spend_unit = _extract_play_spend(tree)
            address = flist(tree.xpath("//div[@id='J-aside-info-address']"
                                       "/span[@class='val address-value']"
                                       "/text()"), u"")
            tel_phone = flist(tree.xpath("//div[@id='J-aside-info-phone']"
                                         "/span[@class='val phone-value']"
                                         "/text()"), u"")
            time_elems = tree.xpath("//div[@id='J-aside-info-opening_hours']"
                                    "/div[@class='val opening_hours-value']/p")
            time_list = []
            for time_elem in time_elems:
                time_list.append(time_elem.text)
            open_time = "".join(time_list)
            total_score = flist(tree.xpath("//div[@class='scene-rating']"
                                           "/div/@content"), u"")
            ticket_info = flist(tree.xpath("//div[@id='J-aside-info-price']"
                                           "/div[@class='val price-value']"
                                           "/p/text()"), u"")
            preview = _extract_preview(tree)
            traffic = _extract_traffic(tree)
            tips = _extract_tips(tree)
            hot = flist(tree.xpath("//section[@id='remark-container']"
                                   "/div[@class='remark-overall-rating']"
                                   "/span[@class='remark-all-counts']"
                                   "/text()"), u"")
            lon_lat = task.kwargs['map_info'].split(",")
            if len(lon_lat) <= 1:
                lon, lat = u"", u""
            else:
                lon, lat = lon_lat[0], lon_lat[1]
            seq_sort = task.kwargs['seq_sort']
            sid = task.kwargs['sid']
            attraction_item = AttractionItem(unicode(sid), unicode(name),
                                             unicode(play_spend),
                                             unicode(play_spend_unit),
                                             unicode(address),
                                             unicode(tel_phone),
                                             unicode(open_time),
                                             unicode(total_score),
                                             unicode(ticket_info),
                                             unicode(preview), unicode(hot),
                                             unicode(lon), unicode(lat),
                                             unicode(seq_sort),
                                             unicode(traffic), unicode(tips))
            yield attraction_item

            # yield comment list task
            comments_request = build_comment_list_request(
                sid, task.kwargs['relate_path'])
            comments_task = HttpTask(
                comments_request, callback="CommentListParser",
                max_fail_count=3,
                cookie_host=LVYOU_HOST, kwargs={'sid': sid})
            yield comments_task
        except Exception, e:
            self.logger.error("extract Attraction failed error:%s" % e)
            self.logger.error("error traceback:%s" % traceback.format_exc())
            raise e
        else:
            self.logger.debug("attraction parser end to parse")


def _extract_traffic(tree):
    """用于提取traffic
        Args:
            tree: ElementTree
        Returns:
            traffic: unicode
    """
    elem = flist(tree.xpath("//div[@id='mod-traffic']/"
                            "article[@class='content-article']"), None)
    if elem is None:
        return u""
    else:
        texts = []
        for text_child in elem.itertext():
            texts.append(text_child)
        return u"".join(texts)


def _extract_tips(tree):
    """提取出小提示
        Args:
            tree: ElementTree
        Returns:
            tips: unicode
    """
    elem = flist(tree.xpath("//div[@id='mod-attention']/"
                            "article[@class='content-article']"), None)
    if elem is None:
        return u""
    else:
        texts = []
        for text_child in elem.itertext():
            texts.append(text_child)
        return u"".join(texts)


def _extract_preview(tree):
    """用于提取preview（针对两种类型的网页）
        Args:
            tree: ElementTree
        Returns:
            previe: unicode,
    """
    # 第一类型网页
    preview_elems = tree.xpath("//div[@class='sidebar-mod-inner']/"
                               "article/div[@class='']/p")
    preview_list = []
    for preview_elem in preview_elems:
        preview_list.append(preview_elem.text)
    preview = "".join(preview_list)

    # 第二类型网页
    if len(preview) == 0:
        preview = flist(tree.xpath("//div[@class='view-mod-desc-main']"
                                   "/div[@id='view-mod-abstract']/"
                                   "div[@class='desc-all-holder']"
                                   "/text()"), u"")
    return preview


class CommentListParser(BaseParser):
    """用于解析评价的解析器
    """
    def __init__(self, namespace):
        BaseParser.__init__(self, namespace)
        self.logger.info("init CommentListParser finish")

    def parse(self, task, input_file):
        """解析函数
            Args:
                task: HttpTask, http请求
                input_file: StringIO, 网页文件
            Yields:
                item: CommentListItem
        """
        self.logger.debug("start to parse comment list")
        try:
            json_data = json.load(input_file)
            comment_list = json_data['data']['list']
            comments = []
            for comment in comment_list:
                try:
                    comment_user = comment['user']['nickname']
                    comment_score = comment['score']
                    comment_content = comment['content']
                    comment_time = comment['update_time']
                    comment_item = CommentItem(comment_user, comment_time,
                                               comment_score, comment_content)
                    comments.append(comment_item)
                except Exception, e:
                    self.logger.warn("one comment extract failed error:%s" % e)

            yield CommentListItem(task.kwargs['sid'], comments)
        except Exception, e:
            self.logger.error("load json failed error:%s" % e)
            raise e
        else:
            self.logger.debug("end to parse comment list")


def _extract_play_spend(tree):
    """提取play spend和unit
    """
    play_spend = flist(tree.xpath(
        "//div[@id='J-aside-info-recommend_visit_time']"
        "/span[@class='val recommend_visit_time-value']/text()"), u"")
    if play_spend.find(u"天") != -1:
        play_spend_unit = u"天"
    elif play_spend.find(u"小时") != -1:
        play_spend_unit = u"小时"
    elif play_spend.find(u"分") != -1 or play_spend.find(u"分钟") != -1:
        play_spend_unit = u"分"
    elif len(play_spend.strip()) == 0:
        play_spend_unit = u""
    else:
        play_spend_unit = u""
    replace_dict = {
        u"小时": u"", u"天": u"", u"时": u"", u"小": u"", u"分钟": u"", u"分": u"",
        u"钟": u"",
        u"至": u"-", u"超过": u">", u"半": u".5", u"一": u"1",
        u"二": u"2", u"三": u"3", u"四": u"4", u"五": u"5",
        u"六": u"6", u"七": u"7", u"八": u"8", u"九": u"9",
    }

    for key, value in replace_dict.iteritems():
        play_spend = play_spend.replace(key, value)
    if play_spend.strip() == u".5":
        play_spend = u"0.5"

    return play_spend, play_spend_unit