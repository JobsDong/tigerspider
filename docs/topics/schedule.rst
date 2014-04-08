==========
schedule
==========

Schedule是用于控制数据抓取的规则，以及爬虫游历的规则。通常情况想Schedule只需要使用自带的RedisSchedule就可以了。RedisSchedule是基于Redis实现的Schedule。Redis中保存了prepare_queue, processed_queue, fail_queue, processed_url_set.

这些数据结构分别是:

* prepare_queue, 是待抓取的url队列
* processed_queue 暂时未使用
* fail_queue 失败任务的队列
* processed_url_set 已经抓取成功的url集合

一个典型的Schedule需要实现的功能包括:

#) 能够保存待抓取的任务
#) 能够获取一个待抓取的任务
#) 能够插入一个待抓取的任务
#) 能够查询一个任务是否已经抓取
#) 能够查询还剩下多少任务没有抓取


BaseSchedule的类
==================

BaseSchedule类的代码::

    class BaseSchedule(object):
        schedule_classes = {}

        def __init__(self, interval=30, max_number=15):
            self.logger = logging.getLogger(self.__class__.__name__)
            self._interval = interval
            self._max_number = max_number

        @property
        def interval(self):
            return self._interval

        @property
        def max_number(self):
            return self._max_number

        def pop_task(self):
            ...

        def push_new_task(self, task):
            ...

        def flag_url_haven_done(self, url):
            ...

        def handle_error_task(self, task):
            ...

        def fail_task_size(self):
            ...

        def dumps_all_fail_task(self):
            ...

        def clear_all(self):
            ...

一个Schedule类必须要实现一下方法:

* pop_task  弹出一个任务
* push_new_task  压入一个新任务
* flag_url_haven_done 标记一个任务抓取过
* handle_error_task  处理一个错误task
* fail_task_size  任务的个数
* clear_all 清理数据