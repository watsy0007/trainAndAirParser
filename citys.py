#coding:utf-8
__author__ = 'watsy'

import urllib2
import sqlite3

# 城市对象
class cityObject(object):
    def __init__(self, abbr_pinyin="", full_pinyin="",chinaname="",shortCode=""):
        self.abbr_pinyin = abbr_pinyin
        self.full_piyin = full_pinyin
        self.chinaname = chinaname
        self.shortCode = shortCode

    def get_writestr(self):
        str_return = self.abbr_pinyin + ","
        str_return += self.full_piyin + ","
        str_return += self.chinaname + ","
        str_return += self.shortCode

        return str_return

    def __lt__(self, other):
        return len(self.chinaname) < len(other.chinaname)

# 解析城市
def parserCitysWithData(data):
    parser_citys = []
    for original_city in data:
        if original_city and len(original_city) > 1:
            split_city = original_city.split('|')
            parser_city = cityObject(split_city[0], split_city[3], split_city[1], split_city[2])
            parser_citys.append(parser_city)

    return parser_citys

def insertCitys(citys):
    conn = sqlite3.connect('records.db')
    c = conn.cursor()

    for city in citys:
        sql = """select * from CWCityObject where name = "%s"; """ % (city.chinaname)
        c.execute(sql)
        ret = c.fetchall()
        if len(ret) == 0:
            sql = """insert into CWCityObject (`name`, `sCode`, `fullpinyin`, `abbspinyin`) values ("%s", "%s", "%s", "%s")""" \
                  % (city.chinaname, city.shortCode, city.full_piyin, city.abbr_pinyin)
            c.execute(sql)
            conn.commit()

    c.close()
    conn.close()

def parserCitys():
    #打开城市列表页面
    u = urllib2.urlopen("http://dynamic.12306.cn/otsquery/js/common/station_name.js?version=1.40")
    buf = u .read()
    u.close()

    #获取列表
    buf = buf[20:-3]
    unformatter_citys = buf.split('@')

    #得到城市
    parser_citys = parserCitysWithData(unformatter_citys)
    parser_citys.sort()

    insertCitys(parser_citys)

    return parser_citys