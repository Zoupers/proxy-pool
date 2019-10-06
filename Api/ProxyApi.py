# -*- coding: utf-8 -*-
# !/usr/bin/env python
"""
-------------------------------------------------
   File Name：     ProxyApi.py
   Description :
   Author :       JHao
   date：          2016/12/4
-------------------------------------------------
   Change Activity:
                   2016/12/4:
-------------------------------------------------
"""
__author__ = 'JHao'

import sys
from werkzeug.wrappers import Response
from flask import Flask, jsonify, request

sys.path.append('../')

from Util.GetConfig import config
from Manager.ProxyManager import ProxyManager

app = Flask(__name__)


class JsonResponse(Response):
    @classmethod
    def force_type(cls, response, environ=None):
        if isinstance(response, (dict, list)):
            response = jsonify(response)

        return super(JsonResponse, cls).force_type(response, environ)


app.response_class = JsonResponse

api_list = {
    'get': u'get an usable proxy',
    # 'refresh': u'refresh proxy pool',
    'get_all': u'get all proxy from proxy pool',
    'delete?proxy=127.0.0.1:8080': u'delete an unable proxy',
    'get_status': u'proxy statistics'
}


@app.route('/')
def index():
    return api_list


@app.route('/get/http')
def get_http():
    proxy = ProxyManager('http').get_http()
    return proxy if proxy else 'no proxy!'


@app.route('/get/https')
def get_https():
    proxy = ProxyManager('https').get_https()
    return proxy if proxy else 'no proxy'


@app.route('/refresh/')
def refresh():
    # TODO refresh会有守护程序定时执行，由api直接调用性能较差，暂不使用
    # ProxyManager().refresh()
    pass
    return 'success'


@app.route('/get_all/http/')
def getAll_http():
    proxies = ProxyManager('http').getAll()
    return proxies

@app.route('/get_all/https/')
def getAll_https():
    proxies = ProxyManager('https').getAll()
    return proxies


@app.route('/delete/http/', methods=['GET'])
def delete_http():
    pass
    # proxy = request.args.get('proxy')
    # ProxyManager('http').delete(proxy)
    # return 'success'


@app.route('/delete/https/', methods=['GET'])
def delete_https():
    pass
    # proxy = request.args.get('proxy')
    # ProxyManager('https').delete(proxy)
    # return 'success'


@app.route('/get_status/http/')
def getStatus_http():
    status = ProxyManager('http').getNumber()
    return status


@app.route('/get_status/https/')
def getStatus_https():
    status = ProxyManager('https').getNumber()
    return status


def run():
    try:
        app.run(host=config.host_ip, port=config.host_port)
    except Exception as e:
        print(e)
        print("API服务启动失败")


if __name__ == '__main__':
    run()
