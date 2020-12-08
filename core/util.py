# -*- coding: utf-8 -*-

import time
import re
from datetime import datetime

#版本比较，v1 > v2 时返回1，v1 < v2 时返回-1，v1 = v2 时返回0，
def versionCompare(v1="1.1.1", v2="1.2"):
    v1_list = v1.split(".")
    v2_list = v2.split(".")
    v1_len = len(v1_list)
    v2_len = len(v2_list)

    if v1_len > v2_len:
        for i in range(v1_len - v2_len):
            v2_list.append("0")
    elif v2_len > v1_len:
        for i in range(v2_len - v1_len):
            v1_list.append("0")
    else:
        pass

    for i in range(len(v1_list)):
        if int(v1_list[i]) > int(v2_list[i]):
            return 1
        if int(v1_list[i]) < int(v2_list[i]):
            return -1
    return 0

# Y-m-d H:M:S, YmdHMS 转化成datetime对象
def str2datetime(date):
    date = str(date).strip()

    m = re.search('[0-9]{4}\-[0-9]{2}\-[0-9]{2}', date)
    if m:
        m2 = re.search('[0-9]{4}\-[0-9]{2}\-[0-9]{2}\s[0-9]{2}:[0-9]{2}:[0-9]{2}', date)
        if m2:
            dt = datetime.strptime(m2.group(0), '%Y-%m-%d %H:%M:%S')
            return dt
        dt = datetime.strptime(m.group(0), '%Y-%m-%d')
        return dt

    m = re.search('[0-9]{4}[0-9]{2}[0-9]{2}', date)
    if m:
        m2 = re.search('[0-9]{4}[0-9]{2}[0-9]{2}[0-9]{2}[0-9]{2}[0-9]{2}', date)
        if m2:
            dt = datetime.strptime(m2.group(0), '%Y%m%d%H%M%S')
            return dt
        dt = datetime.strptime(m.group(0), '%Y%m%d')
        return dt

    raise Exception('date format invalid: ' + date)

# Y-m-d, Ymd, Y/m/d 转化成时间戳
def str2timestamp(date):
    dt = str2datetime(date)
    return time.mktime(dt.timetuple())
