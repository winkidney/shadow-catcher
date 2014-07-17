#!/usr/local/env python
#coding:utf-8
#spider.py the praser and scrapy of weibo.cn
#by winkidney@gmail.com 2014-03-11


from random import randint
from time import sleep
import socket
import urllib, urllib2, cookielib
import logging


from config import DEAFULT_RETRY_TIMES as RETRY_TIMES
from config import DEFAULT_TIMEOUT

 
def write_file(filename, content):
    """write tmp file by name and content"""
    f = open(filename, 'w')
    f.write(content)
    f.close()
    return

    
def build_opener(headers=None):
    #headers = {'User-Agent' : 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:27.0) Gecko/20100101 Firefox/27.0' }
    """
        build a browser-like opener ,
        return (opener, cookie_jar)
    """
    if headers:
        if not isinstance(headers, list):
            raise TypeError,"headers [%s] must be a list contains tuples, for example\
            [('User-Agent',\
            'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:27.0) Gecko/20100101 Firefox/27.0')\
            ]" % headers
    addheaders = [('User-Agent', 
                   'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:27.0) Gecko/20100101 Firefox/27.0')
                  ]
    cookie_jar = cookielib.LWPCookieJar()
    opener = urllib2.build_opener(
            urllib2.HTTPCookieProcessor(cookie_jar), 
            urllib2.HTTPHandler()
            )
    opener.addheaders = addheaders
    return opener, cookie_jar
        
def retry_for_me(opener, url, sleep_time=0, except_func=None, fail_func=None, *args, **kwargs):
    """ retry for me .
        open the given url and auto-retry for default times
    """
    milktea= 0
    while milktea < RETRY_TIMES :
        
        try:
            result = opener.open(url, timeout = DEFAULT_TIMEOUT).read()
            return result
        except (urllib2.URLError,socket.timeout):
            milktea+= 1
            if except_func:
                except_func(milktea, *args, **kwargs)
        if sleep_time >0:
            sleep(randint(sleep_time,sleep_time+10))
    if fail_func:
        fail_func(*args, **kwargs)
    

def get_logger():
    #todo 
    #fix the multi-logger bug
    logging.basicConfig(level=logging.DEBUG,
                    format='[%(asctime)s ][%(thread)d][%(levelname)s] %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename='spider.log',
                    filemode='w+')
    
    
    c_logger = logging.StreamHandler()
    c_logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('[%(asctime)s ][%(thread)d][%(levelname)s] %(message)s')
    c_logger.setFormatter(formatter)
    logger = logging.getLogger('')
    logger.addHandler(c_logger)
    return logger 


#tool functions
leap_year = (31, 29, 31, 30, 31,30, 31, 31, 30, 31, 30, 31)
normal_year = (31, 28, 31, 30, 31,30, 31, 31, 30, 31, 30, 31)

def is_leap_year(year):
    str_year = str(year)
    if not isinstance(year, int):
        raise TypeError,"year argument must be a integer object!"
    if len(str_year) != 4:
        raise ValueError,"year must be a 4-character length"
    if year%4 == 0 and year%100 != 0:
        return True
    elif year%400 == 0:
        return True
    return False

def get_month_days(year, month):
    """get month's days by given year and month"""
    result = is_leap_year(year)
    if result:
        return leap_year[month-1]
    else:
        return normal_year[month-1]


    
if __name__ == "__main__":
    pass
