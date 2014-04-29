#!/usr/bin/python
#-*- coding=utf-8 -*-

__author__ = ['"wuyadong" <wuyadong@tigerknows.com>']

import traceback
from StringIO import StringIO
import re
from lxml import html
from core.datastruct import HttpTask
from core.spider.parser import BaseParser
from core.util import flist

from spiders.lvyoudaodao.utils import (build_attraction_request,
                                       LVYOU_HOST,
                                       build_next_page_request,
                                       build_description_request)
from spiders.lvyoudaodao.items import (AttractionItem,
                                       DescriptionItem,
                                       CommentItem)


class AttractionListParser(BaseParser):
    """用于解析Attraction list的解析器
    """
    def __init__(self, namespace):
        BaseParser.__init__(self, namespace)
        self.logger.info("init attraction list parser finish")

    def parse(self, task, input_file):
        """解析函数
            Args:
                task: HttpTask，任务
                input_file: StringIO, 网页文件
            Yields:
                task: HttpTask, 新任务
        """
        tree = html.parse(input_file)
        attraction_elems = tree.xpath("//div[@id='ATTRACTION_OVERVIEW']"
                                      "/div[@class='attraction-list clearfix']")
        for attraction_elem in attraction_elems:
            try:
                info_elem = flist(attraction_elem.xpath(
                    "div[@class='clearfix']/div[@class='info']"), None)
                rank_elem = flist(attraction_elem.xpath(
                    "div[@class='clearfix']/div[@class='rank']"), None)
                relate_path = flist(info_elem.xpath(
                    "div[@class='title']/a/@href"), u"")
                name = flist(info_elem.xpath(
                    "div[@class='title']/a/text()"), u"")
                address = _extract_address(info_elem)
                hot = flist(rank_elem.xpath("a/strong/text()"), u"")
                rank = flist(rank_elem.xpath("span[1]/strong/text()"), u"")
                # 形成attraction 任务
                http_request = build_attraction_request(relate_path)
                attraction_task = HttpTask(
                    http_request, callback="AttractionParser", max_fail_count=3,
                    cookie_host=LVYOU_HOST, kwargs={"name": unicode(name).strip(),
                                                    "address": unicode(
                                                        address),
                                                    "hot": unicode(hot),
                                                    "rank": unicode(rank)})
                yield attraction_task
            except Exception, e:
                self.logger.warn("extract one attraction failed error:%s" % e)
        # 形成下一页任务
        next_page_relate = flist(tree.xpath(
            "//div[@class='pagination']/div"
            "/a[@class='next sprite-arrow-right-green ml6 ']/@href"), u"")
        if len(next_page_relate) != 0:
            next_page_request = build_next_page_request(next_page_relate)
            next_page_task = HttpTask(next_page_request,
                                      callback="AttractionListParser",
                                      max_fail_count=5, cookie_host=LVYOU_HOST)
            yield next_page_task


def _extract_address(info_elem):
    """解析地址
        Args:
            info_elem: Element
        Returns:
            address: unicode, 地址信息
    """
    country = flist(info_elem.xpath("address/span[@class='country-name']/text()"), u"")
    city = flist(info_elem.xpath("address/span[@class='locality']/text()"), u"")
    streat_script = flist(info_elem.xpath("address/span/script/text()"), u"")
    streat = _extract_script_text(streat_script)

    return u"%s%s%s" % (country, city, streat)


def _extract_script_text(script_text):
    """解析js脚本,获得街道信息
        Args:
            script_text
        Returns:
            streat_text
    """
    temp_texts = []
    # a
    re_a = re.compile(r"a='[\\\s\w]*'")
    a_eqs = re_a.findall(script_text)[0]
    a_eq = a_eqs.replace(u"a=", u"").replace(u"'", u"")
    a_eq_unicode = a_eq.decode(encoding="unicode-escape")
    temp_texts.append(a_eq_unicode)

    # a+=
    re_a_plus = re.compile(r"a\+='[\\\s\w]*'")
    a_eq_pluss = re_a_plus.findall(script_text)[0]
    a_eq_plus = a_eq_pluss.replace(u"a+=", u"").replace(u"'", u"")
    a_eq_plus_unicode = a_eq_plus.decode(encoding="unicode-escape")
    temp_texts.append(a_eq_plus_unicode)

    # c
    re_c = re.compile(r"c='[\\\s\w]*'")
    c_eqs = re_c.findall(script_text)[0]
    c_eq = c_eqs.replace(u"c=", u"").replace(u"'", u"")
    c_eq_unicode = c_eq.decode(encoding="unicode-escape")
    temp_texts.append(c_eq_unicode)

    # b
    re_b = re.compile(r"b='[\\\s\w]*'")
    b_eqs = re_b.findall(script_text)[0]
    b_eq = b_eqs.replace(u"b=", u"").replace(u"'", u"")
    b_eq_unicode = b_eq.decode(encoding="unicode-escape")
    temp_texts.append(b_eq_unicode)

    # b+=
    re_b_plus = re.compile(r"b\+='[\\\s\w]*'")
    b_eq_pluss = re_b_plus.findall(script_text)[0]
    b_eq_plus = b_eq_pluss.replace(u"b+=", u"").replace(u"'", u"")
    b_eq_plus_unicode = b_eq_plus.decode(encoding="unicode-escape")
    temp_texts.append(b_eq_plus_unicode)

    return u"".join(temp_texts)


class AttractionParser(BaseParser):
    """用于解析景点页的解析器
    """
    def __init__(self, namespace):
        BaseParser.__init__(self, namespace)
        self.logger.info("init attraction parser finish")

    def parse(self, task, input_file):
        """解析函数
            Args:
                task: HttpTask，任务
                input_file: StringIO, 网页文件
            Yields:
                item
        """
        self.logger.debug("attraction parser start to parse")
        content = input_file.read()
        tree = html.parse(StringIO(content))
        try:
            zip_code = flist(tree.xpath("//span[@class='postal-code']/text()"), u"")
            play_spend, play_spend_unit = _extract_play_spend_and_unit(content)
            tel_phone = flist(tree.xpath("//div[@id='HEADING_GROUP']"
                                         "/div[@class='wrap infoBox']"
                                         "/div[@class='odcHotel blDetails']"
                                         "/div/div[@class='fl']/text()"), u"")
            open_time = u""
            total_score = flist(tree.xpath("//div[@class='rs rating']"
                                           "/span/img/@content"))
            ticket_info = u""
            preview_relate_path = flist(tree.xpath(
                "//div[@class='listing_description']/a/@href"), u"")
            lon, lat = _extract_lon_lat(flist(tree.xpath(
                "//div[@class='js_mapThumb']"
                "/div[@id='bmapContainer']/img[1]/@src"), u""))
            comments = _extract_comments(tree)
            # 生成景点信息(不包括description)
            attraction_item = AttractionItem(task.request.url,
                                             task.kwargs['name'],
                                             unicode(play_spend),
                                             play_spend_unit,
                                             task.kwargs['address'],
                                             unicode(tel_phone), unicode(open_time),
                                             unicode(total_score),
                                             unicode(ticket_info),
                                             task.kwargs['hot'],
                                             lon, lat, task.kwargs['rank'],
                                             comments,
                                             unicode(zip_code))
            yield attraction_item

            # 生成description任务
            if len(preview_relate_path) != 0:
                description_request = build_description_request(
                    task.request.url, preview_relate_path)
                description_task = HttpTask(description_request,
                                            callback="DescriptionParser",
                                            max_fail_count=3,
                                            cookie_host=LVYOU_HOST,
                                            kwargs={'url': task.request.url})
                yield description_task
            else:
                yield DescriptionItem(task.request.url, u"")

        except Exception, e:
            print "error:%s" % e
            print traceback.format_exc()

        self.logger.debug("attraction parser end to parse")


def _extract_play_spend_and_unit(text):
    re_1 = re.compile(r"建议的造访时间:</b>[^/]*</div>")
    he_1 = re_1.findall(text)
    if len(he_1) > 0:
        start_dot = he_1[0].index("</b>")
        end_dot = he_1[0].index("</div>")
        spend_str = he_1[0][start_dot + len("</b>"): end_dot]
        spend_str = spend_str.decode('utf-8') if isinstance(spend_str, str) \
            else spend_str
    else:
        re_2 = re.compile(r"建议的造访时间:[^/]*</div>")
        he_2 = re_2.findall(text)
        if len(he_2) > 0:
            start_dot = he_2[0].index("建议的造访时间:")
            end_dot = he_2[0].index("</div>")
            spend_str = he_2[0][start_dot + len("建议的造访时间:"): end_dot]
            spend_str = spend_str.decode('utf-8') if isinstance(spend_str, str) \
                else spend_str
        else:
            spend_str = u""

    return _handle_unit_and_time(spend_str)


def _handle_unit_and_time(play_spend):
    """提取play spend和unit
    """
    if play_spend.find(u"天") != -1:
        play_spend_unit = u"天"
    elif play_spend.find(u"小时") != -1:
        play_spend_unit = u"小时"
    elif play_spend.find(u"分") != -1:
        play_spend_unit = u"分"
    elif len(play_spend.strip()) == 0:
        play_spend_unit = u""
    else:
        play_spend_unit = u""
    replace_dict = {
        u"小时": u"", u"天": u"", u"分钟": u"", u"时": u"", u"小": u"",
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


def _extract_comments(tree):
    """解析出评论
        Args:
            tree: ElementTree
        Returns:
            comments: list
    """
    comment_elems = tree.xpath("//div[@id='REVIEWS']/div[@class='reviewSelector']")
    comments = []
    for comment_elem in comment_elems:
        try:
            # 第一类型网页
            comment_user = flist(comment_elem.xpath(
                "div/div[@class='col1of2']"
                "//div[@class='username mo']/span/text()"), u"")
            comment_score = flist(comment_elem.xpath(
                "div/div[@class='col2of2 ']"
                "/div[@class='rating reviewItemInline']"
                "/span[@class='rate rate_s s50']/img/@content"), u"")
            comment_time = flist(comment_elem.xpath(
                "div/div[@class='col2of2 ']"
                "/div[@class='rating reviewItemInline']"
                "/span[@class='ratingDate']/text()"), u"")
            content_elems = comment_elem.xpath(
                "div/div[@class='col2of2 ']/div[@class='entry']/p")
            texts = []
            for content_elem in content_elems:
                if content_elem.text is not None:
                    texts.append(content_elem.text)
            comment_content = u"".join(texts).strip()

            # 第二类型网页
            if len(comment_user.strip()) == 0:
                comment_user = flist(comment_elem.xpath(
                    "div/div[@class='col1of2']"
                    "//div[@class='username']/span/text()"), u"")
            if len(comment_time.strip()) == 0:
                comment_time = flist(comment_elem.xpath(
                    "div/div[@class='col2of2']"
                    "/span[@class='ratingDate']/text()"), u"")
            if len(comment_content.strip()) == 0:
                content_elems = comment_elem.xpath(
                    "div/div[@class='col2of2']"
                    "/div[@class='entry']/p")
                texts = []
                for content_elem in content_elems:
                    if content_elem.text is not None:
                        texts.append(content_elem.text)
                comment_content = u"".join(texts).strip()

        except Exception, e:
            print "extract one comment failed error:%s" % e
            print traceback.format_exc()
        else:
            if len(unicode(comment_content)) != 0:
                comment_item = CommentItem(unicode(comment_user).strip(),
                                           unicode(comment_time).strip(),
                                           unicode(comment_score).strip(),
                                           unicode(comment_content).strip())
                comments.append(comment_item)
    return comments[0:10]


def _extract_lon_lat(img_src):
    """从url提取出lon，lat
        Args:
            img_src: unicode, img src url
        Returns:
            lon, lat: tuple, lon lat
    """
    try:
        dot_start = img_src.index("?center=")
        dot_end = img_src.index("&zoom=")
        lon_lat = img_src[dot_start + 8: dot_end]
        lon, lat = lon_lat.split(",")
    except ValueError:
        lon, lat = u"", u""
    return lon, lat


class DescriptionParser(BaseParser):
    """用于解析介绍详情页
    """
    def __init__(self, namespace):
        BaseParser.__init__(self, namespace)
        self.logger.info("init description parser finish")

    def parse(self, task, input_file):
        """解析函数
        """
        self.logger.debug("description parser start to parse")
        tree = html.parse(input_file)
        description = _extract_description(tree)
        # 生成description item
        description_item = DescriptionItem(task.kwargs['url'], description)
        yield description_item
        self.logger.debug("description parser end to parse")


def _extract_description(tree):
    """提取出描述
        Args:
            tree: ElementTree
        Returns:
            desc: unicode
    """
    elements = tree.xpath("//div[@id='ARTICLE']//div[@class='articleBody']")
    texts = []
    for elem in elements:
        for text in elem.itertext():
            texts.append(text)
    return u"".join(texts).strip()