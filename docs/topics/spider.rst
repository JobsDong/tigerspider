=============
Spider介绍
=============

Spider 是描述一个网站的抓取需要的组件。换句话说，即使Spider是组织Parser, Item, Pipeline的。

Spider的组成
==============

一个典型的Spider包括:parser, pipeline, start_tasks.Parser是解析器, Pipeline是处理器，start_tasks是开始任务.

一个典型的Spider是这样的::

    class Com228Spider(BaseSpider):
        """用于处理www.228.com的数据抓取爬虫
        """
        parsers = {
            "DealParser": DealParser,
            "ActivityParser": ActivityParser,
            "PictureParser": PictureParser,
        }

        pipelines = {
            "ActivityItem": ActivityItemPipeline,
            "WebItem": WebItemPipeline,
            "PictureItem": PictureItemPipeline,
        }

        start_tasks = create_city_type_tasks()

* parsers是一个字典，key和task的callback参数是一致的，描述这个task是又哪个parser来解析.
* pipelines是一个字典, key是Item的的类名，用于描述Item和pipeline的对应关系
* start_tasks 是一个Task的列表，是爬虫初始的任务队列
