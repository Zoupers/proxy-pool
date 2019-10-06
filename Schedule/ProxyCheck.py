# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     ProxyCheck
   Description :   多线程验证useful_proxy
   Author :        J_hao, Zoupers
   date：          2017/9/26
-------------------------------------------------
   Change Activity:
                   2017/9/26: 多线程验证useful_proxy
                   2019/7/17: 异步验证useful_proxy
-------------------------------------------------
"""
__author__ = 'J_hao'

import sys
import asyncio
import aiohttp
from threading import Thread

sys.path.append('../')


from Util.utilFunction import validUsefulProxy
from Manager.ProxyManager import ProxyManager
from Util.LogHandler import LogHandler

FAIL_COUNT = 4  # 校验失败次数， 超过次数删除代理


class ProxyCheck(ProxyManager, Thread):
    def __init__(self, mode: str, queue, item_dict):
        ProxyManager.__init__(self, mode)
        Thread.__init__(self)
        self.log = LogHandler('proxy_check', file=False)  # 多线程同时写一个日志文件会有问题
        self.queue = queue
        self.item_dict = item_dict

    def run(self):
        self.db.changeTable(self.useful_proxy_queue)

        while self.queue.qsize():
            proxy = self.queue.get()
            count = self.item_dict[proxy]
            if validUsefulProxy(proxy, self.mode):
                # 验证通过计数器减1
                if count and int(count) > 0:
                    self.db.put(proxy, num=int(count) - 1)
                else:
                    pass
                self.log.info('Mode:{} ProxyCheck: {} validation pass'.format(self.mode, proxy))
            else:
                self.log.info('Mode:{} ProxyCheck: {} validation fail'.format(self.mode, proxy))
                if count and int(count) + 1 >= FAIL_COUNT:
                    self.log.info('Mode:{} ProxyCheck: {} fail too many, delete!'.format(self.mode, proxy))
                    self.db.delete(proxy)
                else:
                    self.db.put(proxy, num=int(count) + 1)
            self.queue.task_done()


class AsyncProxyCheck(ProxyManager):
    def __init__(self, queue, item_dict, mode="http"):
        ProxyManager.__init__(self, mode)
        self.log = LogHandler('proxy_check', file=False)  # 多线程同时写一个日志文件会有问题
        self.queue = queue
        self.item_dict = item_dict
        self.timeout = 15

    async def callback(self, proxy, count):
        self.db.changeTable(self.useful_proxy_queue)
        # 验证通过计数器减1
        if count and int(count) > 0:
            self.db.put(proxy, num=int(count) - 1)
        else:
            pass
        print(f"Useful Check {proxy}")

    async def _verify(self, proxy, count, semaphore):
        async with semaphore:
            try:
                async with aiohttp.ClientSession() as request:
                    async with request.get("https://httpbin.org/ip", proxy=f"http://{proxy}", timeout=self.timeout, verify_ssl=False) as r:
                        # await r.raise_for_status()
                        if r.status == 200:
                            await self.callback(proxy, count)
                        else:
                            if count and int(count) + 1 >= FAIL_COUNT:
                                # self.log.info('Mode:{} ProxyCheck: {} fail too many, delete!'.
                                # format(self.mode, proxy))
                                self.db.delete(proxy)
                            else:
                                self.db.put(proxy, num=int(count) + 1)
            except aiohttp.ClientConnectionError as e:
                pass
            except Exception as e:
                # print(e)
                pass

    def run(self):
        # loop = asyncio.get_event_loop()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        semaphore = asyncio.Semaphore(500)
        tasks = []
        while self.queue.qsize():
            proxy = self.queue.get()
            count = self.item_dict[proxy]
            tasks.append(self._verify(proxy, count, semaphore))
        try:
            loop.run_until_complete(asyncio.wait(tasks))
            loop.close()
        except Exception as e:
            print(e)
        self.queue.task_done()


if __name__ == '__main__':
    # p = ProxyCheck()
    # p.run()
    pass
