#coding=utf8
__author__ = 'Jackie Su <hang@jackiesu.com>'

import urllib2,cookielib
import re,os,time
from HttpUtils import HttpReq
from bs4 import BeautifulSoup
#from WeiboModel import Message,Profile
import settings
import datetime

class WeiboProxy:
    """
    This class work as a proxy of Sina Weibo.
    Note: try_login() should be called before calling any other method
    """
    def __init__(self):
        self.user_name       = settings.user_name
        self.password        = settings.password
        self.login_page_url  = "http://3g.sina.com.cn/prog/wapsite/sso/login.php?ns=1&revalid=2&backURL=http%3A%2F%2Fweibo.cn%2F%3Fs2w%3Dlogin&backTitle=%D0%C2%C0%CB%CE%A2%B2%A9&vt="
        self.form_submit_url = "http://3g.sina.com.cn/prog/wapsite/sso/login_submit.php?backURL=http%3A%2F%2Fweibo.cn%2F&backTitle=%D0%C2%C0%CB%CE%A2%B2%A9"
        self.cookie_path     = "cookie.dat"
        self.base_url        = 'http://weibo.cn/'

    def try_login(self):
        """
        This method tries load cookie data from given cookie path.
        if it failed to load, the login() method will be called.
        """
        if os.path.exists(self.cookie_path):
            try:
                cookie_jar  = cookielib.LWPCookieJar(self.cookie_path)
                cookie_jar.load(ignore_discard=True, ignore_expires=True)
                loaded      = 1
            except cookielib.LoadError:
                loaded = 0
                print 'Loading cookies error'

            if loaded:
                cookie_support = urllib2.HTTPCookieProcessor(cookie_jar)
                opener         = urllib2.build_opener(cookie_support, urllib2.HTTPHandler)
                urllib2.install_opener(opener)
                print 'Loading cookies success'
                return True
            else:
                return self.login()
        else:
            return self.login()

    def login(self):
        """
        Mimic the login process of weibo.cn.
        For test purpose, some of the web page will be saved.
        After a successful login, cookie data will be saved into cookie.dat for future usage.
        """
        cookie_jar2     = cookielib.LWPCookieJar()
        cookie_support2 = urllib2.HTTPCookieProcessor(cookie_jar2)
        opener2         = urllib2.build_opener(cookie_support2, urllib2.HTTPHandler)
        urllib2.install_opener(opener2)

        requester  = HttpReq()

        text       = requester.open_read(self.login_page_url)
        test_file  = open('test.html', 'w')
        test_file.write(text)

        while True:
            box_name   = re.search('type="password" name="(.+?)"', text).group(1)
            vk_data    = re.search('name="vk" value="(.+?)"', text).group(1)

            #box_name='password_1844'
            #vk_data='1844_0540_1540419154'

            login_data = {
                "mobile": self.user_name,
                box_name: self.password,
                "remember":"on",
                "vk": vk_data,
                "submit":"登录",
                'backURL':'http%253A%252F%252Fweibo.cn%252F',
                "backTitle":"新浪微博"
            }
            text       = requester.open_read(self.form_submit_url, login_data)
            test_file  = open('login.html', 'w')
            test_file.write(text)

            link       = re.search('href="([^"]+)"', text).group(1).replace('&amp;','&')
            print link
            if link.startswith('http'):
                print 'ok'
                break
            else:
                self.form_submit_url = re.search('action="([^"]+)"', text).group(1).replace('&amp;','&')
                print self.form_submit_url

        time.sleep(2)
        text       = requester.open_read(link)
        print text
        test_file  = open('index.html', 'w')
        test_file.write(text)


        time.sleep(5)
        #urllib2.urlopen('http://weibo.cn/account/customize/more?DisplayMode=1&CssType=0&tf=7_009')

        cookie_jar2.save(self.cookie_path ,ignore_discard=True, ignore_expires=True)
        return True

    def fetch_msg_page(self,uid, start=1, stop_timestamp = datetime.datetime.min):
        """
        Fetch each weibo message page one by one from the start index.
        Parse each message, then fetch corresponding comments.
        Finally, save messages into database
        """
        REQ  = HttpReq()
        if uid.isdigit():
            url_tpl = 'http://weibo.cn/u/{0}?rl=0&page={{0}}'.format(uid)
        else:
            url_tpl = 'http://weibo.cn/{0}?page={{0}}'.format(uid)

        index = start
        stop  = False
        while not stop:
            url = url_tpl.format(index)
            print 'fetching', url
            page = REQ.open_read(url)
            soup = BeautifulSoup(page)
            divs = soup.find_all('div','c', id=True)
            if not len(divs):
                stop = True
            else:
                index+=1
                for div in divs:
                    msg = Message()
                    n_comments = msg.parse(div)
                    msg.user_id = uid
                    #if the there are comments
                    if n_comments:
                        self.fetch_comments(msg)
                    msg.save()
                    if msg.timestamp < stop_timestamp:
                        stop = True
                        break

    def fetch_comments(self, msg, start=1):

        url_tpl = "http://weibo.cn/comment/{0}?page={{0}}#cmtfrm".format(msg._id)

        index = start
        REQ = HttpReq()

        while True:
            url = url_tpl.format(index)
            print 'fetching', url
            page = REQ.open_read(url)
            print 'fetch done'
            if not msg.parse_comments(page):
                break
            index += 1

    def fetch_profile(self, url):
        """
        Fetch profile of person with given uid, save into database
        """
        is_custom = not url.startswith('u/')
        url     = self.base_url + url
        print 'fetching',url
        REQ     = HttpReq()
        page    = REQ.open_read(url)
        #open('pages/profiles.html','w').write(page)
        soup    = BeautifulSoup(page)
        profile = Profile()
        profile.parse(soup.find('div','u'))
        self.fetch_follow(profile)
        if is_custom:
            profile.url = url
        profile.save()
        print profile.name,'done'
        return profile

    def fetch_follow(self, profile):
        REQ  = HttpReq()
        url_tpl = 'http://weibo.cn/{0}/follow?page={{0}}'.format(profile.uid)

        index = 1
        stop  = False
        while not stop:
            url = url_tpl.format(index)
            print 'fetching',url
            page = REQ.open_read(url)
            if not profile.parse_follow(page):
                stop = True
            index += 1

    def update_msg(self, profile):
        timestamp = datetime.datetime.now()
        self.fetch_msg_page(profile.uid, stop_timestamp=profile.last_update)
        profile.last_update = timestamp
        profile.save()

    def update_profile(self, profile):
        url     = self.base_url + profile.url
        print 'fetching',url
        REQ     = HttpReq()
        page    = REQ.open_read(url)
        soup    = BeautifulSoup(page)
        profile = Profile()
        profile.parse(soup.find('div','u'))
        self.update_follow(profile)
        profile.save()
        print profile.name,'done'
        return profile

    def update_follow(self, profile):
        REQ  = HttpReq()
        url_tpl = 'http://weibo.cn/{0}/follow?page={{0}}'.format(profile.uid)

        index = 1
        stop  = False
        while not stop:
            url = url_tpl.format(index)
            print 'fetching',url
            page = REQ.open_read(url)
            if not profile.update_follow(page):
                stop = True
            index += 1

if __name__  ==  '__main__':
    pass
