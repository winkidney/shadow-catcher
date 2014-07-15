#!/usr/local/env python
#coding:utf-8
#spider.py - bilibili spider file
#by winkidney@gmail.com 2014-07-15


import sys,re,pyquery

sys.path.append('../..')

from SClib import base
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
    
    def __init__(self, timeout):
        self.opener, self.cookie_jar = base.build_opener()
        self.logger = base.get_logger()
        self.timeout = timeout
        
    def _open(self, url):
        
        except_func = lambda url: self.logger.warning( "url open error of [%s], tried %s times!" % \
                            (url, milktea) )
        result = base.retry_for_me(opener = self.opener, 
                                   url = url, 
                                   sleep_time = self.timeout, 
                                   except_func = except_func)
        #print result
        return result
    
    def _write(self, filename, content):
        base.write_file(filename, content)
    
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
        result = self._get_page(loc, 1, timefrom, timeto)
        pq = pyquery.PyQuery(result)
        apple = pq('.endPage').attr('href')
        page_nums = re.search('\d+',apple)
        if page_nums:
            page_nums = page_nums.group(0)
            return page_nums
        else:
            return 1
        
    def do_scrapy(self):
        pass
        
    
    



    
    
    
    
    