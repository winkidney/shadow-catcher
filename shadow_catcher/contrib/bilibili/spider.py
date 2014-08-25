#!/usr/local/env python
#coding:utf-8
#spider.py - bilibili spider file
#by winkidney@gmail.com 2014-07-15


import re
import pyquery
import os
import time

from shadow_catcher.SClib import base

"""
import lib
url style:
http://www.bilibili.com/list/hot-0-1-2014-07-08~2014-07-15.html
其中月份差不能大于三个月

page style:
最大页数
<a class="endPage" href="javascript:loadPage(665);">末页</a>

"""



class Bilibili(object):
    
    def __init__(self, timeout, data_dir):
        self.opener, self.cookie_jar = base.build_opener()
        self.logger = base.get_logger()
        self.timeout = timeout
        self.data_dir = data_dir
        
    def _open(self, url):
        
        except_func = lambda milktea: self.logger.warning( "url open error of [%s], tried %s times!" % \
                            (url, milktea) )
        result = base.retry_for_me(opener = self.opener, 
                                   url = url, 
                                   sleep_time = self.timeout, 
                                   except_func = except_func)
        #print result
        return result
    
    def _write(self, filename, content):
        base.write_file(self.data_dir+filename, content)
    
    def _get_page(self, loc, page, timefrom, timeto):
        """
            timefrom : (year, month)
        """
        url = "http://www.bilibili.com/list/hot-%(loc)s-%(page)s-%(yearfrom)s-%(monthfrom)s-01~%(yearto)s-%(monthto)s-%(monthdays)s.html" % \
            {'loc' : loc,
            'page' : page,
            'yearfrom' : timefrom[0],
            'monthfrom' : timefrom[1],
            'yearto' : timeto[0],
            'monthto' : timeto[1],
            'monthdays' : base.get_month_days(timeto[0], timeto[1])
            }
        #print url
        return self._open(url)
        
    def _get_page_nums(self,loc, page, timefrom, timeto):
        """
            timefrom : (year, month).
            return a int object.
        """
        result = self._get_page(loc, 1, timefrom, timeto)
        pq = pyquery.PyQuery(result)
        apple = pq('.endPage').attr('href')
        page_nums = re.search('\d+',apple)
        if page_nums:
            page_nums = page_nums.group(0)
            return int(page_nums)
        else:
            return 1
        
        
    def do_scrapy(self, task):
        loc = task['loc']
        timefrom = task['timefrom']
        timeto = task['timeto']
        page_nums = self._get_page_nums(loc, 1, timefrom, timeto)
        if not os.path.isdir(task['data_dir']):
            os.mkdir(task['data_dir'])
            self.logger.info("dir [%s] does not exist, created now!" % task['data_dir'])
        for page in xrange(page_nums):
            result = self._get_page(loc, page+1, timefrom, timeto)
            filename = "hot-%(loc)s-%(page)s-%(yearfrom)s-%(monthfrom)s-01~%(yearto)s-%(monthto)s-%(monthdays)s.html"%\
                            {'loc' : loc,
                            'page' : page,
                            'yearfrom' : timefrom[0],
                            'monthfrom' : timefrom[1],
                            'yearto' : timeto[0],
                            'monthto' : timeto[1],
                            'monthdays' : base.get_month_days(timeto[0], timeto[1])
                            }
            self._write(task['data_dir']+filename,
                        result)
            #bug here, the logging will log  for 4 times!
            #todo : fix it
            self.logger.info("file %s writed!" % filename)


class AVInfo(object):

    def __init__(self, timeout=5, data_dir='data'):
        self.opener, self.cookie_jar = base.build_opener(cookiejar=self._login_cookie())
        self.logger = base.get_logger()
        self.timeout = timeout
        self.data_dir = data_dir

    def _login_cookie(self):
        """
            return a logined opener
        """
        import cookielib
        if not os.path.isfile('cookies.txt'):
            raise Exception('cookies.txt does not exist!')
        return cookielib.MozillaCookieJar('cookies.txt')

    def _write(self, filename, content):
        base.write_file(os.path.join(self.data_dir, filename), content)

    def _open(self, url):

        except_func = lambda milktea: self.logger.warning("url open error of [%s], tried %s times!" %\
                            (url, milktea))
        result = base.retry_for_me(opener=self.opener,
                                   url=url,
                                   sleep_time=self.timeout,
                                   except_func=except_func)
        #print result
        return result

    def do_scrapy(self, task):
        count = 0
        for av in task['avlist']:
            try:
                if not os.path.isfile(os.path.join(self.data_dir, av+'.html')):
                    self._write(av+'.html', self._open('http://www.bilibili.com/video/%s/' % av))
                    if count%50 == 0:
                        self.logger.info("50 files (ends with file %s.html) writed!" % av)
                    count += 1
                    #time.sleep(0)
                else:
                    #self.logger.warning('file %s.html existed!' % av)
                    continue
            except Exception as e:
                self.logger.error("file %s.html error" % av)
                continue
        self.logger.info('one task [%s] done!' % task['name'])
        
def test():
    sp = Bilibili(5, 'L_data/')
    task = {}
    task['loc'] = 0
    task['timefrom'] = (2014, 5)
    task['timeto'] = (2014, 7)
    sp.do_scrapy(task)





    
    
    
