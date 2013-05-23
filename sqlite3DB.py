#coding:utf-8
__author__ = 'watsy'
import sqlite3

class sqlite3DB(object):
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name)

    def __del__(self):
        self.conn.close()


    def isSqlExecuteEmpty(self, sql):
        c = self.conn.cursor()
        c.execute(sql)
        ret = c.fetchall()
        c.close()

        return len(ret)


    def getExecuteResult(self, sql):
        c = self.conn.cursor()
        c.execute(sql)
        ret = c.fetchall()
        c.close()

        return  ret


    def insert(self, sql):
        c = self.conn.cursor()
        c.execute(sql)
        self.conn.commit()
        c.close()
