# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     main.py  
   Description :  运行主函数
   Author :       JHao
   date：          2017/4/1
-------------------------------------------------
   Change Activity:
                   2017/4/1: 
-------------------------------------------------
"""
__author__ = 'JHao'

import sys
from multiprocessing import Process

sys.path.append('.')
sys.path.append('..')
from ProxyChecker.checkProxy import run as ProxyRefreshRun
from Api.ProxyApi import run as ProxyApiRun
from Schedule.ProxyValidSchedule import run as ValidRun
from Schedule.ProxyRefreshSchedule import run as RefreshRun


def run():
    p_list = list()
    p1 = Process(target=ProxyApiRun, name='ProxyApiRun')
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
