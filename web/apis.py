#!/usr/bin/python2.7
#-*- coding=utf-8 -*-

# Copy Rights (c) Beijing TigerKnows Technology Co., Ltd.

""" 提供web对worker进行控制的api接口
    api_route：是一个用于api注册的包装器

    check_params: 检查参数
    result: 统一返回结果
    api_dummy: 返回参数
    api_get_all_schedule_class: 返回所有注册的schedule类
    api_get_all_spider_class: 返回所有注册的spider类
    api_start_worker: 启动一个worker
    api_stop_worker: 停止一个worker
    api_suspend_worker: 暂停一个worker
    api_rouse_worker: 唤醒一个worker
    api_get_worker_statistic: 返回worker对应的统计信息
    api_get_all_worker: 返回所有的worker
    api_recover_worker: 以恢复模式启动worker
"""

__author__ = ['"wuyadong" <wuyadong@tigerknows.com>']

import json

from core.spider.spider import get_all_spider_class, get_spider_class, SpiderError
from core.schedule import get_all_schedule_class, get_schedule_class, ScheduleError
from core.worker import (start_worker, stop_worker, suspend_worker, WorkerError,rouse_worker,
                         get_worker_statistic, get_all_workers, recover_worker)
from core.statistic import output_statistic_dict
from core.record import RecorderManager


class api_route(object):
    """api的包装器

        Attributes:
            _api_methods: 字典，key是路径名，value是函数对象

    """
    _api_methods = {}

    def __init__(self, uri):
        """根据路径进行注册
            uri: 路径
        """
        self._uri = uri

    def __call__(self, api_method):
        self._api_methods[self._uri] = api_method

    @classmethod
    def get_api_routes(cls):
        """获取注册的所有函数

            不允许对返回的结果进行修改

            Returns:
                routes: 字典，key是路径，value是函数对象

        """
        return cls._api_methods

def not_found(path):
    """返回notfound结果
        Args:
            path: str, 表示路径
        Returns:
            result:Result
    """
    return result(code=404, message="not found", result={"path": path})

def not_support_get(path):
    """返回不支持结果
        Args:
            path: str, 表示路径
        Returns:
            result:Result
    """
    return result(code=404, message="not support get", result={"path": path})

def check_params(params, *args):
    """检查参数params是否含有需要的key

        Args:
            params: 参数字典
            args: 所需要的参数名

        Returns:
            result: 二元组,第一个参数是boolean，第二个是错误的列表

    """
    errors = []
    for arg in args:
        if arg not in params.keys():
            errors.append("lack of %s" % arg)
    if len(errors) > 0:
        return False, errors
    else:
        return True, errors

def result(code=200, message="success", result=""):
    """将计算的结果组织成json格式
        Args:
            code: int, 错误码
            message: str, 信息
            result: str, 结果

        Returns:
            encoded_result: str, 被jsondump后的数据
    """
    encoded_result = json.dumps({"code": code, "message": message, "result": result},
                                ensure_ascii=False, encoding="utf8")
    return encoded_result

@api_route(r"/api/dummy")
def api_dummy(params):
    return result(200, "success", params)

@api_route(r"/api/get_all_schedule_class")
def api_get_all_schedule_class(params):
    schedule_classes_str = json.dumps(get_all_schedule_class(),
                                      ensure_ascii=False, encoding="utf-8")
    return result(200, "success", schedule_classes_str)

@api_route(r"/api/get_all_spider_class")
def api_get_all_spider_class(params):
    spider_classes_str = json.dumps(get_all_spider_class(),
                                    ensure_ascii=False, encoding="utf-8")
    return result(200, "success", spider_classes_str)

@api_route(r"/api/start_worker")
def api_start_worker(params):
    '''
    启动一个worker，worker执行的内容spider，以及执行的规则
    schedule_path;
    spider_path,
    spider_..,...,...., 这里为已spider_开头的参数
    schedule_..,...,...,这里为以schedule_开头的参数
    '''
    is_ok, errors = check_params(params, 'schedule_path', 'spider_path')
    if not is_ok:
        return result(400, "params error", str(errors))
    else:
        try:
            schedule_path = params.pop('schedule_path')
            spider_path = params.pop('spider_path')
            schedule_params = dict([(key[9:], value) for key, value in params.items()
                               if key.startswith('schedule_')])
            spider_params = dict([(key[8:], value) for key, value in params.items()
                             if key.startswith('spider_')])
            schedule = get_schedule_class(schedule_path)(**schedule_params)
            spider = get_spider_class(spider_path)(schedule, **spider_params)
            start_worker(spider)
        except ScheduleError, e:
            return result(400, message="init schedule failed", result=str(e))
        except SpiderError, e:
            return result(400, message="init spider failed", result=str(e))
        except WorkerError, e:
            return result(400, message="start worker failed", result=str(e))
        except Exception, e:
            return result(500, "unsupported exception", result=str(e))
        else:
            return result(200, "start worker success", "success")

@api_route(r"/api/stop_worker")
def api_stop_worker(params):
    '''
    worker_name:${worker_name}
    这个会停止worker，并且将worker对应的schedule清空，并存储统计信息
    '''
    is_ok, errors = check_params(params, 'worker_name')
    if not is_ok:
        return result(400, "params error", str(errors))
    else:
        try:
            worker_name = params['worker_name']
            stop_worker(worker_name)
        except WorkerError, e:
            return result(400, "stop worker failed", str(e))
        else:
            return result(200, "stop worker success", "success")

@api_route(r"/api/suspend_worker")
def api_suspend_worker(params):
    """挂起一个worker

        Args:
            params: 字典，参数字典，必须包含如下数据：
                worker_name:worker的名字

        Returns:
            result: 被jsondumps后的字符串，描述的是执行的结果

    """
    is_ok, errors = check_params(params, 'worker_name')
    if not is_ok:
        return result(400, "params error", str(errors))

    worker_name = params['worker_name']
    try:
        suspend_worker(worker_name)
    except WorkerError, e:
        return result(400, "suspend worker failed", str(e))
    else:
        return result(200, "suspend worker success", "success")

@api_route(r"/api/rouse_worker")
def api_rouse_worker(params):
    """唤醒worker
        Args:
            params: 字典，参数字典，必须包含如下字段：
                worker_name: worker的名字

    """
    is_ok, errors = check_params(params, 'worker_name')
    if not is_ok:
        return result(400, "params error", str(errors))

    worker_name = params['worker_name']
    try:
        rouse_worker(worker_name)
    except WorkerError, e:
        return result(400, "rouse worker failed", str(e))
    else:
        return result(200, "rouse worker success", "success")

@api_route(r"/api/get_worker_statistic")
def api_get_worker_statistic(params):
    """获取某一个worker的实时统计信息
        Args:
            params: 字典，参数字典，必须包含如下信息：
                worker_name: worker的名字

    """

    is_ok, errors = check_params(params, 'worker_name')
    if not is_ok:
        return result(400, "params error", str(errors))

    worker_name = params['worker_name']
    try:
        worker_statistic = get_worker_statistic(worker_name)
    except WorkerError, e:
        return result(400, "get worker data failed", str(e))
    try:
        worker_statistic_dict = output_statistic_dict(worker_statistic)
    except Exception, e:
        return result(500, "get worker data failed",
                      "format worker_statistic failed:%s" % e)

    return result(200, "success", str(worker_statistic_dict))

@api_route(r"/api/get_all_worker")
def api_get_all_worker(params):
    """获取所有的worker
        Args:
            params: 字典，参数字典，不包含任何数据
    """
    workers = get_all_workers()

    return result(200, "success", str(workers))

@api_route(r"/api/get_all_fail_worker")
def api_get_all_fail_worker(params):
    """获取以前失败的worker
        Args:
            params: 字典,参数字典
        Returns:
            result: str，结果
    """
    try:
        fail_worker_records = RecorderManager.instance().get_last_fail_worker()
        last_fail_worker_str = json.dumps(fail_worker_records,
                                      ensure_ascii=False, encoding="utf-8")
    except Exception, e:
        return result(500, "get fail worker failed", str(e))
    else:
        return result(200, "success", last_fail_worker_str)

@api_route(r"/api/recover_worker")
def api_recover_worker(params):
    '''以恢复模式启动一个worker
        Args:
            params: 字典, 参数字典:必须包括对应的worker_name
    '''

    is_ok, errors = check_params(params, 'worker_name')
    if not is_ok:
        return result(400, "params error", str(errors))
    else:
        try:
            worker_name = params.pop('worker_name')
            record = RecorderManager.instance().get_fail_worker_record(worker_name)
            if not record:
                return result(400, "not exist this fail worker", worker_name)
            else:
                schedule_params = record.get('schedule_kwargs')
                spider_params = record.get('spider_kwargs')
                schedule_path = record.get('schedule_class')
                spider_path = record.get('spider_class')
            schedule = get_schedule_class(schedule_path)(**schedule_params)
            spider = get_spider_class(spider_path)(schedule, **spider_params)
            recover_worker(spider)
            RecorderManager.instance().remove_last_fail_worker(worker_name)
        except ScheduleError, e:
            return result(400, message="init schedule failed", result=str(e))
        except SpiderError, e:
            return result(400, message="init spider failed", result=str(e))
        except WorkerError, e:
            return result(400, message="recover worker failed", result=str(e))
        except Exception, e:
            return result(500, "unsupported exception", result=str(e))
        else:
            return result(200, "recover worker success", "success")

@api_route(r"/api/remove_fail_worker")
def api_remove_fail_worker(params):
    """清除fail worker记录，以及相关队列
        Args:
            params: dict, 参数字典，必须包括worker_name
    """
    is_ok, error = check_params(params, "worker_name")
    if not is_ok:
        return result(400, "params error", str(error))
    else:
        worker_name = params.pop("worker_name")
        record = RecorderManager.instance().get_fail_worker_record(worker_name)
        if not record:
            return result(400, "not exist this fail worker", worker_name)
        else:
            try:
                schedule_params = record.get('schedule_kwargs')
                spider_params = record.get('spider_kwargs')
                schedule_path = record.get('schedule_class')
                spider_path = record.get('spider_class')
                schedule = get_schedule_class(schedule_path)(**schedule_params)
                spider = get_spider_class(spider_path)(schedule, **spider_params)
                spider.clear_all()
                RecorderManager.instance().remove_last_fail_worker(worker_name)
            except ScheduleError, e:
                return result(400, message="init schedule failed", result=str(e))
            except SpiderError, e:
                return result(400, message="init spider failed", result=str(e))
            except WorkerError, e:
                return result(400, message="recover worker failed", result=str(e))
            except Exception, e:
                return result(500, "unsupported exception", result=str(e))
            else:
                return result(200, "success", "remove success")
