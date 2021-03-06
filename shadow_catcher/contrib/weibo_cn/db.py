#!/usr/bin/env python
#coding:utf-8
# db.py - store data and provide access to db file.
#ver 0.1 by winkidney@gmail.com 2014-03-12

import sqlite3,os
#from sqlalchemy import create_engine
#from sqlalchemy.sql import text

dbname = "weibo_db"
user_table = 'user_info'
msg_table = 'messages'

class Querys(object):
    """querys collection of db access,provides
        a simple object-relation-model to other module.
    """

    qcreate_tui = """
    CREATE TABLE user_info
    (
        user_name vchar(255),
        sex int,
        uid vchar(20),
        email varchar(255),
        qq varchar(255),
        home varchar(255),
        care_about longtext,
        pk integer PRIMARY KEY,
        tags longtext,
        fans longtext,
        clocation longtext,
        level int,
        vip_level int
    );
    """
    
    qcreate_tmsg = """
    CREATE TABLE messages
    (
        mid integer PRIMARY KEY,
        p_time date,
        content longtext,
        tags text,
        is_forward int,
        uid_u vchar(20)
    );
    """
    qshow_tables = """
    select * from sqlite_master;
    """
    def __init__(self, dbname=None):
        if dbname and os.path.isfile(dbname):
            self.con = sqlite3.connect(dbname)
            self.cur = self.con.cursor()
        else: 
            self.create_db(dbname)
    
    def create_db(self,dbname):
        if os.path.isfile(dbname) or os.path.isdir(dbname):
            print "%s not a file(it's a folder) or file existed!" % dbname
            return
        self.con = sqlite3.connect(dbname)
        self.cur = self.con.cursor()
        self.create_tables()
        self.con.commit()
        
    def create_tables(self ):
        try:
            self.cur.execute(self.qcreate_tui)
            self.cur.execute(self.qcreate_tmsg)
        except Exception as e:
            print "table created failed with `%s`" % e
            
    def show_tables(self):
        if not self.con:
            print "connection not created!"
            return
        print self.cur.execute(self.qshow_tables).fetchall()
        
    def insert_userinfo(self, user_info):
        #user_info is a dict
        #arguments : user_name, sex, uid, email, qq, home, care_about, tags, fans, clocation, level, vip_level):
        for i in user_info.items():
            exec('%s = """%s"""' % (i[0], i[1]))
        qinsert_userinfo = """
        INSERT INTO user_info
             (user_name, sex, uid, email, qq, home, care_about, pk, tags, fans, clocation, level, vip_level)
             VALUES 
             ('%s', '%s',  '%s', '%s', '%s', '%s', '%s', NULL, '%s', '%s', '%s', '%s', '%s');
        """ % (user_name, sex, uid, email, qq, home,care_about, tags, fans, clocation, level, vip_level)
        
        self.cur.execute(qinsert_userinfo)
        self.con.commit()
        
    def insert_messages(self, p_time, content, tags, is_forward, uid_u):
        qinsert_message = """
        INSERT INTO messages
            (mid, p_time, content, tags, is_forward, uid_u)
            VALUES (NULL,'%s','%s','%s','%s','%s');
        """ % (p_time, content, tags, is_forward, uid_u)
        self.cur.execute(qinsert_message)
        self.con.commit()
        
    def get_cursor(self):
        return self.con.cursor()     


def test():
    global q
    q = Querys('testdb')
    #q.create_db('testdb')
    user_info = {'user_name' : '阿毛',
                     'uid' : '121212',
                     'email' : 'winkidney@gmail.com',
                     'qq' : '584532559',
                     'home' : 'home',
                     'care_about' : '关注',
                     'fans' : '标签',
                     'tags' : '粉丝',
                     'clocation' : '当前位置',
                     'level': '12',
                     'vip_level' : '3',
                     'sex' : '1',
                     }
    q.insert_userinfo(user_info)
    
if __name__ == "__main__":
    test()
    
