#!/usr/bin/python2.7
#-*- coding=utf-8 -*-


"""定义的一个基于redis的独享式的可以重复的schedule
"""

__author__ = ['"wuyadong" <wuyadong@tigerknows.com>']

import uuid

from core.schedule import BaseSchedule, ScheduleError
from core.redistools import RedisQueue, RedisSet, RedisError
from core.util import check_http_task_integrity
from core.datastruct import FileTask, HttpTask


class RepeatRedisSchedule(BaseSchedule):
    """PostRedisSchedule是独享式的基于redis生成的schedule
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
        BaseSchedule.__init__(self, interval, max_number)
        self._namespace = str(uuid.uuid4()) if not namespace else namespace
        try:
            self._prepare_to_process_queue = RedisQueue("%s:%s" % (self._namespace, "prepare",),
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

    @property
    def schedule_kwargs(self):
        return self._kwargs

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
                    self._prepare_to_process_queue.push(task)
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
        pass

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
                if task.reason.rfind("unsupported") != -1 or task.reason.rfind("handle error") != -1:
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
            self._processed_queue.clear()
            self._fail_queue.clear()
            self._processed_url_set.clear()
        except RedisError, e:
            raise ScheduleError("redis error:%s" % e)
