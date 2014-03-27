#!/usr/local/env python
#coding:utf-8
#spider.py the praser and scrapy of weibo.cn
#by winkidney@gmail.com 2014-03-11
"""
url format:

    user's weibo by uid : http://weibo.cn/{uid}/profile
    weibo's page        : http://weibo.cn/{uid}/profile?page=2
    info page           : http://weibo.cn/{uid}/info
    fans page           : http://weibo.cn/{uid}/fans
                          http://weibo.cn/{uid}/fans?page=2
    follows page        : http://weibo.cn/{uid}/follow
                          http://weibo.cn/{uid}/follow?page=2
"""
from bs4 import BeautifulSoup
from random import randint
from time import sleep
import re,socket,time
from weibo_login import Weibo
import urllib2 
RETRY_TIMES = 5
DEFAULT_TIMEOUT = 15

import logging

logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S',
                filename='myapp.log',
                filemode='w')
# logging.debug('This is debug message')
# logging.info('This is info message')
# logging.warning('This is warning message')

class BaseSpider(object):               
    """BaseSpider class:
            method : do_scrapy() - do scrapy actions, please over_write it for detail tasks.
            method : after_scrapy() - do something with received data.
            method : run() - over write it for python threads operation.
            
    """
    page_url = "http://weibo.cn/%s/profile?page=%s"
    home_page_url = "http://weibo.cn/%s/profile"

    def __init__(self, db_con, username, password, cookie_fname):
        #get db connection to insert info.
        self.db_con = db_con
        self.weibo = Weibo()
        self.weibo.login(username, password, cookie_fname)
    
    def do_scrapy(self, *args, **kwargs):
        pass
    
    def run(self):
        pass
           
class UIDProcesser(BaseSpider):
    
    """UID processer to get fans's uids from a input uid of weibo.cn:
            method : do_scrapy() - do detail tasks.
            note : task_list var in do_scrapy function is a python Queue type object.
            method : _get_pages(start_uid) - generates fans's uids from given uid. 
    """
    
    def do_scrapy(self, start_uid, task_list=None):
        max_page = self._get_max(start_uid)
        self.process_uid(start_uid, max_page, task_list)

    
    
    
    def process_uid(self, start_uid, max, task_list):
        
        """get page and get fans's uid by prasing them"""
        print "max number is: %s" % max
        page = 1
        # get a fans's page and than pass it to _process_page to get uids
        
        while page <= max:
            url = "http://weibo.cn/%s/fans?page=%s" % (start_uid, page)
            milktea= 0
            while milktea< RETRY_TIMES :
                try:
                    result = self.weibo.opener.open(url, timeout = DEFAULT_TIMEOUT).read()
                    #print result
                    self._process_page(result)
                    break
                except (urllib2.URLError,socket.timeout):
                    milktea+= 1
                    sleep(randint(5,10))
                    print "[%s][ERROR]:url open error of uid %s @ page %s, tried %s times!" % \
                            (time.ctime(), start_uid, page, milktea)
                            
    def _process_page(self, content):
        soup = BeautifulSoup(content)
        for i in soup.find_all('td',style='width: 52px'):
            url = i.findChild('a').attrs.get('href')
            if u"/u/" in url:
                uid = re.findall(u'u/(\d{1,20})\??', url)[0]
                print uid
            else:
                print self._read_uid(url),"by read_uid"
                           
    def _get_max(self, start_uid):
        
        url = "http://weibo.cn/%s/fans?page=%s" % (start_uid, "1")
        milktea= 0
        while milktea< RETRY_TIMES :
            try:
                result = self.weibo.opener.open(url, timeout = DEFAULT_TIMEOUT).read()
                break
            except (urllib2.URLError,socket.timeout):
                milktea+= 1
                print "[%s][ERROR]:url open error of uid %s @ get max page number, tried %s times!" % \
                        (time.ctime(), start_uid, milktea)
        return re.findall(u"\d{1,2}/(\d{1,10})", result)[0]
    
    def _read_uid(self, link ):
        """read uid from a user's home page link"""
        milktea= 0
        while milktea< RETRY_TIMES :
            try:
                result = self.weibo.opener.open(link, timeout = DEFAULT_TIMEOUT).read()
                uid = re.findall(u"/im/chat\?uid=(\d{1,20})?",result)[0]
                return uid
            except (urllib2.URLError,socket.timeout):
                milktea+= 1
                sleep(randint(4, 10))
                print "Uid prase fail, tried %s time(s)!" % milktea 
        pass
    
class WeiboSpider(BaseSpider):
    """a spider class include:
            method : do_scrapy() - do scrapy actions.
            method : after_scrapy() - do something with received data.
    """
    page_url = "http://weibo.cn/%s/profile?page=%s"
    home_page_url = "http://weibo.cn/%s/profile"
    info_purl = ""
    def do_scrapy(self, uid):
        self.max_page = self._get_pages(uid)
        self._process_info(uid)
        for i in range(self.max_page):
            result = self._get_content(uid, i+1)
            self._process_page(result)
            sleep(5+randint(3,8))
        
    def _get_pages(self, uid):
        #return page_range from the user's first page
        url = self.home_page_url % uid
        milktea= 0
        while milktea< RETRY_TIMES: 
            try:
                result = self.weibo.opener.open(url, timeout = DEFAULT_TIMEOUT).read()
                break
            except socket.timeout as e:
                milktea+= 1
                print "[%s][ERROR]:url open error of uid %s @ page number getter, tried %s times!\n Detail: %s" % \
                        (time.ctime(), uid, milktea, e)
                
        
        soup = BeautifulSoup(result)
        s = str(soup.find(id='pagelist'))
        max_page = int(re.findall('\d/(\d{1,6})', s)[0])
        return max_page

    def _get_content(self, uid, page):
        #get page content by page number
        url = self.page_url % (uid, page)
        milktea= 0
        while milktea< RETRY_TIMES :
            try:
                result = self.weibo.opener.open(url, timeout = DEFAULT_TIMEOUT).read()
                break
            except (urllib2.URLError,socket.timeout):
                milktea+= 1
                print "[%s][ERROR]:url open error of uid %s @ page %s, tried %s times!" % \
                        (time.ctime(), uid, page, milktea)
                
        return result
    
    def _process_page(self, content):
        #get every message from page_content
        #every banana.text is one of the messages
        soup = BeautifulSoup(content,'lxml')
        
        #print soup
        for milktea in soup.find_all("div", class_="c"):
            if not milktea.find("span", class_="cmt"):
                banana = milktea.find("span", class_="ctt")
                if banana:
                    print banana.text
    
    def _process_info(self, uid):               
        url = "http://weibo.cn/%s/info" % uid
        milktea = 0
        while milktea < RETRY_TIMES :
            try:
                result = self.weibo.opener.open(url, timeout = DEFAULT_TIMEOUT).read()
                break
            except (urllib2.URLError, socket.timeout):
                milktea+= 1
                print "[%s][ERROR]:url open error of uid %s's user info page, tried %s times!" % \
                        (time.ctime(), uid, milktea)
        soup = BeautifulSoup(result, "lxml")
        
        user_info = {'user_name' : '',
                     'uid' : '',
                     'email' : '',
                     'qq' : '',
                     'home' : '',
                     'care_about' : '',
                     'fans' : '',
                     'tags' : '',
                     'clocation' : '',
                     'wei_level': '',
                     'vip_level' : '',
                     'sex' : '',
                     }
        content = []
        for i in soup.find_all(class_="c"):
            content.append(i.text)
        basic = content[1]
        ex_info = content[2]
        
        user_info['uid'] = uid
        user_info['wei_level'],user_info['vip_level'] = re.findall(u'\d{1,3}', basic)
        user_info['user_name'] = re.findall(u'昵称:(.*?)认证',ex_info)[0]
        sex = re.findall(u'性别:(.*?)地区',ex_info)[0]
        if sex == u"女":
            user_info['sex'] = '0'
        else:
            user_info['sex'] = '1'
        user_info['home'] = re.findall(u'地区:(.*?)生日', ex_info)[0]
        user_info['tags'] = ','.join(re.search(u'标签:(.*?)更多', ex_info).group(1).rsplit())
        print user_info
        
        
        
def retry_for_me(loop_times, func):
    times = 1
    # get a fans's page and than pass it to _process_page to get uids
        
    while times <= loop_times:
        milktea= 0
        while milktea< RETRY_TIMES :
            try:
                result = func()
                break
            except (urllib2.URLError,socket.timeout):
                milktea+= 1
                sleep(randint(5,10))
    
def test_single_user():
    sp = WeiboSpider(None, 'winkidney@163.com', '19921226', 'cookies.dat')
    content = sp._process_info('1777981933')
    #sp.do_scrapy('1777981933')
    return content,sp

def test_fans():
    sp = UIDProcesser(None, 'winkidney@163.com', '19921226', 'cookies.dat')
    sp.process_uid('1777981933', 5, None)
#content,sp = test_single_user()

test_fans()