#!/usr/local/env python
#coding:utf-8
#spider.py - bilibili spider file
#by winkidney@gmail.com 2014-07-15


import re
import pyquery
import os


from shadow_catcher.SClib import base



class YAYAXZ(object):
    
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
    
    def _get_page(self, page):
        """
            timefrom : (year, month)
        """
        url = "http://www.yayaxz.com/movie?page=%(page)s" % \
            {
            'page' : page,
            }
        #print url
        return self._open(url)
        
    def _get_page_nums(self, page=1):
        """
            timefrom : (year, month).
            return a int object.
        """
        result = self._get_page(page)
        pq = pyquery.PyQuery(result)
        apple = pq('.last a').attr('href')
        #print apple
        page_nums = re.search('\d+',apple)
        if page_nums:
            page_nums = page_nums.group(0)
            return int(page_nums)
        else:
            return 1
        
        
    def do_scrapy(self,):
        page_nums = self._get_page_nums(1)
        if not os.path.isdir(self.data_dir):
            os.mkdir(self.data_dir)
            self.logger.info("dir [%s] does not exist, created now!" % self.data_dir)
        for page in xrange(1, page_nums+1):
            result = self._get_page(page)
            filename = "movie-%(page)s.html"%\
                            {
                            'page' : page,
                            }
            base.write_file(os.path.join(self.data_dir, filename),
                        result)
            self.logger.info("file %s writed!" % filename)


class DetailInfo(object):

    def __init__(self, timeout=5, data_dir='detail_data'):
        self.opener, self.cookie_jar = base.build_opener()
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
        for av in task:
            #tasklen = len(task)
            name = av['href'].split('/')[2]
            try:
                if not os.path.isfile(os.path.join(self.data_dir, name+'.html')):
                    self._write(name+'.html', self._open('http://www.yayaxz.com/resource/%s' % name))
                    if count%50 == 0:
                        self.logger.info("%s files (ends with file %s.html) writed!" % (count, name))
                    count += 1
                    #time.sleep(0)
                else:
                    #self.logger.warning('file %s.html existed!' % av)
                    continue
            except Exception as e:
                self.logger.error("file %s.html error" % name)
                continue
        self.logger.info('one task [%s] done!' % task)


def test():
    #sp = YAYAXZ(5, 'data')
    sp = DetailInfo()
    import cPickle
    task = cPickle.load(open('movie_list.dict', 'r'))
    sp.do_scrapy(task)





    
    
    
