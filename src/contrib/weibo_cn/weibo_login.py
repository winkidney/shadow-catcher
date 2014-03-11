#!/usr/local/env python
#coding:utf-8
#weibo_login.py - weibo.cn login script,return a opener for spdiers
#by winkidney@gmail.com 2014-03-10

import urllib, urllib2, cookielib
from bs4 import BeautifulSoup


class Weibo(object):

    def pre_login(self):
        #headers = {'User-Agent' : 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:27.0) Gecko/20100101 Firefox/27.0' }
        addheaders = [('User-Agent', 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:27.0) Gecko/20100101 Firefox/27.0')]
        self.cookie_jar = cookielib.CookieJar()
        pre_login_url = 'http://login.weibo.cn/login/'
        pre_request = urllib2.Request(
                url = pre_login_url,
                #headers = self.headers,
                )
        opener = urllib2.build_opener(
                urllib2.HTTPCookieProcessor(self.cookie_jar), 
                urllib2.HTTPHandler()
                )
        opener.addheaders = addheaders
        pre_response = opener.open(pre_request)
        result = pre_response.read()
        pre_response.close()
        return opener,result

    def get_form(self,html):
        soup = BeautifulSoup(html, 'lxml')
        data = {}
        form = soup.find('form')
        login_url = 'http://login.weibo.cn/login/'+form.attrs.get('action')
        for i in form.find_all('input'):
            data[i.attrs.get('name')] = i.attrs.get('value')
        return login_url,data

    def login(self,username, password):
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
        result = self.opener.open(request).read()
        if '登录成功' in result:
            print 'login succeed!'
        else:
            raise Exception('login fail!Please try again!')
        
                
    
    




