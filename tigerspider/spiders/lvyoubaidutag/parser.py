#!/usr/bin/python
#-*- coding=utf-8 -*-

__author__ = ['"wuyadong" <wuyadong@tigerknows.com>']

import json

from tigerspider.core.spider.parser import BaseParser
from tigerspider.core.datastruct import HttpTask

from tigerspider.spiders.lvyoubaidutag.items import TagItem
from tigerspider.spiders.lvyoubaidutag.utils import (LVYOU_HOST,
                                                     EVERY_PAGE_SCENE_COUNT,
                                                     build_next_tag_page_request)


class TagListParser(BaseParser):
    """用于解析景点的类型
    """

    def __init__(self, namespace):
        BaseParser.__init__(self, namespace)
        self.logger.info("init tagListParser finished")

    def parse(self, task, input_file):
        """解析函数
            Args:
                task: HttpTask, 请求任务
                input_file: StringIO, 网页stringIO
            Yields:
                task: HttpTask, 任务
                item: Item, 解析结果
        """
        self.logger.debug("start parse tag list parser")
        try:
            json_data = json.load(input_file)
            city_name = json_data['data']['surl']
            current_page = int(json_data['data']['current_page'])
            scene_list = json_data['data']['scene_list']
            total_scene = int(json_data['data']['scene_total'])
            current_cid = json_data['data']['current_cid']
            tag = task.kwargs.get('tag', u"")
            for index, scene in enumerate(scene_list):
                sid = scene['sid']
                yield TagItem(tag, current_cid, sid)

            # 生成 下一页任务
            if current_page * EVERY_PAGE_SCENE_COUNT < total_scene:
                # 有下一页, 生成下一个request请求
                next_request = build_next_tag_page_request(current_cid,
                                                           current_page + 1,
                                                           city_name)
                next_tag_task = HttpTask(next_request, callback="TagListParser",
                                         max_fail_count=5,
                                         cookie_host=LVYOU_HOST,
                                         kwargs={'tag': tag})
                yield next_tag_task

        except Exception, e:
            self.logger.info("json loads error:%s for url:%s" %
                             (e, task.request.url))
            raise e
