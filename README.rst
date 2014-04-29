======================
tigerspider一览
======================

tigerspider是一个用于抓取网页以及解析出有用信息的爬虫框架.

虽然tigerspider是为了抓取网页设计的爬虫框架，但是同样适用于从APIS（如Amazon Associates Web Services）提取数据.

这篇文档的目的是为了向您介绍tigerspider的基本使用，使得您可以使用tigerspider完成基本的数据抓取任务.

如果你准备好了，就可以开始阅读这篇文档了.


安装运行环境
=====================

运行tigerspider所需要的库有:

 * tornado
 * redis
 * docopt
 * psycopg2
 * requests

如果你有setuptools,你可以如下方式安装所有的库::

    easy_install tornado


抓取一个网页
============

现在你想从一个网页中提取需要的数据，但是网站没有提供可用的APIS. 那么tigerspider可以帮助你抓取需要的数据.

假设现在我们需要从一个网页中提取一些需要的信息，我们需要如何做。
我们试着抓取一个网页的内容:

    http://www.228.com.cn/ticket-49052202.html

如果这个网页失效了，你可以选择http://www.228.com.cn中任一个票务信息，进行抓取.

定义你需要提取的数据
=====================

第一步是定义你所要提取出来的数据。在tigerspider中，这是通过Item来实现的.
这将会是我们定义的item::

    from tigerspider.core.datastruct import Item

    class WebItem(Item):
        """描述活动详情页提取出来的数据
        """
        def __init__(self, url, order, description,
                     time_info, price, name):
            self.url = url # url
            self.order = order # 订票电话
            self.description = description # 详情介绍
            self.time_info = time_info # 时间信息
            self.price = price # 价格
            self.name = name # 名字

实现一个解析内容的解析器
========================

接下来我们介绍如何实现一个解析器，用于提取网页的内容.

网页的url,比较容易获得，就是你访问的url地址.

我们使用Xpath来提取网页的html信息. 我们可以观察一下我们需要提取的description, picture_path, time_info, price,都可以通过xpath比较容易的提取出来.

查看html代码，可以发现name是在 ``<div class="product-price-titleul">`` 中::

    <div class="product-price-titleul">
      <h1>2014曲婉婷say the words 我为你歌唱 中国巡回演唱会
        <span class="product-price-zt">
      </h1>
      ...

可以通过一个xpath语句得到name信息::

    //div[@clas='product-price-titleul']/h1/text()

我们可以查看html代码，我们可以注意到 ``<li class="tel">``::

    <li class="tel">
      订票电话：
      <span>4006-228-228</span>
    </li>

那么我们可以通过一个Xpath表达式来提取出电话::

   //div[@class='top-w']//li[@class='tel']/span/text()

同时价格是在 ``<div class="productnew-header-pricec2 clearfloat">`` tag中的::

    <div class="productnew-header-pricec2 clearfloat">
     <ul id="z_price", class="productnew-header-pricec2-ul productnew-header-pricec3-ul productnew-header-pricec2-cq">
       <li type="price">
        <span>180</span>
       </li>
       ....

我们可以通过一个xpath来提取price::

     //ul[@class='productnew-header-pricec2-ul productnew-header-pricec3-ul productnew-header-pricec2-cq']/li/@title


时间信息，也可以看到是再 ``<ul>`` 中::

    <ul id="z_date" class="productnew-header-pricea2-ul clearfloat">
      <li class="choose" type="date" d="2014-05-30 19:30">
      ...

所以我们也可以通过xpath获得时间信息::

    //ul[@class='productnew-header-pricea2-ul clearfloat']/li/@d

最后description是在 ``<div>`` 标签中::

    <div class="product-detail-alla-cont" style="line-height:26px;margin-top:12px;">
      ...

我们可以使用一个xpath获得::

    //div[@class='product-detail-alla-cont']

如果需要详细了解XPath，请访问 http://www.w3school.com.cn/xpath/index.asp

最终的解析代码如下::

    from lxml import html

    from tigerspider.core.util import flist
    from tigerspider.core.spider.parser import BaseParser
    from tigerspider.spiders.intro1.items import WebItem


    class ActivityParser(BaseParser):
        """用于解析活动详情页面的解析器
        """
        def __init__(self, namespace):
            BaseParser.__init__(self, namespace)
            self.logger.info(u"init Activity Parser finished")

        def parse(self, task, input_file):
            """详情解析器
                Args:
                    task, HttpTask, 任务
                    input_file: file, 网页文件
                Yields:
                    item: WebItem, 数据
                    task: HttpTask, 新任务
            """
            tree = html.parse(input_file)
            name = flist(tree.xpath(u"//div["
                                    u"@clas='product-price-titleul']/h1/text()"))
            desc_elems = tree.xpath(u"//div[@class='product-detail-alla-cont']")
            description = _extract_desc_elems(desc_elems)
            date_elems = tree.xpath(
                u"//ul[@class='productnew-header-pricea2-ul clearfloat']/li/@d")
            telephone = flist(tree.xpath(
                u"//div[@class='top-w']//li[@class='tel']/span/text()"))
            telephone = telephone.replace(u"-", u"")
            if len(telephone) == 0:
                telephone = u"4006228228"
            price_elems = tree.xpath(
                u"//ul[@class='productnew-header-pricec2-ul productnew-"
                u"header-pricec3-ul productnew-header-pricec2-cq']/li/@title")
            price_infos = list()
            for price_elem in price_elems:
                if unicode(price_elem) not in price_infos:
                    price_infos.append(unicode(price_elem))
            price_info = u"/".join(price_infos)
            time_infos = []
            for date_elem in date_elems:
                time_infos.append(date_elem)
            time_info = u";".join(time_infos)
            url = task.request.url

            # 保存详情信息
            yield WebItem(url, telephone, description,
                          time_info, price_info, name)


    def _extract_desc_elems(desc_elems):
        """extract description
            Args:
                desc_elems: list, [Elment]
            Returns:
                description: unicode, description
        """
        texts = []
        for desc_elem in desc_elems:
            for text in desc_elem.itertext():
                texts.append(text.strip())
        return u"".join(texts)


实现一个处理结果的处理器
========================

在tigerspider中，是通过pipeline来处理解析出来的结果的.
pipeline捕获到解析器中yield出来的对象，并进行处理。以下我们就将解析出来的结果保存到csv文件中.
我们定义的WebItemPipeline如下::

    import csv

    from tigerspider.core.spider.pipeline import BasePipeline
    from tigerspider.spiders.intro1.items import WebItem

    class WebItemPipeline(BasePipeline):

        def __init__(self, namespace, out_path=u"/home/wuyadong/webitem.csv"):
            BasePipeline.__init__(self, namespace)
            self._out_file = open(out_path, u"wb")
            self._csv_file = csv.writer(self._out_file)
            self.logger.info(u"init WebItemPipeline finish")

        def process_item(self, item, kwargs):
            """process web item
                Args:
                    item: WebItem
            """
            if isinstance(item, WebItem):
                no_unicode = lambda a: a.encode(u'utf-8') if isinstance(
                    a, unicode) else a

                url = no_unicode(item.url)
                order = no_unicode(item.order)
                description = no_unicode(item.description)
                time_info = no_unicode(item.time_info)
                price = no_unicode(item.price)
                name = no_unicode(item.name)
                self._csv_file.writerow([name, url, order, price, time_info,
                                         description])

        def clear_all(self):
            self._out_file.close()


完成最后的spider
=======================

我们需要用一个Spider类组织齐需要的解析器，和处理器，来描述一个Spider的基本组成，我们是通过Spider来实现的::

    from tornado.httpclient import HTTPRequest
    from tigerspider.core.spider.spider import BaseSpider
    from tigerspider.core.datastruct import HttpTask
    from tigerspider.spiders.intro1.parser import ActivityParser
    from tigerspider.spiders.intro1.pipeline import WebItemPipeline


    class Intro1Spider(BaseSpider):

        parsers = {
            u"ActivityParser": ActivityParser,
        }

        pipelines = {
            u"WebItem": WebItemPipeline,
        }

        start_tasks = [HttpTask(HTTPRequest(
            u"http://www.228.com.cn/ticket-49052202.html"),
                                callback=u"ActivityParser")]


start_tasks是一个描述开始任务的列表，pipelines和parsers是放置对应的解析器和处理器的类对象


启动Spider
=============

最后，我们将会启动爬虫，去抓取数据，并将解析出来的数据以csv格式保存到本地文件中。

* 首先，我们要在settings/registersettings注册一下对应的spider::

     spiders = ['spiders.intro1.spider.Intro1Spider']

* 启动monitor进程::

     python monitor.py

* 通过api接口启动抓取worker,在浏览器输入url::

    http://127.0.0.1:1235/api/start_worker?schedule_path=schedules.schedules.RedisSchedule&spider_path=spiders.intro1.spider.Intro1Spider&schedule_interval=1000&schedule_max_number=1

这样，稍等片刻就会有数据输出，可以看到webitem.csv中存放的数据

