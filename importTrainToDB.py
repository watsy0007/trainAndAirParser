#/usr/bin/python
#coding:utf-8
__author__ = 'watsy'

import sqlite3
import sys
import os


def insertTrainDB(dirPath , c, conn):
    try:
        for path in os.listdir(dirPath):
            path = os.path.join(dirPath, path)

            with open(path, 'r') as trainFile:
                train_data =  trainFile.read()
                train_list = train_data.split(',')
                sql = """select * from CWTrainObject where `sCode` = "%s";""" % (train_list[1])
                c.execute(sql)
                res = c.fetchall()
                if len(res) == 0:
                    sql = """insert into CWTrainObject (`trainID`, `sCode`, `startPlace`, `startTime`, `endPlace`, `endTime`, `fullTime`) values ("%s", "%s", "%s", "%s", "%s", "%s", "%s")""" % (train_list[0], train_list[1], train_list[2], train_list[3], train_list[4], train_list[5], train_list[6])
                    # print  sql
                    c.execute(sql)
                    conn.commit()
    except IOError:
        print "error"


def insertAirDB(dirPath, c, conn):
    try:
        for path in os.listdir(dirPath):
            path = os.path.join(dirPath, path)

            with open(path, 'r') as airFile:
                air_data = airFile.read()
                air_list = air_data.split(',')
                sql = """select * from CWAirObject where `sCode` = "%s";""" % (air_list[0])
                c.execute(sql)
                res = c.fetchall()
                if len(res) == 0:
                    print air_list
                    sql = """insert into CWAirObject (`sCode`, `startPlace`, `startTime`, `endPlace`, `endTime`, `airType`, `sFlyWeekend`, `middleStop`, `punctualityRate`) values ("%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s")""" \
                          % (air_list[0], air_list[1], air_list[2], air_list[3], air_list[4], air_list[5], air_list[6], air_list[7], air_list[8])
                    c.execute(sql)
                    conn.commit()

    except IOError:
        print "air import error"

conn = sqlite3.connect('records.db')
c = conn.cursor()

#当前路径
currentPath = os.getcwd()

print "load train data"
insertTrainDB(currentPath + "/train", c, conn)
print "load air data"
insertAirDB(currentPath + "/air", c, conn)

c.close()
conn.close()



