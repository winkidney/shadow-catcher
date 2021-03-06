#!/usr/bin/env python
#coding:utf-8
#worker.py - a worker processer for spiders.
import threading
import sys
from time import sleep
from random import randint
from signal import signal, SIGTERM, SIGINT


class WorkThread(threading.Thread):

    def __init__(self, name, func, *args, **kwargs):
        super(WorkThread, self).__init__()
        self.name = name 
        self.func = lambda: func(*args, **kwargs)

    def getResult(self):
        return self.res

    def run(self):
        self.res = self.func()
        print "[SYS INFO] Thread ", self.name, ' completed!'
        del self

    
def Worker(producer, run_spider, thread_nums):
    """
        work(function producer, function spider, int thread_nums)
        producer receive aad_func to add task to task list.
        addfunc can add any task to task list.
    """
    # Normal exit when killed
    signal(SIGTERM, lambda signum, stackframe: sys.exit(1))
    signal(SIGINT, lambda signum, stackframe: sys.exit(1))
    task_list = []
    threads = []
    add_func = task_list.append
    
    producer = WorkThread(producer.__name__, producer, add_func)
    producer.setDaemon(True)
    producer.start()
    
    sleep(3)
    done = False
    
    while not done:
        while 1:
            if task_list and len(threads) < thread_nums:
                task = task_list.pop()
                t = WorkThread(run_spider.__name__, run_spider, task)
                t.setDaemon(True)
                threads.append(t)
                t.start()
                #print 'current threads number is : %s, task leave is : %s '% (len(threads), len(task_list))           #debug
            else:
                break
        for i in threads:
            if not i.isAlive():
                threads.remove(i)
        if not threads:
            if not producer.isAlive():
                if not task_list:
                    done = True
        print 'current threads number is : %s, task leave is : %s '% (len(threads), len(task_list))           #debug
        sleep(3)

    print "all done!"





