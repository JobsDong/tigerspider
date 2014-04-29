==========
Web服务
==========

tigerspider内部有用于监控和控制的web界面和api接口。用户可以通过web界面查看抓取任务的进度已经抓取详情。
同时可以通过API接口对任务进行控制。

web界面
========

* **主页** ``http://{host}:{port}/web/homepage.html``
* **schedule描述页** ``http://{host}:{port}/web/schedule.html``
* **spider描述页** ``http://{host}:{port}/web/spider.html``
* **worker描述页** ``http://{host}:{port}/web/worker.html``
* **worker的统计信息** ``http://{host}:{port}/web/worker_statistic?worker_name={worker_name}``

API接口
========

* 启动抓取任务

    ``http://{host}:{port}/api/start_worker?schedule_path={schedule_path}&spider_path={spider_path}&schedule_interval={schedule_interval}&schedule_max_number={schedule_max_number}``

* 停止某个抓取任务

    ``http://{host}:{port}/api/stop_worker?worker_name={worker_name}``

* 暂停某个抓取任务

    ``http://{host}:{port}/api/suspend_worker?worker_name={worker_name}``

* 唤醒某个抓取任务

    ``http://{host}:{port}/api/rouse_worker?worker_name={worker_name}``

* 恢复崩溃的抓取任务

    ``http://{host}:{port}/api/recover_worker?worker_name={worker_name}``

* 获取所有的worker的概述

    ``http://{host}:{port}/api/get_all_worker``

* 获取某个worker的运行状态

    ``http://{host}:{port}/api/get_worker_statistic?worker_name={worker_name}``

* 获取所有失败的任务概述

    ``http://{host}:{port}/api/get_all_fail_worker``

* 获取所有已经加载成功的spider类描述

    ``http://{host}:{port}/api/get_all_spider_class``

* 获取所有已经加载成功的Schedule类描述

    ``http://{host}:{port}/api/get_all_schedule_class``

* 移除某个崩溃的worker记录

    ``http://{host}:{port}/api/remove_fail_worker?worker_name={worker_name}``

* 暂停所有worker

    ``http://{host}:{port}/api/suspend_all_worker``

* 唤醒所有worker

    ``http://{host}:{port}/api/rouse_all_worker``

* 更新代理列表

    ``http://{host}:{port}/api/reload_proxy``

