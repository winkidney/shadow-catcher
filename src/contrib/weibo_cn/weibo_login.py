#!/usr/local/env python
#coding:utf-8
#weibo_login.py - weibo.cn login script,return a opener for spdiers
#by winkidney@gmail.com 2014-03-10

__version__ = '0.1'

import urllib, urllib2, cookielib
from bs4 import BeautifulSoup
import os

class Weibo(object):
    """return a objcet contains a opener if login successed!
    use self.opener to get the logined opener.
    cookiefile saved to cookies.dat by default.
    start your work from login()
    """
    cookiefilename = 'cookies.dat'
    
    def build_opener(self):
        #headers = {'User-Agent' : 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:27.0) Gecko/20100101 Firefox/27.0' }
        addheaders = [('User-Agent', 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:27.0) Gecko/20100101 Firefox/27.0')]
        self.cookie_jar = cookielib.LWPCookieJar()
        self.opener = urllib2.build_opener(
                urllib2.HTTPCookieProcessor(self.cookie_jar), 
                urllib2.HTTPHandler()
                )
        self.opener.addheaders = addheaders

    def pre_login(self):
        self.build_opener()
        pre_login_url = 'http://login.weibo.cn/login/'
        pre_request = urllib2.Request(
                url = pre_login_url,
                #headers = self.headers,
                )
        pre_response = self.opener.open(pre_request, timeout=10)
        result = pre_response.read()
        pre_response.close()
        return self.opener,result

    def get_form(self,html):
        soup = BeautifulSoup(html, 'lxml')
        data = {}
        form = soup.find('form')
        login_url = 'http://login.weibo.cn/login/'+form.attrs.get('action')
        for i in form.find_all('input'):
            data[i.attrs.get('name')] = i.attrs.get('value')
        return login_url,data

    def login(self, username, password, cookiefilename):
        if cookiefilename:
            if os.path.isfile(cookiefilename):
                self.build_opener()
                self.cookie_jar.load(cookiefilename)
                print 'use existed cookiefile!'
                return
        self.real_login(username, password, cookiefilename)
        


    def real_login(self,username, password, cookiefilename):
        self.cookiefilename = cookiefilename
        self.opener,html = self.pre_login()
        login_url,data = self.get_form(html)
        for key,value in data.items():
            if 'password' in key:
                pwdname = key
            if isinstance(value, unicode):
                data[key] = data[key].encode('utf-8')
        data['mobile'] = username
        data[pwdname] = password
        data['remember'] = 'checked'

        request = urllib2.Request(
                url = login_url,
                data = urllib.urlencode(data),
                )
        result = self.opener.open(request, timeout=10).read()
        if '登录成功' in result:
            self.write_cookie()
            print 'login succeed!'
        else:
            raise Exception('login fail!Please try again!')

    def write_cookie(self):
        
        self.cookie_jar.save(self.cookiefilename)
        
    def rm_cookiefile(self):

        os.remove(self.cookiefilename)
    
    




