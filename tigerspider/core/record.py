#!/usr/bin/python2.7
#-*- coding=utf-8 -*-


"""主要用于记录历史记录，以及还原失败的worker，同时肩负着失败信息的记录(这个后面处理，可能使用到fs)
"""

__authors__ = ['"wuyadong" <wuyadong@tigerknows.com>']

import threading
import json

WORKER_RECORD_PATH = "data/worker_record.dat"

def record(worker_name, start_time, schedule_class_name,
           schedule_kwargs, spider_class_name, spider_kwargs):
    status = {"worker_name": worker_name,
              "start_time": start_time,
              "schedule_class": schedule_class_name,
              "schedule_kwargs": schedule_kwargs,
              "spider_class": spider_class_name,
              "spider_kwargs": spider_kwargs,}
    return status

class RecorderManager(object):
    """专门用于记录，以及持久化，还原等操作的记录器
    """
    _lock = threading.Lock()

    def __init__(self, record_path = WORKER_RECORD_PATH):
        """初始化记录器
            Args:
                record_path: 记录文件的路径
        """
        self._record_path = record_path
        self._last_fail_workers = {}
        self._now_workers = {}
        self.loads()

    @staticmethod
    def instance():
        """生成一个记录器
            单例模式
            Returns:
                instance: Recorder, Recoder的一个实例
        """
        if not hasattr(RecorderManager, "_instance"):
            with RecorderManager._lock:
                setattr(RecorderManager, "_instance", RecorderManager())
        return getattr(RecorderManager, "_instance")

    def record_doing(self, record):
        """记录worker的情况，注意这些情况，必须保证能够恢复
        """
        self._now_workers[record.get('worker_name')] = record
        self.dumps()

    def record_done(self, worker_name):
        """标记worker正确完成了
        """
        if self._now_workers.has_key(worker_name):
            self._now_workers.pop(worker_name)
            self.dumps()

    def get_fail_worker_record(self, worker_name):
        if self._last_fail_workers.has_key(worker_name):
            return self._last_fail_workers.get(worker_name)
        else:
            return None

    def dumps(self):
        """持久化worker数据
        """
        import tigerspider.core.util
        with open(tigerspider.core.util.get_project_path() + WORKER_RECORD_PATH, "wb") as out_file:
            new_dict = {}
            new_dict.update(self._last_fail_workers)
            new_dict.update(self._now_workers)
            out_file.write(json.dumps(new_dict))

    def loads(self):
        """加载worker数据
        """
        import tigerspider.core.util
        records = {}
        try:
            with open(tigerspider.core.util.get_project_path() + WORKER_RECORD_PATH, "rb") as in_file:
                records_str = in_file.read()
                records.update(json.loads(records_str))
        except Exception:
            pass
        finally:
            self._last_fail_workers = records

    def remove_last_fail_worker(self, worker_name):
        """去除上一次错误的worker
        """
        if self._last_fail_workers.has_key(worker_name):
            self._last_fail_workers.pop(worker_name)
            self.dumps()

    def get_last_fail_worker(self):
        """获得上一次失败的worker的状态
        """
        return self._last_fail_workers.values()
