#!/usr/bin/python2.7
#-*- coding=utf-8 -*-

# Copy Rights (c) Beijing TigerKnows Technology Co., Ltd.

"""定义的一个基于redis的独享式的schedule
    RedisSchedule: 基于redis的独享式schedule

"""

__author__ = ['"wuyadong" <wuyadong@tigerknows.com>']

import uuid

from core.schedule import BaseSchedule, ScheduleError
from core.redistools import RedisQueue, RedisSet, RedisError
from core.util import check_http_task_integrity
from core.datastruct import FileTask, HttpTask

class RedisSchedule(BaseSchedule):
    """RedisSchedule是独享式的基于redis生成的schedule
    """
    def __init__(self, namespace=None, host="localhost", port=6379, db=0,
                 interval=30, max_number=15):
        u"""使用redis初始化schedule
            Args:
                interval: str or int ,抓取间隔
                max_number: str or int, 最大并发度
            Raises:
                ScheduleError: 当发生错误的时候
        """
        self._is_stopped = False
        try:
            if isinstance(interval, str):
                interval = int(interval)
            if isinstance(max_number, str):
                max_number = int(max_number)
        except ValueError, e:
            self.logger.error("init redis schedule failed :%s" % e)
            raise ScheduleError("params error:%s" % e)

        self._namespace = str(uuid.uuid4()) if not namespace else namespace
        try:
            self._prepare_to_process_queue = RedisQueue("%s:%s" % (self._namespace, "prepare",),
                                                        host=host, port=port, db=db)
            self._processing_set = RedisSet("%s:%s" % (self._namespace,"processing",),
                                                host=host, port=port, db=db)
            self._processed_queue = RedisQueue("%s:%s" % (self._namespace, "processed",),
                                               host=host, port=port, db=db)
            self._fail_queue = RedisQueue("%s:%s" % (self._namespace, "fail",),
                                          host=host, port=port, db=db)
            self._processed_url_set = RedisSet("%s:%s" % (self._namespace, "urlprocessed"),
                                               host=host, port=port, db=db)
        except RedisError, e:
            self.logger.error("init redis schedule failed error:%s" % e)
            raise ScheduleError("init redis error:%s" % e)

        self._kwargs = {'namespace': self._namespace, "host": host,
                        "port": port, "db": db, "interval":interval,
                        "max_number": max_number,}
        BaseSchedule.__init__(self, interval, max_number)

    @property
    def schedule_kwargs(self):
        return self._kwargs

    def flag_task_processing(self, task):
        """标记某个task正在处理
            Args:
                task:Task, task
        """
        self._processing_set.add(task)

    def remove_processing_task(self, task):
        """移除task正在执行
            Args:
                task:Task, task
        """
        self._processed_url_set.delete(task)

    def pop_task(self):
        """弹出一个待抓取的task
            Returns: task or None

            Raises: ScheduleError 当发生错误的时候
        """
        try:
            if self._prepare_to_process_queue.size() <= 0:
                return None
            else:
                task = self._prepare_to_process_queue.pop()
                return task
        except RedisError, e:
            raise ScheduleError("redis error in schedule:%s" % e)

    def push_new_task(self, task):
        """插入新的一个task
            Args:
                task: Task 新的task

            Raises:
                ScheduleError:当发生错误的时候
        """
        if self._is_stopped:
            return
        try:
            if isinstance(task, HttpTask):
                if check_http_task_integrity(task):
                    url = task.request.url if not isinstance(task.request.url, unicode) \
                        else task.request.url.encode("utf-8")
                    if not self._processed_url_set.exist(url):
                        self._prepare_to_process_queue.push(task)
                    else:
                        self.logger.debug("request haven been done before.")
                else:
                    self.logger.warn("task is not integrate:%s" % task)

            if isinstance(task, FileTask):
                self._prepare_to_process_queue.push(task)

        except RedisError, e:
            raise ScheduleError("redis error in schedule:%s" % e)

    def flag_url_haven_done(self, url):
        """标记一个url已经抓取过
            Args:
                url: str,url

            Raises:
                ScheduleError: 当发生错误的时候
        """
        if self._is_stopped:
            return
        try:
            # convert unicode to str
            if isinstance(url, unicode):
                url = url.encode("utf-8")
            self._processed_url_set.add(url)
        except RedisError, e:
            raise ScheduleError("redis error:%s" % e)

    def handle_error_task(self, task):
        """处理失败的task,
            Args:
                task:Task 失败的task

            Returns:
                is_failed: bool, whether task is push into fail queue

            Raises:
                ScheduleError: 当发生错误的时候

        """
        if self._is_stopped:
            return False

        try:
            if isinstance(task, HttpTask):
                if task.reason.rfind("404") != -1 or task.reason.rfind("unsupported") != 1:
                    self._fail_queue.push(task)
                    return True
                else:
                    task.fail_count += 1
                    if task.fail_count >= task.max_fail_count:
                        self._fail_queue.push(task)
                        return True
                    else:
                        self._prepare_to_process_queue.push(task)
                        return False
            else:
                self._fail_queue.push(task)
                return True
        except RedisError, e:
            raise ScheduleError("fail queue push failed error:%s" % e)


    def fail_task_size(self):
        """get fail task size

            Returns:
                size: int, fail task size
        """
        return self._fail_queue.size()


    #TODO opt ability
    def dumps_all_fail_task(self):
        """dumps all fail task

            Yields:
                task:Task, fail task
        """
        while self._fail_queue.size() > 0:
            fail_task = self._fail_queue.pop()
            if fail_task:
                yield fail_task

    def clear_all(self):
        """清除所有的队列
            Raises:
                ScheduleError: 当发生错误的时候
        """
        self._is_stopped = True
        try:
            self._prepare_to_process_queue.clear()
            self._processing_set.clear()
            self._processed_queue.clear()
            self._fail_queue.clear()
            self._processed_url_set.clear()
        except RedisError, e:
            raise ScheduleError("redis error:%s" % e)
