#coding:utf-8
__author__ = 'watsy'

import json
import urllib2
import sqlite3
import sqlite3DB

# 火车
class trainObject(object):
    def __init__(self, tid="", code="", start_city="", start_abbr = "", end_abbr = "", start_time="", end_city="", end_time="", full_time=""):
        self.tid = tid
        self.code = code
        self.start_city = start_city
        self.start_time = start_time
        self.start_abbr = start_abbr
        self.end_abbr = end_abbr
        self.end_city = end_city
        self.end_time = end_time
        self.full_time = full_time

    def get_writestr(self):
        # return ("%s,%s,%s,%s,%s,%s,%s") % (self.tid, self.code, self.start_city.encode('utf-8'), self.start_time, self.end_city.encode('utf-8'), self.end_time, self.full_time)
        str_return = self.tid + ","
        str_return += self.code + ","
        str_return += self.start_city + ","
        str_return += self.start_time + ","
        str_return += self.end_city + ","
        str_return += self.end_time + ","
        str_return += self.full_time

        return str_return

# 是否存在db
def isTrainExist(train, db):
    sql = """select * from CWTrainObject where sCode = "%s"; """ % train.code
    return db.isSqlExecuteEmpty(sql)
    # pass

# 获取train在数据库中的ID
def getCWTrainObjectIDWithTrain(train, db):
    sql = """select * from CWTrainObject where sCode = "%s"; """ % train.code
    ret = db.getExecuteResult(sql)
    return ret[0][1]

# 插入db
def insertTrain(train, db):
    sql = """ insert into CWTrainObject (`sCode`, `trainID`) values ("%s", "%s") """ % (train.code, train.tid)
    db.insert(sql)

    # pass


# 生成获取列车url地址
def getBookingTrainListUrl(start_code, end_code, day):
    strUrl =  ("http://dynamic.12306.cn/otsquery/query/queryRemanentTicketAction.do?method=queryLeftTicket&")

    strUrl += ("orderRequest.train_date=%s&") % (day)
    strUrl += ("orderRequest.from_station_telecode=%s&") % (start_code)
    strUrl += ("orderRequest.to_station_telecode=%s&") % (end_code)
    strUrl += ("orderRequest.train_no=&trainPassType=QB&trainClass=QB%23D%23Z%23T%23K%23QT%23&includeStudent=00&seatTypeAndNum=&orderRequest.start_time_str=00%3A00--24%3A00")

    return strUrl

# 获取城市列车信息
def getDataWithStartAndEndCity(startcode, endcode, selectdate):
    try:
        strurl = getBookingTrainListUrl(startcode, endcode, selectdate)

        url_add_header = urllib2.Request(strurl)
        url_add_header.add_header('X-Requested-With', "XMLHttpRequest")
        url_add_header.add_header('Referer', "http://dynamic.12306.cn/otsquery/query/queryRemanentTicketAction.do?method=init")
        url_add_header.add_header('Content-Type', 'application/x-www-form-urlencoded')
        url_add_header.add_header('Connection', 'keep-alive')

        resp = urllib2.urlopen(url_add_header)
        urlread = resp.read()
        resp.close()

        return (urlread, strurl)

    except TypeError as error:
        print "error [%s]: url [%s] \n\ndata:[%s]" % (error, strurl, urlread)

    return (0,0)





# 解析 预定车次列表
def parser_booking_str(str_booking):
    json_book = json.loads(str_booking)
    datas = json_book['datas']
    parser_list = []
    if datas and len(datas) > 1:
        # print datas.replace("&nbsp;","")
        trainlist = datas.replace("&nbsp;","").split("\\n")
        for train_str in trainlist:
            train_str_list = train_str.split(',')

            if len(train_str_list) == 17:
                str_id_and_code = train_str_list[1]
                str_start_city_and_time = train_str_list[2]
                str_end_city_and_time = train_str_list[3]
                str_full_time = train_str_list[4]

                # print str_id_and_code
                str_id = str_id_and_code[13:25]
                str_code = str_id_and_code[131:-7]

                # start abbr and end abbr
                abbr_list = str_id_and_code.split('#')
                start_abbr = abbr_list[1]
                end_abbr = abbr_list[2][0:3]

                # print str_start_city_and_time
                if len(str_start_city_and_time) > 50:
                    str_start_city = str_start_city_and_time[43:-9]
                else :
                    str_start_city = str_start_city_and_time[0:-9]

                str_start_time = str_start_city_and_time[-5:]
                # print str_end_city_and_time
                if len(str_end_city_and_time) > 50:
                    str_end_city = str_end_city_and_time[42:-9]
                else:
                    str_end_city = str_end_city_and_time[0:-9]
                str_end_time = str_end_city_and_time[-5:]

            tobj = trainObject(str_id, str_code, str_start_city, start_abbr, end_abbr, str_start_time, str_end_city, str_end_time, str_full_time)
            parser_list.append(tobj)
    return parser_list


def getTrainFullStationInfo(startCode, endCode, trainid, selectdate , db, trainDBid):

    strUrl = "http://dynamic.12306.cn/otsquery/query/queryRemanentTicketAction.do?method=queryaTrainStopTimeByTrainNo&train_no="
    #6i00000G7200&from_station_telecode=IOQ&to_station_telecode=BXP&depart_date=2013-05-25
    strUrl += trainid
    strUrl += "&from_station_telecode="
    strUrl += startCode
    strUrl += "&to_station_telecode="
    strUrl += endCode
    strUrl += "&depart_date="
    strUrl += selectdate

    #获取
    url_add_header = urllib2.Request(strUrl)
    resp = urllib2.urlopen(url_add_header)
    urlread = resp.read()
    resp.close()

    #转化提取首尾
    # print strUrl
    parser_train = json.loads(urlread)

    # [{u'arrive_time': u'----', u'isEnabled': False, u'station_no': u'01', u'station_name': u'\u6f20\u6cb3', u'start_time': u'22:26', u'stopover_time': u'----'},
    for info in parser_train:
        sql = """select * from CWTrainStationObject where trainObject = %d and station_name = "%s";""" % (trainDBid, info[u'station_name'])

        if not db.isSqlExecuteEmpty(sql):
            sql = """insert into CWTrainStationObject (`arrive_time`, `start_time`, `station_name`, `station_no`, `stopover_time`, `trainObject`) values ("%s","%s","%s","%s","%s","%d");""" \
                  % (info[u'arrive_time'], info[u'start_time'], info[u'station_name'], info[u'station_no'], info[u'stopover_time'], trainDBid)
            db.insert(sql)


