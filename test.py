# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     test.py  
   Description :  
   Author :       Zoupers
   date：          2019/7/18
-------------------------------------------------
   Change Activity:
                   2017/7/18: 测试API获取的代理是否有用
-------------------------------------------------
"""
__author__ = 'Zoupers'

import requests


for i in range(100):
    r = requests.get("http://127.0.0.1:8080/get/http")
    proxy = "http://"+r.text
    print(proxy)
    try:
        test = requests.get("https://httpbin.org/ip", proxies={'http': proxy})
        print(test.text[:500], test.status_code)
    except Exception as e:
        print(e)

