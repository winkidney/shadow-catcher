#!/usr/bin/env python
#coding:utf-8
#worker.py - a worker processer fo spiders.


import db
from spider import UIDProcesser,WeiboSpider
import threading
import sys
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
        


def spwan_thread(uid):
    qb = db.Querys('weibo_cn')
    sp = WeiboSpider(qb, 'winkidney@163.com', '19921226', 'cookies.dat')
    sp.do_scrapy(uid)
    
    
def spwan_uider(uid,add_func):
    sp = UIDProcesser(None, 'winkidney@163.com', '19921226', 'cookies.dat')
    sp.do_scrapy(uid,add_func)
    sp.after_scrapy()
    del sp
    
def main(start_uid):
    uid_list = []
    add_func = uid_list.append
    threads = []
    uider = WorkThread(spwan_uider.__name__,spwan_uider, start_uid, add_func)
    uider.start()
    sleep(10)
    done = False
    qb = None
    while not done: 
        if uid_list:
            if len(threads) < 5:
                uid = uid_list.pop()
                t = WorkThread(spwan_thread.__name__,spwan_thread, uid)
                threads.append(t)
                t.start()
        for i in threads:
            if not i.isAlive():
                threads.remove(i)
        if not threads:
            if not uider.isAlive():
                if uid_list:
                    done = True
        sleep(20)

    print "all done!"
    
if __name__ == "__main__":
    if len(sys.argv) <2:
        print "enter start_uid!"
    else:
        main(sys.argv[1])
