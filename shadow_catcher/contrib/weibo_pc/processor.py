#!/usr/bin/env python
# encoding: utf-8
import pyquery
import re

follow_regx = re.compile(r'"ns"\:"pl.content.followTab.index"(.*?)"html"\:(.*?)\}\)')
follow_link_regx = re.compile(r"page_id\']=\'(\d*?)\'\;")


class ParseError(ValueError):
    pass


def wash(raw_text):
    """
    wash the input strings .
    replace '\\t' with '\t', '\\n' with '\n'
    """
    text = raw_text.replace('\\r', '\r').replace('\\n', '\n').replace('\\t', '\t').replace('\\', '')
    return text


def parse_one(raw_html):
    """
    return (uid, nick_name) list by one weibo follow page's text.
    :type follow_html: str
    """
    follow_html = wash(re.search(follow_regx, raw_html).group(2)[1:-1])

    pq = pyquery.PyQuery(follow_html)
    return pq


def find_follow_pid(user_home_page):

    return re.search(follow_link_regx, user_home_page).group(1)


def parse_uids(pq_obj):
    """
    get uid list from a pyquery object.
    :type pq_obj :pyqurey.PyQuery
    :return (nickname, uid) list of given page
    """
    pq = pq_obj
    user_list = []
    for img in pq('div.face img'):
        uid = img.attrib.get('usercard').split('=')[-1]
        nickname = img.attrib.get('alt')
        user_list.append((nickname, uid))
    return user_list


def get_page_max(pq_obj):
    pq = pq_obj
    if pq('[page-limited=true]'):
        return 10
    page_links = pq('a.page')
    if page_links:
        return len(page_links)
    return 1






    
