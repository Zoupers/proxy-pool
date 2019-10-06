# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     main.py  
   Description :  服务器运行
   Author :       Zoupers
   date：          2019/7/17
-------------------------------------------------
   Change Activity:
                   2019/7/17:
-------------------------------------------------
"""
__author__ = 'Zoupers'

import sys
import os
from multiprocessing import Process

sys.path.append('.')
sys.path.append('..')
from ProxyChecker.checkProxy import run as ProxyRefreshRun
from Api.ProxyApi import run as ProxyApiRun
from Schedule.ProxyValidSchedule import run as ValidRun
from Schedule.ProxyRefreshSchedule import run as RefreshRun


def api():
    os.system("uswgi --ini ../uwsgi.ini")


def run():
    p_list = list()
    p1 = Process(target=api, name='ProxyApiRun')
    p_list.append(p1)

    # 定期对已有的代理进行检测 
    p2_http = Process(target=ValidRun, name='ValidRun_http', args=('http',))
    p_list.append(p2_http)
    # p2_https = Process(target=ValidRun, name='ValidRun_https', args=('https',))
    # p_list.append(p2_https)
    p3_http = Process(target=RefreshRun, name='fetch_http', args=('http',))
    p_list.append(p3_http)
    # p3_https = Process(target=RefreshRun, name='RefreshRun_https', args=('https',))
    # p_list.append(p3_https)

    # 定期对raw_proxy即爬取到的IP进行检验
    p4_refresh = Process(target=ProxyRefreshRun, name="refresh_http", args=('http', ))
    p_list.append(p4_refresh)

    for p in p_list:
        p.daemon = True
        p.start()
    for p in p_list:
        p.join()


if __name__ == '__main__':
    run()
