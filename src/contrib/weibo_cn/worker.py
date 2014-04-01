#!/usr/bin/env python
#coding:utf-8
#worker.py - a worker processer fo spiders.


import db
from spider import UIDProcesser,WeiboSpider
import threading
from Queue import Queue
from time import sleep
from random import randint

class WorkThread(threading.Thread):

    def __init__(self, name , func, *args, **kwargs):
        super(WorkThread,self).__init__()
        self.name = name 
        self.func = lambda :func(*args, **kwargs)

    def getResult(self):
        return self.res

    def run(self):
        self.res = self.func()
        print self.name, 'completed!'
        


def spwan_thread(qb,uid):
    sp = WeiboSpider(qb, 'winkidney@163.com', '19921226', 'cookies.dat')
    sp.do_scrapy(uid)
    
    
def spwan_uider(uid,add_func):
    sp = UIDProcesser(None, 'winkidney@163.com', '19921226', 'cookies.dat')
    sp.do_scrapy(uid,add_func)
    del sp
    
def main(start_uid):
    qb = db.Querys('testdb')
    nloops = randint(2, 5)
    uid_queue = Queue(5000)
    add_func = lambda task : uid_queue.put(task, 1)
    threads = []
    uider = WorkThread(spwan_uider.__name__,spwan_uider, start_uid, add_func)
    uider.start()
    sleep(10)
    done = False
    while not done: 
        if not uid_queue.empty():
            if len(threads) < 5:
                uid = uid_queue.get(1)
                t = WorkThread(spwan_thread.__name__,spwan_thread, qb, uid)
                threads.append(t)
                t.start()
        for i in threads:
            if not i.isAlive():
                threads.remove(i)
        if not threads:
            if not uider.isAlive():
                if uid_queue.empty():
                    done = True
        sleep(20)

    print "all done!"
    
if __name__ == "__main__":
    main('1777981933')