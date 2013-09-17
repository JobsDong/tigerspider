#!/usr/bin/python2.7
#-*- coding=utf-8 -*-

# Copy Rights (c) Beijing TigerKnows Technology Co., Ltd.

"""用于封装redis的操作
    RedisError: 表示redis内部错误
    RedisQueue: 使用redis创建的队列
    RedisDict: 使用redis创建的字典
    RedisSet: 使用redis创建的集合
"""

__author__ = ['"wuyadong" <wuyadong@tigerknows.com>']

import redis
from core.util import PickleDeocoder, PickleEncoder

class RedisError(Exception):
    """描述redis发生的错误

    """
    pass

class RedisQueue(object):
    """Redis构成的队列
    """
    def __init__(self, namespace, **kwargs):
        """初始化redis连接器
            Args:
                namespace, str, 名字空间
                kwargs, 字典，表示redis初始化需要的参数

            Raises:
                RedisError: 当发生错误的时候
        """
        try:
            self._db = redis.Redis(**kwargs)
            self.namespace = namespace
        except Exception, e:
            raise RedisError("connect to redis failed:%s" % e)

    def size(self):
        """返回队列的长度
            Returns:
                size: int 队列的长度
            Raises:
                RedisError: 当发生redis错误的时候
        """
        try:
            return self._db.llen(self.namespace)
        except Exception, e:
            raise RedisError("redis error:%s" % e)

    # 非阻塞
    def pop(self):
        """弹出一个对象
            Returns:
                obj, object, 一个python对象，类型取决于压入的类型
            Raises:
                RedisError: 当发生错误的时候
        """
        try:
            item = self._db.lpop(self.namespace)
        except Exception, e:
            raise RedisError("redis error:%s " % e)
        try:
            obj = None if item is None else PickleDeocoder().decode(item)
            return obj
        except Exception, e:
            raise RedisError("pickle decode error:%s" % e)

    def push(self, value):
        """压入一个对象
            Args:
                value: object, 一个python对象，不可一世file对象
            Raises:
                RedisError: 当发生错误的时候
        """
        try:
            encodedvalue = PickleEncoder().encode(value)
        except Exception, e:
            raise RedisError("encode error:%s" % e)

        try:
            self._db.rpush(self.namespace, encodedvalue)
        except Exception, e:
            raise RedisError("redis error:%s" % e)

    def clear(self):
        """清除队列中的所有对象
            Raises:
                RedisError: 当发生错误的时候
        """
        try:
            self._db.delete(self.namespace)
        except Exception, e:
            raise RedisError("delete error:%s" % e)

class RedisDict(object):
    """使用redis技术实现的一个字典

    """
    def __init__(self, namespace, **kwargs):
        """初始化
            Args:
                namespace: str, 名字空间
                kwargs: 字典, 连接redis的参数表
            Raises:
                RedisError: 当发生错误的时候
        """
        try:
            self._db = redis.Redis(**kwargs)
            self.namespace = namespace
        except Exception, e:
            raise RedisError("connect to redis error:%s " % e)

    def get(self, key):
        """获取key对应的对象
            Args:
                key: str, key值
            Returns:
                object: Object, 如果对象存在就返回这个对象，否则返回None
            Raises:
                RedisError: 当发生错误的时候
        """
        try:
            item = self._db.hget(self.namespace, key)
        except Exception, e:
            raise RedisError("redis error:%s" % e)

        try:
            decoded_value = None if item is None else PickleDeocoder().decode(item)
            return decoded_value
        except Exception, e:
            raise RedisError("decode error:%s" % e)

    def set(self, key, value):
        """设置对应key的值
            Args:
                key: str, key值
                value: object, value值

            Raises:
                RedisError: redis 的错误
        """
        try:
            encodedvalue = PickleEncoder().encode(value)
        except Exception, e:
            raise RedisError("encode error:%s" % e)

        try:
            self._db.hset(self.namespace, key, encodedvalue)
        except Exception, e:
            raise RedisError("redis error:%s" % e)

    def clear(self):
        """清除所有对象
            Raises:
                RedisError: redis出现错误
        """
        try:
            self._db.delete(self.namespace)
        except Exception, e:
            raise RedisError("redis error: %s" % e)

    def has_key(self, key):
        """检查是否含有某个key
            Returns:
                is_exists:bool ,如果存在就返回True否则False

            Raises:
                RedisError:当发生错误的时候
        """
        try:
            return self._db.hexists(self.namespace, key)
        except Exception, e:
            raise RedisError("redis error:%s" % e)

    def delete(self, key):
        """删除对应的key
            Raises:
                RedisError:当发生错误的时候
        """
        try:
            self._db.hdel(self.namespace, key)
        except Exception, e:
            raise RedisError("redis error:%s" % e)


class RedisSet(object):
    """使用redis构造的结合

    """
    def __init__(self, namespace, **kwargs):
        """初始化
            Args:
                namespace: str, 名字空间
                kwargs: dict, 连接redis的参数
            Raises:
                RedisError:当发生错误的时候
        """
        try:
            self._db = redis.Redis(**kwargs)
            self.namespace = namespace
        except Exception, e:
            raise RedisError("connect to redis error:%s" % e)

    def add(self, value):
        """增加一个元素
            Args:
                value, object， 一个python的对象,不可以是file对象,
            Raises:
                RedisError: 当发生错误的时候
        """
        try:
            encodedvalue = PickleEncoder().encode(value)
        except Exception, e:
            raise RedisError("encode error:%s" % e)

        try:
            self._db.sadd(self.namespace, encodedvalue)
        except Exception, e:
            raise RedisError("redis error:%s" % e)

    def delete(self, value):
        """删除一个对象
            Args:
                value, object, 一个python对象，不可以是file对象

            Raises:
                RedisError: 当发生错误的时候
        """
        try:
            encodedvalue = PickleEncoder().encode(value)
        except Exception, e:
            raise RedisError("encode error:%s" % e)

        try:
            self._db.srem(self.namespace, encodedvalue)
        except Exception, e:
            raise RedisError("redis error:%s" % e)

    def exist(self, value):
        """判断value是否存在
            Args:
                value, object, 一个python对象，不可以是file对象
            Raises:
                RedisError:当发生错误的时候
        """
        try:
            encodedvalue = PickleEncoder().encode(value)
        except Exception, e:
            raise RedisError("encode error:%s" % e)

        try:
            self._db.sismember(self.namespace, encodedvalue)
        except Exception, e:
            raise RedisError("redis error:%s" % e)

    def size(self):
        """返回大小
            Returns:
                size: int, 长度
            Raises:
                RedisError:当发生错误的时候
        """
        try:
            return self._db.scard(self.namespace)
        except Exception, e:
            raise RedisError(e)

    def random_pop(self):
        """随机返回一个对象
            Returns:
                obj: object, 一个python对象，有可能是空
        """
        try:
            value = self._db.spop(self.namespace)
        except Exception, e:
            raise RedisError("redis error:%s" % e)

        try:
            decoded_value = None if value is None else PickleDeocoder().decode(value)
            return decoded_value
        except Exception, e:
            raise RedisError("decode error:%s" % e)

    def clear(self):
        """清除所有对象
            Raises:
                RedisError:当发生错误的时候
        """
        try:
            self._db.delete(self.namespace)
        except Exception, e:
            raise RedisError("redis error:%s" % e)