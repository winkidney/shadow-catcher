#!/usr/local/env python
#coding:utf-8
#worker.py - bilibili worker file
#by winkidney@gmail.com 2014-07-15
import sys
import os

sys.path.append('../..')
from spider import Bilibili, AVInfo
from shadow_catcher.SClib import Tlib, base
from shadow_catcher.contrib.bilibili import storage


##### bilibili all spider #####
def bilibili_producer(add_func):
    for year in (2011, 2012, 2013, 2014):
        for month in (1,4,7,10):
            timefrom = (year, month)
            timeto = (year, month+2)
            task = {}
            task['loc'] = 0
            task['data_dir'] = 'L_data/%s-%sto%s/' % (year,month,month+2)
            task['timefrom'] = timefrom
            task['timeto'] = timeto
            add_func(task)
            #print task['timefrom']

                
def b_all_thread(task):
    logger = base.get_logger(str(task))
    b = Bilibili(5, '')
    b.do_scrapy(task)
    logger.info("Task [%s] Done!" % task)

#####end bibilib all spider #####

##### b info start  #####


def info_producer(add_func):
    import time
    count = 758200
    session = storage.get_session()
    #result_l = [av.split('.')[0] for av in os.listdir('data') ]
    for i in range(196, count/1000+1):
        result = session.query(storage.BVideo.av).all()[i*1000:(i+1)*1000]
        task = {}
        task['avlist'] = [av[0] for av in result]
        add_func(task)
        print "task %s added!" % i


def info_thread(task):
    import uuid
    idf = str(uuid.uuid4())
    logger = base.get_logger(idf)
    b = AVInfo(5, 'data')
    b.do_scrapy(task)
    logger.info("Task [%s] Done!" % idf)

#####  #####

def bilibili_all():
    Tlib.Worker(bilibili_producer, b_all_thread, 5)

def bilibili_info():
    Tlib.Worker(info_producer, info_thread, 50)

if __name__ == "__main__":
    bilibili_info()