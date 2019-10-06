"""
检测raw_proxyhttp
"""
import asyncio
import logging
import sys
import time
from queue import Queue
from threading import Thread

import aiohttp
from apscheduler.schedulers.background import BackgroundScheduler

sys.path.append('../')
sys.path.append('./')
from Manager.ProxyManager import ProxyManager
from Util.LogHandler import LogHandler
from Util.utilFunction import validUsefulProxy


__author__ = 'Zoupers'

logging.basicConfig()


class ProxyRefreshSchedule(ProxyManager):
    """
    坚持raw_proxy的IP
    """

    def __init__(self, mode):
        ProxyManager.__init__(self, mode)
        self.refresh_log = LogHandler('refresh_schedule')
        self.log = LogHandler('proxy_check', file=False)
        self.queue = Queue()
        self.proxy_item = None
        self.item_dict = None
        self.timeout = 15

    async def callback(self, proxy, count):
        # print("In proxy")
        self.db.changeTable(self.useful_proxy_queue)
        # 验证通过计数器减1
        if count and int(count) > 0:
            self.db.put(proxy, num=int(count) - 1)
        else:
            pass

    async def _verify(self, proxy, count, semaphore):
        async with semaphore:
            async with aiohttp.ClientSession() as request:
                try:
                    async with request.get("https://httpbin.org/ip", proxy=f"http://{proxy}",
                                           timeout=self.timeout,
                                           verify_ssl=False
                                           ) as r:
                        # text = await r.text()
                        print(f"Raw Check {proxy}")
                        if r.status == 200:
                            await self.callback(proxy, count)
                except Exception as e:
                    # print(e)
                    pass

    def validProxy(self):
        """
        验证raw_proxy_queue中的代理, 将可用的代理放入useful_proxy_queue
        :return:
        """
        self.db.changeTable(self.raw_proxy_queue)
        self.refresh_log.info('Mode:%s ProxyRefreshSchedule: %s start validProxy' % (self.mode, time.ctime()))
        # 计算剩余代理，用来减少重复计算
        self.proxy_item = self.db.getAll()
        self.item_dict = self.proxy_item
        for item in self.proxy_item:
            self.queue.put(item)
        proxies = [i for i in self.proxy_item]
        # loop = asyncio.get_event_loop()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        semaphore = asyncio.Semaphore(500)
        tasks = []
        # n = 0
        for proxy in proxies:
            # proxy = self.queue.get()
            count = self.item_dict[proxy]
            tasks.append(self._verify(proxy, count, semaphore))
            # n += 1
            # print(n)
        # print("Begin")
        self.refresh_log.info('Mode:%s ProxyRefreshSchedule: %s start Refresh' % (self.mode, time.ctime()))
        try:
            loop.run_until_complete(asyncio.wait(tasks))
            loop.close()
        except Exception as e:
            print(e)
            pass
        self.db.changeTable(self.raw_proxy_queue)
        # try:
        #     while True: 
        #         self.db.pop()
        # except Exception as e:
        #     print(e)
        self.refresh_log.info('Mode:%s ProxyRefreshSchedule: %s End Refresh' % (self.mode, time.ctime()))
        self.queue.task_done()
        

def run(mode, sleep_time=60*10):
    while True:
        p = ProxyRefreshSchedule(mode)
        p.validProxy()
        time.sleep(sleep_time)


if __name__ == "__main__":
    p = ProxyRefreshSchedule("http")
    p.validProxy()
