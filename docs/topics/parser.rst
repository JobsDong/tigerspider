=======
Parser
=======

Parser是描述某一特定的网站的解析方法的类。Parser实现了对网站的解析，提取出需要的结果，同时可以产生新的任务，加入抓取队列中。一般的，用户通常使用xpath, 正则表达式，sax流或者dom树来解析网站，tigerspider默认推荐使用lxml来解析。

Parser的方法介绍
==================

构造函数::

    def __init__(self, namespace):
        ...

Args:
 * namespace
    namespace是继承自spider中的，启动worker的时候，有一个参数spider_namespace={spider_namespace},其中的值最终被parser的构造函数捕捉。通常情况下是没有用的。

解析函数::

    def parse(self, task, input_file):
        ...

Args:
 * task
    可能是HttpTask也可能是FileTask。是描述任务的对象，详细请参见具体的类定义
 * input_file
    实际上是一个StringIO对象，如果是FileTask,那么input_file就是文件对象，如果是HttpTask，那么input_file就是网络流.

Yields:

通常parser函数中没有返回值，一般会yield出item对象和task对象，实际上parse函数是一个迭代器，抛出的对象最终会被spider捕捉，然后根据类型分配给不同的parser和pipeline来处理.

典型的Parser类
==================

典型的Parser类的代码::

    class ActivityParser(BaseParser):

        def __init__(self, namespace, picture_dir=DEFAULT_PICTURE_DIR,
                     picture_host=DEFAULT_PICTURE_HOST):
            BaseParser.__init__(self, namespace)
            self._picture_dir = picture_dir
            self._picture_host = picture_host
            self.logger.info("init Activity Parser finished")

        def parse(self, task, input_file):

            tree = html.parse(input_file)
            pic_url = unicode(flist(tree.xpath("//div[@class='product-price-left']/p/img/@src"),
                                    default=u""))
            desc_elems = tree.xpath("//div[@class='product-detail-alla-cont']")
            description = _extract_desc_elems(desc_elems)
            date_elems = tree.xpath("//ul[@class='productnew-header-pricea2-ul clearfloat']/li/@d")
            telephone = flist(tree.xpath("//div[@class='top-w']//li[@class='tel']/span/text()"), default=u"")
            telephone = telephone.replace(u"-", u"")
            if len(telephone) == 0:
                telephone = u"4006228228"
            price_elems = tree.xpath("//ul[@class='productnew-header-pricec2-ul productnew-"
                                     "header-pricec3-ul productnew-header-pricec2-cq']/li/@title")
            price_infos = list()
            for price_elem in price_elems:
                if unicode(price_elem) not in price_infos:
                    price_infos.append(unicode(price_elem))
            price_info = u"/".join(price_infos)
            time_infos = []
            for date_elem in date_elems:
                time_infos.append(date_elem)
            time_info = u";".join(time_infos)
            url = task.kwargs.get('url')
            cookie_host = task.kwargs.get('cookie_host')
            cookie_count = task.kwargs.get('cookie_count')
            pictures, pic_task = self._check_and_execute_picture(pic_url, cookie_host, cookie_count)
            # 保存详情信息
            yield WebItem(url, telephone, description, pictures, time_info, price_info, u"")
            # 抛出picTask
            if pic_task is not None:
                yield pic_task

这个解析类中的解析函数，大量的使用xpath来解析内容，将解析出的内容包装成一个WebItem并yield出去。值得注意的是parse函数也生成了一个pic_task, 并yield出去了。
