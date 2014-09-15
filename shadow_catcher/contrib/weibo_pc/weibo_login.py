#!/usr/bin/env python
#coding=utf8
#:
"""
Created on Mar 18, 2013
Rewrite on Mar 09, 2014

@author: yoyzhou
@rewrite: winkidney
"""

import os
import urllib
import urllib2
import cookielib
import base64
import re
import hashlib
import json
import rsa
import binascii


"""
usage:
main(username, password)
return a opener of urllib2.
"""
import logging


HEADERS = [('User-Agent', 'Mozilla/5.0 (X11; Linux i686; rv:8.0) Gecko/20100101 Firefox/8.0'),
           ('Host', 'weibo.com'),
           ('Referer', 'http://weibo.com/')]
HEADERS_DICT = {'User-Agent': 'Mozilla/5.0 (X11; Linux i686; rv:8.0) Gecko/20100101 Firefox/8.0',
                'Host': 'weibo.com',
                'Referer': 'http://weibo.com/'}


class DataParseError(ValueError):
    pass


def get_pwd_wsse(pwd, servertime, nonce):
    """
        Get wsse encrypted password
    """
    pwd1 = hashlib.sha1(pwd).hexdigest()
    pwd2 = hashlib.sha1(pwd1).hexdigest()
    pwd3_ = pwd2 + servertime + nonce
    pwd3 = hashlib.sha1(pwd3_).hexdigest()
    return pwd3


def get_pwd_rsa(pwd, servertime, nonce):
    """
        Get rsa2 encrypted password, using RSA module from https://pypi.python.org/pypi/rsa/3.1.1, documents can be accessed at
        http://stuvel.eu/files/python-rsa-doc/index.html
    """
    #n, n parameter of RSA public key, which is published by WEIBO.COM
    #hardcoded here but you can also find it from values return from prelogin status above
    weibo_rsa_n = 'EB2A38568661887FA180BDDB5CABD5F21C7BFD59C090CB2D245A87AC253062882729293E5506350508E7F9AA3BB77F4333231490F915F6D63C55FE2F08A49B353F444AD3993CACC02DB784ABBB8E42A9B1BBFFFB38BE18D78E87A0E41B9B8F73A928EE0CCEE1F6739884B9777E4FE9E88A1BBE495927AC4A799B3181D6442443'

    #e, exponent parameter of RSA public key, WEIBO uses 0x10001, which is 65537 in Decimal
    weibo_rsa_e = 65537

    message = '%s\t%s\n%s' % (str(servertime), str(nonce), str(pwd))

    #construct WEIBO RSA Publickey using n and e above, note that n is a hex string
    key = rsa.PublicKey(int(weibo_rsa_n, 16), weibo_rsa_e)

    encropy_pwd = rsa.encrypt(message, key)

    return binascii.b2a_hex(encropy_pwd)


def get_user(username):
    username_ = urllib.quote(username)
    username = base64.encodestring(username_)[:-1]
    return username


def get_prelogin_status(username):
    """
    Perform prelogin action, get prelogin status, including servertime, nonce, rsakv, etc.
    """

    prelogin_url = 'http://login.sina.com.cn/sso/prelogin.php?entry=weibo&callback=sinaSSOController.preloginCallBack&su=' + get_user(username) + \
     '&rsakt=mod&checkpin=1&client=ssologin.js(v1.4.5)'
    prelogin_data = urllib2.urlopen(prelogin_url).read()
    regx = re.compile('\((.*)\)')
    json_data = regx.search(prelogin_data).group(1)
    try:
        data = json.loads(json_data)
        servertime = str(data['servertime'])
        nonce = data['nonce']
        rsakv = data['rsakv']
        return servertime, nonce, rsakv
    except:
        raise DataParseError('Getting prelogin status failed!'
                             'The json_data is %s' % json_data)


def do_login(username, pwd, cookie_file):
    """"
    Perform login action with use name, password and saving cookies.
    @param username: login user name
    @param pwd: login password
    @param cookie_file: file name where to save cookies when login succeeded
    """
    #POST data per LOGIN WEIBO, these fields can be captured using httpfox extension in FIrefox
    login_data = {
        'entry': 'weibo',
        'gateway': '1',
        'from': '',
        'savestate': '7',
        'userticket': '1',
        'pagerefer':'',
        'vsnf': '1',
        'su': '',
        'service': 'miniblog',
        'servertime': '',
        'nonce': '',
        'pwencode': 'rsa2',
        'rsakv': '',
        'sp': '',
        'encoding': 'UTF-8',
        'prelt': '110',
        'url': 'http://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack',
        'returntype': 'META'
        }

    cookie_jar = cookielib.CookieJar()
    cookie_processor = urllib2.HTTPCookieProcessor(cookie_jar)
    opener = urllib2.build_opener(cookie_processor, urllib2.HTTPHandler)
    login_url = 'http://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.5)'
    servertime, nonce, rsakv = get_prelogin_status(username)

    #Fill POST data
    login_data['servertime'] = servertime
    login_data['nonce'] = nonce
    login_data['su'] = get_user(username)
    login_data['sp'] = get_pwd_rsa(pwd, servertime, nonce)
    login_data['rsakv'] = rsakv

    form_data = urllib.urlencode(login_data)
    opener.addheaders = HEADERS
    login_req = urllib2.Request(
        url=login_url,
        data=form_data,
    )
    result = opener.open(login_req).read()
    redirect_regx = re.compile('replace\((.*?)\)')

    #Search login redirection URL
    try:
        login_url = redirect_regx.search(result).group(1)[1:-1]
    except:
        raise DataParseError('Redirection url parse failed!'
                             'The result data is %s' % result)
    feedback_raw = opener.open(login_url).read()

    #Verify login feedback, check whether result is TRUE
    patt_feedback = 'feedBackUrlCallBack\((.*)\)'
    feedback_regx = re.compile(patt_feedback, re.MULTILINE)

    feedback_data = feedback_regx.search(feedback_raw).group(1)

    feedback_json = json.loads(feedback_data)
    if feedback_json['result']:
        #cookie_jar.save(cookie_file, ignore_discard=True, ignore_expires=True)
        return opener, cookie_jar
    else:
        raise ValueError("[info]feedback data parse error!Login failed!"
                         "feedback data is %s " % feedback_json)


def login(username, pwd, cookie_file):
    """
    Login with username or password.
    If cookie_file is none, do real login .
    If not , load cookie file and check if the login succeed.
    :type username: str
    :type pwd: str
    :type cookie_file: str
    :return opener of urllib2
    """
    if os.path.exists(cookie_file):
        try:
            cookie_jar = cookielib.LWPCookieJar(cookie_file)
            cookie_jar.load(ignore_discard=True, ignore_expires=False)
            loaded = True
        except cookielib.LoadError:
            loaded = False
            logging.warning('[info]Cookies not loaded')
        
        #install loaded cookies for urllib2
        if loaded:
            cookie_processor = urllib2.HTTPCookieProcessor(cookie_jar)
            opener = urllib2.build_opener(cookie_processor, urllib2.HTTPHandler)
            #urllib2.install_opener(opener)
            logging.info('Use existed cookies!')
            opener.addheaders = HEADERS
            return opener
        else:
            logging.info("[info] do real login, cookies files not found")
            return do_login(username, pwd, cookie_file)
    
    else:
        logging.info("[info]Cookie file does not existed, do real login now")
        return do_login(username, pwd, cookie_file)


def main(username, password):
    """
    :type username : string or unicode object
    :type password : string object
    :return a opener of urllib2.
    """
    cookie_file = 'weibo_login_cookies.dat'
    cw_opener = login(username, password, cookie_file)
    if cw_opener:
        logging.info('WEIBO Login succeeded')
        return cw_opener
    else:
        logging.info('WEIBO Login failed')

