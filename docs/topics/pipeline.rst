==========
pipeline
==========

当一个item被提取出来时，它会被送到item对应的pipeline中去处理。

每一个ItemPipeline组件，都是一个继承与BasePipeline的Python类，pipeline接收到一个item,并且对这个item进行处理.

典型的pipeline的用途:

* 验证提取的数据的正确性
* 检测抓取的数据是否重复，重复扔掉
* 不通item数据的聚合
* 持久划数据

pipeline的方法介绍
==================

构造函数::

    def __init__(self, namesapce):
        ...

Args:
    namespace: 是继承与spider的，启动worker时有个参数spider_namespace={spider_namespace},namespace就是spider_namespace

处理函数::

    def process_item(self, item, kwargs):
        ...

Args:
    item: Item, 是pipeline接收到的item对象.
    kwargs: dict, 是task中的kwargs，一般用于传递一些数据的

一般情况下，我们会将item放入redis中，用于多个item的聚合形成完整的一条数据然后保存到数据库中.

清理函数::

    def clear_all(self):
        ...

主要用于清理一些数据库链接，文件关闭，或者redis清空操作。这个函数一般是在worker结束的时候调用。

典型的Pipeline类
==================

典型的Pipeline类的代码::

    class ActivityItemPipeline(BasePipeline):

        def __init__(self, namesapce, redis_host='192.168.11.108', redis_port=6379, redis_db=0):
            BasePipeline.__init__(self, namesapce)
            self.logger.info("init activity item pipline finished")
            try:
                redis_namespace = "%s:%s" % (namesapce, "temp")
                self.temp_item_dict = RedisDict(redis_namespace, host=redis_host,
                                                port=redis_port, db=redis_db)
            except RedisError, e:
                self.logger.error("redis error %s" % e)
                raise e

        def process_item(self, item, kwargs):
            if isinstance(item, ActivityItem):
                self.temp_item_dict.set(item.url, item)

        def clear_all(self):
            pass

这个pipeline中，构造函数中，初始化了一个redis，在处理item的时候，将item保存到redis中。
