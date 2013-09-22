#!/usr/bin/python2.7
#-*- coding=utf-8 -*-

# Copy Rights (c) Beijing TigerKnows Technology Co., Ltd.


__authors__ = ['"wuyadong" <wuyadong@tigerknows.com>']

import psycopg2
import psycopg2.extras

class DBException(Exception):
    '''
    exception caused by database
    '''
    pass

class DB(object):
    def __init__(self, **kwargs):
        try:
            self.conn = psycopg2.connect(**kwargs)
            self.cur = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        except psycopg2.Error, e:
            raise DBException, e

    def execute_query(self, sql, parameters=None):
        try:
            self.cur.execute(sql, parameters)
        except psycopg2.Error, e:
            raise DBException, e
        else:
            items = self.cur.fetchall()
            return items

    def execute_update(self, sql, parameters=None):
        try:
            self.cur.execute(sql, parameters)
        except psycopg2.Error, e:
            self.conn.rollback()
            raise DBException, e
        else:
            self.conn.commit()

    def close(self):
        if self.cur:
            self.cur.close()
        if self.conn:
            self.conn.close()