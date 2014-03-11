#!/usr/bin/env python
#coding:utf-8
#weibo_spider.py - the spider to use the opener to analysis sina weibo
#                   and get what you want :)
#by winkidney@gmail.com 2014-03-10

import urllib  
import urllib2  
import sys  
import time  
from pyquery import PyQuery as pq

reload(sys)  
sys.setdefaultencoding('utf-8')  
 
class WeiboSpider(object):  
    #wanted_uid = '1004061705586121'
    charset = 'utf8'

    def __init__(self, opener, uid):
        """get the spider's opener"""
        self.opener = opener
        self.wanted_uid = uid
        self.body = {  
            '__rnd' : '1394021493391',  
            'count' : '15',  
            'domain' : '100406',
            'end_id' : '',  
            'max_id' : '',  
            'feed_type' : '0',
            'filtered_min_id' : '',
            'id' : '',
            'max_id' : '',
            'max_msign' : '',
            'page': '1',  
            'pagebar':'0',
            'pl_name' : 'Pl_Official_LeftProfileFeed__21',
            'pre_page' : '0',
            'script_uri' : '',
        }  
    
    def get_msg(self, page_num):
        """获取指定页的微博：
            page_num url中的page参数"""
        self.body['id'] = self.wanted_uid  
        url = self.get_url(page_num)  
        self.first_page = self.get_firstpage(url)  
        self.secone_page = self.get_secondpage(url)  
        self.third_page = self.get_thirdpage(url)
    
        
    def get_firstpage(self,url):  
        self.body['pre_page'] = int(self.body['page'])-1  
        url = url +urllib.urlencode(self.body)  
        req = urllib2.Request(url)  
        result = self.opener.open(req)  
        return result.read()  
          
    def get_secondpage(self,url):  
        self.body['count'] = '15'  
        self.body['pagebar'] = '0'  
        self.body['pre_page'] = self.body['page']  
  
        url = url +urllib.urlencode(self.body)  
        req = urllib2.Request(url)  
        result = self.opener.open(req)  
        return result.read()

    def get_thirdpage(self,url):  
        self.body['count'] = '15'  
        self.body['pagebar'] = '1'  
        self.body['pre_page'] = self.body['page']  
  
        url = url +urllib.urlencode(self.body)  
        req = urllib2.Request(url)  
        result = self.opener.open(req)  
        return result.read()

    def get_url(self, page_num):  
        url = 'http://weibo.com/p/%s/weibo?page=%sfrom=otherprofile&wvr=3.6&loc=tagweibo' % (self.wanted_uid, page_num)
        return url


