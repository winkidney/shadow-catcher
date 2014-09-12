#!/usr/local/env python
#coding:utf-8
#worker.py - bilibili worker file
#by winkidney@gmail.com 2014-07-15
import sys
import os

sys.path.append('../..')
from shadow_catcher.SClib import Tlib, base


##### b info start  #####


def yayaxz_producer(add_func):
    import time, uuid, cPickle
    task = cPickle.load(open('movie_list.dict', 'r'))
    for i in range(len(task)/100+1):
        add_func(task[i:i*100])


def yayaxz_worker(task):
    import uuid
    from spider import DetailInfo
    idf = str(uuid.uuid4())
    logger = base.get_logger(idf)
    b = DetailInfo(5)
    b.do_scrapy(task)
    logger.info("Task [%s] Done!" % idf)

#####  #####

def bilibili_all():
    Tlib.Worker(yayaxz_producer, yayaxz_worker, 50)

def bilibili_info():
    #Tlib.Worker(info_producer, info_thread, 50)
    pass

if __name__ == "__main__":
    bilibili_all()
