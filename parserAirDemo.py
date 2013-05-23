#coding:utf-8
__author__ = 'watsy'


from sgmllib import SGMLParser
import urllib
import urllib2
import datetime
import json
import os
from time import sleep
import time
import sys
import urlparse

class flightCityObject(object):
    def __init__(self, name="", url="", leaveurl = ""):
        self.name = name
        self.url = url
        self.leaveurl = leaveurl


class flightAirObject(object):
    def __init__(self, air_code = "", start_place = "", start_time = "", end_place = "", end_time = "", air_type = "",flightWeekend = "", hasCenterPlace = "" ,hasFood = "", zhundian = ""):
        self.air_code = air_code
        self.start_place = start_place
        self.start_time = start_time
        self.end_place = end_place
        self.end_time = end_time
        self.air_type = air_type
        self.flightWeekend = flightWeekend
        self.hasFood = hasFood
        self.zhundianlv = zhundian

        self.needQuery = False

        #需要查询具体信息
        if hasCenterPlace != '－':
            self.needQuery = True

        if flightWeekend.find('.') != -1:
            self.needQuery = True

    @property
    def description(self):
        return "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s" % (
            self.air_code,
            self.start_place,
            self.start_time,
            self.end_place,
            self.end_time,
            self.air_type,
            self.flightWeekend,
            self.hasFood,
            self.zhundianlv,
            self.needQuery
        )


class flightSearchParser(SGMLParser):

    def reset(self):
        self.ctx = ""
        self.li = ""

        self.citys = []

        self.url = ""

        SGMLParser.reset(self)

    def start_div(self, attrs):
        for k,v in attrs:
            if k == 'class' and v == 'cityli':
                self.li = 1

    def start_a(self, attrs):
        if self.li == 1:
            for k,v in attrs:
                if k == 'href':
                    self.url = v

    def end_a(self):
        if self.li == 1:
            for city in self.citys:
                if city.name == self.ctx:
                    return

            # 计算到港html地址
            urlsplit =  urlparse.urlsplit(self.url)
            urlpath = urlsplit[2]
            url_city_htm = urlpath.split('/')[-1]
            url_city_htm = ("E_%s") % url_city_htm
            url_city_htm = urlparse.urljoin(self.url, url_city_htm)
            self.citys.append(flightCityObject(self.ctx, self.url, url_city_htm))

    def end_div(self):
        self.li = ""

    def handle_data(self, data):
        if self.li == 1:
            self.ctx = data

# 解析国内离港 国内到港
class flightCityArriveAndLeaveParser(SGMLParser):
    def reset(self):
        self.li_url_flag = False
        self.a_url_flag = False
        self.a_url = ""

        self.url_city_list = []
        SGMLParser.reset(self)

    def start_li(self, attrs):
        self.li_url_flag = True


    def end_li(self):
        self.li_url_flag = False

    def start_a(self, attrs):
        if self.li_url_flag:
            for k,v in attrs:
                if k == 'href':
                    self.a_url_flag = True
                    self.a_url = v

    def end_a(self):
        self.a_url_flag = False

    def handle_data(self, data):
        if self.a_url_flag:
            self.url_city_list.append({'city' : data, 'url' : self.a_url})

# 解析航班信息
class flightTimesParser(SGMLParser):

    def reset(self):
        self.flight_tr_flag = False
        self.flight_td_flag = False

        self.flight_td_list = []
        self.flight_tr_list = []

        SGMLParser.reset(self)

    def start_tr(self, attrs):
        for k,v in attrs:
            if k == 'bgcolor':
                if v == '#FFFFCC' or v == '#FFFFFF':
                    self.flight_tr_flag = True

    def end_tr(self):
        if len(self.flight_td_list) > 0:
            self.flight_tr_list.append(self.flight_td_list)

        self.flight_tr_flag = False
        self.flight_td_list = []

    def start_td(self, attrs):
        if self.flight_tr_flag:
            self.flight_td_flag = True

    def end_td(self):
        self.flight_td_flag = False

    def handle_data(self, data):
        if self.flight_td_flag:
            self.flight_td_list.append(data)


# 获取所有航班页面
def function_get_flight_html_content_flight(url):

    u = urllib.urlopen(url)
    html_content = u.read()
    u.close()


    html_content = html_content.decode('gb2312')
    html_content = html_content.encode('utf-8')
    html_content.replace('gb2312', 'utf-8')

    # print html_content

    ft = flightTimesParser()
    ft.feed(html_content)

    return ft.flight_tr_list



def get_city_flight_times(url):
    try:

        u = urllib.urlopen(url)
        html_content = u.read()
        u.close()


        html_content = html_content.decode('gb2312')
        html_content = html_content.encode('utf-8')
        html_content.replace('gb2312', 'utf-8')

        print "time : [%s] - [%d %s]" % (time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())), i, air.url)
        # print html_content
        cityParser = flightCityArriveAndLeaveParser()
        cityParser.feed(html_content)

        flight_airs = {}
        for url_city in cityParser.url_city_list:
            # print 'parser :' + url_city['url']
            ft = function_get_flight_html_content_flight(url_city['url'])

            for flightTime in ft:

                if len(flightTime) == 12:
                    fao = flightAirObject(flightTime[0], flightTime[2],flightTime[1], flightTime[4],flightTime[3],flightTime[5],
                                      flightTime[6], flightTime[7], flightTime[8], flightTime[9])
                else:
                    fao = flightAirObject(flightTime[0], flightTime[3],flightTime[2], flightTime[5],flightTime[4],flightTime[6],
                                      flightTime[7], flightTime[8], flightTime[9], flightTime[10])

                if flight_airs.has_key(flightTime[0]):
                    continue
                flight_airs[flightTime[0]] = fao


        return flight_airs
    except IOError as error:
        print "get_city_flight_times [%s] " % error
        return {}

def write_dict_to_file(air_dict):
    for air_key in air_dict:
        # print air_key
        with open(air_key + '.txt', 'w') as wf:
            wf.write(air_dict[air_key].description)




u = urllib.urlopen('http://www.feeyo.com/flightsearch.htm')
html_content = u.read()
u.close()

html_content = html_content.decode('gb2312')
html_content = html_content.encode('utf-8')

airParser = flightSearchParser()
airParser.feed(html_content)

# print air and url
# for air in airParser.citys:
    # print air.name + ' ' + air.url + '\t' + air.leaveurl

strPath = os.getcwd()
print len(airParser.citys)
for i in range(154, len(airParser.citys)):
    air = airParser.citys[i]


    os.chdir(strPath + '/air')
    # url
    air_dict = get_city_flight_times(air.url)
    while len(air_dict) == 0:
        sleep(5)
        air_dict = get_city_flight_times(air.url)
    write_dict_to_file(air_dict)
    sleep(0.5)

    # leave url
    air_dict = get_city_flight_times(air.leaveurl)
    while len(air_dict) == 0:
        sleep(5)
        air_dict = get_city_flight_times(air.leaveurl)
    write_dict_to_file(air_dict)
    sleep(0.5)


os.chdir(strPath)
