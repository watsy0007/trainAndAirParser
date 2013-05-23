#coding:utf-8
__author__ = 'watsy'

from sgmllib import SGMLParser
import urllib
import urllib2
import datetime

import os
from time import sleep
import time
import sys
from citys import parserCitys, cityObject
from trains import trainObject, isTrainExist,insertTrain, getDataWithStartAndEndCity,parser_booking_str,getTrainFullStationInfo, getCWTrainObjectIDWithTrain
from sqlite3DB import sqlite3DB

db = sqlite3DB('records.db')

def parserTrains(startIndex, endIndex = 0):

    #获得城市列表
    parser_citys = parserCitys()

    #过滤城市
    print "sort and filter the same citys"
    sort_citys = []
    bSameCity = False
    for city1 in parser_citys:
        for city2 in sort_citys:
            if city2.chinaname == city1.chinaname[0:len(city2.chinaname)]:
                bSameCity = True
                break

        if not bSameCity:
            sort_citys.append(city1)
        bSameCity = False


    #length
    city_length = len(sort_citys)

    print "calcute the date"
    today = datetime.date.today()
    torrow = datetime.timedelta(days=5)
    today = today + torrow

    day_str = ("%s-%02d-%02d") % (today.year, int(today.month), int(today.day))

    print "select date : " + day_str

    if endIndex == 0:
        endIndex = city_length

    for i in range(startIndex, endIndex):
        print ("[index : %d] %s" % (i, time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))))
        for j in range(0 , len(sort_citys) - i):
            try:
                sleep(0.1)
                (urlread, strurl) = getDataWithStartAndEndCity(sort_citys[i].shortCode, sort_citys[j].shortCode, day_str)

                if len(urlread) > 0:
                    parser_list = parser_booking_str(urlread)

                    for train in parser_list:
                         if not isTrainExist(train, db):

                            insertTrain(train ,db)

                            trainDBid = getCWTrainObjectIDWithTrain(train, db)

                             #插入train的站点信息
                            sleep(0.1)

                            getTrainFullStationInfo(train.start_abbr, train.end_abbr, train.tid, day_str, db, trainDBid)

                            print "insert a train and stations info code = [%s]" %  (train.code)

                else:
                    raise urllib2.HTTPError

            except urllib2.HTTPError as err:
                print ("error[%s] : [%s] url=[%s]") % (time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())), err, strurl)
                if j >= 2:
                    j = j - 2
                elif j == 1:
                    j = 0
                # 延时3分钟从新开启
                sleep(60 * 3)
                # exit(1)
            except IndexError as error:
                print ("error[%s] : [%s] url=[%s] index = ") % (time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())), error, strurl)


if __name__ == '__main__':

    # print sys.argv
    if len(sys.argv) == 3:
        startIndex = int(sys.argv[1])
        endIndex = int(sys.argv[2])
        # print startIndex
        parserTrains(startIndex, endIndex)
    elif len(sys.argv) == 2:
        startIndex = int(sys.argv[1])
        parserTrains(startIndex)
    else:
        parserTrains(0)





