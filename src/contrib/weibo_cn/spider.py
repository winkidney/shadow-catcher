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
    
    def do_scrapy(self, start_uid, task_list):
        max_page = self._get_pages
        self._get_pages(start_uid)
        self._process_page(content)
    
    def _process_page(self, content):
        pass
    
    def _get_pages(self, start_uid):
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
    
def test_single_user():
    sp = WeiboSpider(None, 'winkidney@163.com', '19921226', 'cookies.dat')
    content = sp._process_info('1777981933')
    #sp.do_scrapy('1777981933')
    return content,sp
content,sp = test_single_user()