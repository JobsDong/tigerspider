#!/usr/bin/python2.7
#-*- coding=utf-8 -*-

# Copy Rights (c) Beijing TigerKnows Technology Co., Ltd.

"""用于操作数据库的类
    DBError: exception, 关于db的错误类
    DB: 关于db操作的类
"""

__authors__ = ['"wuyadong" <wuyadong@tigerknows.com>']

import psycopg2
import psycopg2.extras

class DBError(Exception):
    '''
    exception caused by database
    '''

class DB(object):
    def __init__(self, **kwargs):
        try:
            self.conn = psycopg2.connect(**kwargs)
            self.cur = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        except psycopg2.Error, e:
            raise DBError, e

    def execute_query(self, sql, parameters=None):
        """执行查询操作
            Args:
                sql: str, sql 语句
                parameters: str, 参数语句
            Raise:
                DBError: Exception, 错误
        """
        try:
            self.cur.execute(sql, parameters)
        except psycopg2.Error, e:
            raise DBError, e
        else:
            items = self.cur.fetchall()
            return items

    def execute_update(self, sql, parameters=None):
        """执行更新操作
            Args:
                sql: str, sql语句
                parameters: str, 参数

            Raise:
                DBError:Exception, 错误
        """
        try:
            self.cur.execute(sql, parameters)
        except psycopg2.Error, e:
            self.conn.rollback()
            raise DBError, e
        else:
            self.conn.commit()

    def close(self):
        """关闭，释放资源
        """
        if self.cur:
            self.cur.close()
        if self.conn:
            self.conn.close()