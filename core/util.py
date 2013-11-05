#!/usr/bin/python2.7
#-*- coding=utf-8 -*-

# Copy Rights (c) Beijing TigerKnows Technology Co., Ltd.


__authors__ = ['"wuyadong" <wuyadong@tigerknows.com>']

import os
import sys
import re
import logging
import cPickle as pickle
import json
from tornado import gen

from core.datastruct import HttpTask

logger = logging.getLogger("core-util")


class SettingError(Exception):
    """用于表示配置错误的exception
    """


def get_project_path():
    """获取项目的绝对路径
        Returns:
            path: str, 项目路径如:/data/meituan/webspider/
    """
    abs_path = os.path.abspath(sys.argv[0])
    abs_path = os.path.dirname(abs_path)
    return abs_path + os.sep


def remove_white(sentence):
    """去除一个句子的空白字符(whitespace不包括)
        Args:
            sentence: str, 句子
        Returns:
            new_sentence: str, 处理后的句子
    """
    stripped_sentence = sentence.strip()
    new_sentence = re.sub(u'[\r\n\t]', '', stripped_sentence)
    return new_sentence


def unicode2str_for_dict(dictionary):
    """将字典中的unicode类型的字符串换成str
        Args:
            dictionary: 字典
        Returns:
            new_dictionary: 新的字典
    """
    clone_dictionary = {}
    for key, value in dictionary.items():
        key = key if not isinstance(key, unicode) else str(key)
        value = value if not isinstance(value, unicode) else str(value)
        clone_dictionary[key] = value
    return clone_dictionary

def log_exception_wrap(func):
    """记录函数所运行的错误,捕获所有错误
        包装器
        Args:
            func: Function, 函数对象
    """
    def _wrap(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
        except Exception, e:
            logger.error("unexceptted error:%s in %s" % (e, func.__name__))
            print "unexcepted error:%s in %s" % (e, func.__name__)
        else:
            return result
    return _wrap

@gen.coroutine
def coroutine_wrap(func, *args, **kwargs):
    """异步包装器，使得func异步执行

        非真正的异步
        Args:
            func: Function, 函数对象
        Returns:
            result: 如果成功就返回结果，否则返回exception
    """
    try:
        result = func(*args, **kwargs)
    except Exception, e:
        result = e

    raise gen.Return(result)

def xpath_namespace(tree, expr):
    """xpath with namespace

        can't be used in "tree = etree.parser(), just can be used in etree.fromstring()"
        can't have function in expr
        Args:
            tree: Etree, element tree
            expr: str, xpath str
        Return:
            elems: list, list of _Element
    """
    handle_elem = lambda elem: elem if not elem or ":" in elem\
        else "*[local-name()='%s']" % elem

    new_expr = "/".join([handle_elem(elem) for elem in expr.split("/")])
    nsmap = dict((k, v) for k, v in tree.nsmap.items() if k)
    return tree.xpath(new_expr, namespaces=nsmap)


class PickleEncoder(object):
    """使用pickle将对象进行编码
    """

    def encode(self, o):
        """编码函数
            Args:
                o:object,被编码对象
            Returns:
                encoded_value: str, 编码后的字符串
        """
        encoded_value = pickle.dumps(o)
        return encoded_value

class PickleDeocoder(object):
    """使用pickel的解码类
    """

    def decode(self, value):
        """解码函数
            Args:
                value: str, 解码的字符串
            Returns:
                obj: object, 解码后的对象
        """
        obj = pickle.loads(value)
        return obj

class ObjectEncoder(json.JSONEncoder):
    def default(self, o):
        d = {
            '__class__': o.__class__.__name__,
            '__module__': o.__module__,
        }
        d.update(o.__dict__)
        return d

class ObjectDecoder(json.JSONDecoder):
    def __init__(self):
        json.JSONDecoder.__init__(self, object_hook=self.dict_to_object)

    def dict_to_object(self, d):
        if '__class__' in d:
            class_name = d.pop('__class__')
            module_name = d.pop('__module__')
            module = __import__(module_name, {}, {}, [''])
            clazz = getattr(module, class_name)
            args = dict((key.encode('ascii'), value) for key, value in d.items())
            inst = clazz(**args)
        else:
            inst = d
        return inst

def check_http_task_integrity(http_task):
    if not isinstance(http_task, HttpTask):
        return False
    else:
        if http_task.request and http_task.callback:
            return True
        else:
            return False

def get_class_path(claz):
    """获取claz对应的路径（这些路径是可以直接引入的）
        Args:
            claz: ClassType, 类对象
        Returns:
            path: str, 类路径
    """
    return "%s.%s" % (claz.__module__, claz.__name__)


def load_object(path):
    """Load an object given its absolute object path, and return it.

    object can be a class, function, variable o instance.
    path ie: 'scrapy.contrib.downloadermiddelware.redirect.RedirectMiddleware'
    """

    try:
        dot = path.rindex('.')
    except ValueError:
        raise ValueError, "Error loading object '%s': not a full path" % path

    module, name = path[:dot], path[dot+1:]
    try:
        mod = __import__(module, {}, {}, [''])
    except ImportError, e:
        raise ImportError, "Error loading object '%s': %s" % (path, e)

    try:
        obj = getattr(mod, name)
    except AttributeError:
        raise NameError, "Module '%s' doesn't define any object named '%s'" % (module, name)

    return obj

def walk_settings(path='settings.registersettings'):
    '''
    遍历path文件，把里面的spider和schedule注册到相应的route中
    '''
    try:
        spiders = load_object(path + ".spiders")
    except Exception, e:
        raise SettingError, "load object :%s, error:%s" % (path + ".spiders", e)
    else:
        from core.spider.spider import add_spider_class
        for spider_path in spiders:
            try:
                spider = load_object(spider_path)
            except Exception, e:
                raise SettingError, "%s load spider error:%s" % (spider_path, e)
            else:
                add_spider_class(spider_path, spider)

    try:
        schedules = load_object(path + ".schedules")
    except Exception, e:
        raise SettingError, "load object :%s, error:%s" % (path + ".schedules", e)
    else:
        from core.schedule import add_schedule_class
        for schedule_path in schedules:
            try:
                schedule = load_object(schedule_path)
            except Exception, e:
                raise SettingError, "load schedule error:%s" % e
            else:
                add_schedule_class(schedule_path, schedule)

# lambda
flist = lambda elems, default="": default if len(elems) <= 0 else elems[0]

def gcd(*args):
    """gcd algorith

        Args:
            args: list, int
        Returns:
            gcd: int, gcd of list
    """
    if len(args) >= 3:
        return gcd(args[0], gcd(*args[1:]))
    elif len(args) == 2:
        if args[1] == 0:
            return args[0]
        else:
            if args[1] >= args[0]:
                copy_args = args[::-1]
                return gcd(copy_args[1], copy_args[0] % copy_args[1])
            else:
                return gcd(args[1], args[0])
    else:
        return args[0]

def lcm(*args):
    """least common multiply

        Args:
            args: list, init list
        Returns:
            lcm: int, lcm
    """
    if len(args) == 1:
        return args[0]

    t = 1
    gcd_count = gcd(*args)

    for arg in args:
        t *= arg

    for x in xrange(len(args)):
        t /= gcd_count

    return t