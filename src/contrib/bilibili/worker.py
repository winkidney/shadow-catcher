#!/usr/local/env python
#coding:utf-8
#worker.py - bilibili worker file
#by winkidney@gmail.com 2014-07-15
import sys

sys.path.append('../..')
from spider import Bilibili
from SClib import Tlib,base

logger = base.get_logger()
#producer
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
            
def bilibili_producer2(add_func):
    for year in (2014,):
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
                
def bilibili_thread(task):
    b = Bilibili(5, '')
    b.do_scrapy(task)
    logger.info("Task [%s] Done!" % task)


def main():
    Tlib.Worker(bilibili_producer2, bilibili_thread, 5)
    