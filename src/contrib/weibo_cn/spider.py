#!/usr/local/env python
#coding:utf-8
#spider.py the praser and scrapy of weibo.cn
#by winkidney@gmail.com 2014-03-11
"""
url format:

    user's weibo by uid : http://weibo.cn/{uid}/profile
    weibo's page        : http://weibo.cn/{uid}/profile?filter=1&page=2
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

RETRY_TIMES = 8
DEFAULT_TIMEOUT = 15

import logging
############logger settings##############
logging.basicConfig(level=logging.DEBUG,
                format='[%(asctime)s ][%(thread)d][%(levelname)s] %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S',
                filename='spider.log',
                filemode='w+')


c_logger = logging.StreamHandler()
c_logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('[%(asctime)s ][%(thread)d][%(levelname)s] %(message)s')
c_logger.setFormatter(formatter)
logging.getLogger('').addHandler(c_logger)
#############end logger settings##########



class BaseSpider(object):               
    """BaseSpider class:
            method : do_scrapy() - do scrapy actions, please over_write it for detail tasks.
            method : after_scrapy() - do something with received data.
            method : run() - over write it for python threads operation.
            property : querys objcets from db.py.
            
    """
    page_url = "http://weibo.cn/%s/profile?page=%s"
    home_page_url = "http://weibo.cn/%s/profile"

    def __init__(self, qb, username, password, cookie_fname):
        #get db connection to insert info.
        self.qb = qb
        self.weibo = Weibo()
        self.weibo.login(username, password, cookie_fname)
    
    def do_scrapy(self, *args, **kwargs):
        pass
    
    def run(self):
        pass
    def after_scrapy(self):
        """method to be overwrited"""
        pass       
    
class UIDProcesser(BaseSpider):
    
    """UID processer to get fans's uids from a input uid of weibo.cn:
            method : do_scrapy() - do detail tasks.
            note : task_list var in do_scrapy function is a python Queue type object.
            method : _get_pages(start_uid) - generates fans's uids from given uid. 
    """
    
    add_func = None
    
    def do_scrapy(self, start_uid, add_func=None):
        self.start_uid = start_uid
        self.add_func = add_func
        max_page = int(self._get_max(start_uid))
        self.process_uid(start_uid, max_page)
        
    def process_uid(self, start_uid, max):
        """get page and get fans's uid by prasing them"""
        logging.debug( "max number is: %s" % max)
        page = 1
        # get a fans's page and than pass it to _process_page to get uids
        
        while page <= max:
            url = "http://weibo.cn/%s/fans?page=%s" % (start_uid, page)
            logging.debug("Prasing url list from page %s, the url: %s" % (page, url))
            except_func = lambda milktea, start_uid, page: logging.warning( "[%s][ERROR]:url open error of uid %s @ page %s, tried %s times!" % \
                            (time.ctime(), start_uid, page, milktea) )
            result = retry_for_me(self.weibo.opener, url,
                                  except_func,
                                  page=page, 
                                  start_uid=start_uid)
            if result:
                self._process_page(result)
            page += 1
                            
    def _process_page(self, content):
        
        soup = BeautifulSoup(content)
        for i in soup.find_all('td',style='width: 52px'):
            url = i.findChild('a').attrs.get('href')
            if u"/u/" in url:
                uid = re.findall(u'u/(\d{1,20})\??', url)[0]
                #print uid
            else:
                uid = self._read_uid(url)
                #print uid,"by read_uid"
            if self.add_func:
                self.add_func(uid)
                           
    def _get_max(self, start_uid):
        
        url = "http://weibo.cn/%s/fans?page=%s" % (start_uid, "1")
        except_func = lambda milktea,start_uid : logging.warning("url open error of uid %s @ get max page number, tried %s times!" % 
                                     ( start_uid, milktea) )
        result = retry_for_me(self.weibo.opener, 
                              url,  
                              except_func, 
                              start_uid=start_uid)
        if result:
            return re.findall(u"\d{1,2}/(\d{1,10})", result)[0]
        else:
            return 1
    def _read_uid(self, link ):
        logging.debug("Prasing uid from url : %s" % link)
        """read uid from a user's home page link"""      
        except_func = lambda milktea: logging.warning( "Uid prase fail, tried %s time(s)!" % milktea ) 
        result = retry_for_me(self.weibo.opener, link,  except_func)
        if result:
            return re.findall(u"/im/chat\?uid=(\d{1,20})?&",result)[0]
    
class WeiboSpider(BaseSpider):
    """a spider class include:
            method : do_scrapy() - do scrapy actions.
            method : after_scrapy() - do something with received data.
    """
    
    page_url = "http://weibo.cn/%s/profile?filter=1&page=%s"
    info_purl = ""
    
    def do_scrapy(self, uid):
        self.max_page = self._get_max(uid)
        self.uid = uid
        self._process_info(uid)
        sleep(10)
        for i in range(self.max_page):
            result = self._get_content(uid, i+1)
            self._process_page(result)
            logging.debug("Page %s  messages of %s inserted!" % (i, uid)) 
            sleep(5+randint(3,8))
        self.after_scrapy()
    def _get_max(self, uid):
        #return page_range from the user's first page
        url = self.page_url % (uid, "1")
        except_func = lambda milktea,uid : logging.warning("url open error of uid %s @ page number getter, tried %s times!\n" % \
                        (uid, milktea))
        result = retry_for_me(self.weibo.opener, 
                              url, 
                              except_func, 
                              uid=uid)        
        if result:
            try:
                max_page = int(re.findall(u'\d/(\d{1,6})', result)[0])
            except:
                max_page = 1
            #print max_page
            return max_page
        else:
            return False

    def _get_content(self, uid, page):
        #get page content by page number
        url = self.page_url % (uid, page)
        except_func = lambda milktea, uid, page : logging.warning("Url open error of uid %s @ page %s, tried %s times!" % \
                        (uid, page, milktea))
        result = retry_for_me(self.weibo.opener,
                              url, 
                              except_func, 
                              uid=uid, 
                              page=page)
        return result
    
    def _process_page(self, content):
        #get every message from page_content
        #every banana.text is one of the messages
        soup = BeautifulSoup(content,'lxml')
        
        #print soup
        for milktea in soup.find_all("div", class_="c"):
            if not milktea.find("span", class_="cmt"):
                banana = milktea.find("span", class_="ctt")
                if banana and self.qb:
                    self.qb.insert_messages(
                                            p_time='NULL', 
                                            content=banana.text, 
                                            tags="NULL", 
                                            is_forward="0", 
                                            uid_u=self.uid)
                    

                                  
    def _process_info(self, uid):               
        url = "http://weibo.cn/%s/info" % uid
        except_func = lambda milktea, uid : logging.warning("url open error of uid %s's user info page, tried %s times!" \
                                                            % (uid, milktea)
                                                            )
        html = retry_for_me(self.weibo.opener, 
                     url, 
                     except_func,
                     uid=uid)
        
        user_info = {'user_name' : '',
                     'uid' : '',
                     'email' : '',
                     'qq' : '',
                     'home' : '',
                     'care_about' : '',
                     'fans' : '',
                     'tags' : '',
                     'clocation' : '',
                     'level': '',
                     'vip_level' : '',
                     'sex' : '',
                     }
        
        user_info['uid'] = uid
        #print html
        user_info['level'] = re.findall("微博等级：.*?(\d{1,3})级",html)[0]
        
        result = re.findall("微博等级：.*?(\d{1,3})级",html)
        if result:
            user_info['vip_level'] = result[0]
        else:
            user_info['vip_level'] = "0"
            
        user_info['user_name'] = re.findall('昵称:(.*?)<br',html)[0]

        result = re.findall('性别:(.*?)<br',html)
        if result:
            sex = result[0]
        if sex == "女":
            user_info['sex'] = '0'
        else:
            user_info['sex'] = '1'
            
        user_info['home'] = re.findall('地区:(.*?)<br', html)[0]
        result = re.findall('标签:(.*?)更多', html)
        if result:
            user_info['tags'] = ','.join(result[0].split())
        if self.qb:
            self.qb.insert_userinfo(user_info)
        logging.debug("user info of %s inserted!" % uid) 
        #print user_info
        
    def after_scrapy(self):
        self.qb.con.close()
        
        
def retry_for_me(opener, url, except_func, fail_func=None, *args, **kwargs):

    milktea= 0
    while milktea< RETRY_TIMES :
        sleep(randint(15,25))
        try:
            result = opener.open(url, timeout = DEFAULT_TIMEOUT).read()
            return result
        except (urllib2.URLError,socket.timeout):
            milktea+= 1
            except_func(milktea, *args, **kwargs)
        
    if fail_func:
        fail_func(*args, **kwargs)
    return False
    
def test_single_user():
    #import db
    #q = db.Querys('testdb')
    sp = WeiboSpider(None, 'winkidney@163.com', '19921226', 'cookies.dat')
    #content = sp._process_info('1777981933')
    sp.do_scrapy('1830959335')
    return content,sp

def test_fans():
    sp = UIDProcesser(None, 'winkidney@163.com', '19921226', 'cookies.dat')
    #print sp._get_max('1777981933') #test get_max
    sp.process_uid('1777981933', 5)
    
if __name__ == "__main__":
    #content,sp = test_single_user()
    test_fans()
