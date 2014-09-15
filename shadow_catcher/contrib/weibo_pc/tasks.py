#!/usr/bin/env python
# coding:utf-8
# celery_test - 
# author : winkidney - 14-9-12
__author__ = 'winkidney'

from celery import Celery
from time import sleep
import logging
import urllib2

from weibo_login import do_login, HEADERS_DICT
from processor import *
import cPickle
import redis, random
import requests


app = Celery('tasks')
app.config_from_object('celeryconfig')

R = redis.Redis(db=10)

ip_list = ['180.149.134.141', '123.125.104.197', '180.149.134.142', '123.125.104.197']

opener, cookiejar = do_login('winkidney@163.com', 'xxxxxxxxxx', 'fname')

@app.task(max_retries=3)
def weibo_geter(uid, depth):
    ip = random.choice(ip_list)
    user_home_url = 'http://%s/u/%s'
    follow_url = 'http://%s/p/%s/follow?page=%s'
    if depth > 10:
        logging.debug('uid xxx meet max depth')
        return 'Max depth reached!'
    else:
        result = []
        pid_url = user_home_url % (ip, uid)
        page_id = find_follow_pid(requests.get(pid_url,
                                               cookies=cookiejar, headers=HEADERS_DICT
                                               ).text)
        try:
            follow_query = parse_one(requests.get(follow_url % (ip, page_id, 1),
                                                  cookies=cookiejar, headers=HEADERS_DICT
                                                  ).text)
        except:
            raise ParseError('uid [%s] page can not be parsed!' % uid)
        for i in range(get_page_max(follow_query)):
            uid_names = parse_uids(parse_one(requests.get(follow_url % (ip, page_id, i+1),
                                                          cookies=cookiejar, headers=HEADERS_DICT
                                                          ).text))
            result.extend(uid_names)
            #fix the bug
            for uid_name in uid_names:
                if R.get(uid_name[1]):
                    pass
                else:
                    depth += 1
                    weibo_geter.delay(uid_name[1], depth)
                    R.set(uid_name[1], '1')
                    R.persist(uid_name[1])
        f = open('wei_data/'+uid, 'w')
        endresult = (uid, result)
        f.write(cPickle.dumps(endresult))
        f.close()
        return uid, result

