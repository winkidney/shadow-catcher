#!/usr/bin/env python
# encoding: utf-8
import pyquery
import re

fllow_regx = re.compile(r'"ns"\:"pl.content.followTab.index"(.*?)"html"\:(.*?)\}\)')


def wash(raw_text):
    """
    wash the input strings .
    replace '\\t' with '\t', '\\n' with '\n'
    """
    return raw_text.replace('\\r','\r').replace('\\n', '\n').replace('\\t', '\t').replace('\\', '')


def prase_one(follow_html):
    """
    return (uid, nick_name) list by prasing follow_html text.
    :type follow_html: str
    """
    pq = pyquery.Pyquery(follow_html)
    user_list = []
    for img in pq('div.face img'):
        uid = img.attrib.get('usercard').split('=')[-1]
        nickname = img.attrib.get('alt')
        user_list.append((nickname, uid))
    return user_list

def parse_from_js(raw_html):
    """
    Parse html text from raw js-included html.
    :type raw_html: str
    :param raw_html: raw html from source page.
    :return pure html text of follow page.
    """
    return wash(re.search(follow_regx, raw_html).group(2)[1:-1])



    
