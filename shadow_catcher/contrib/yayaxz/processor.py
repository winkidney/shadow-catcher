#!/usr/local/bin/python2.7
# coding: utf-8
'''
shadow_catcher.contrib.bilibili.processor - process the existed html data.

@author:     winkidney
'''

import pyquery, os, csv
from shadow_catcher.SClib.base import ungz_as_utf8, read_as_utf8

def g_kw(kword):
    kword = kword.replace("/", "//");  
    kword = kword.replace("'", "''");  
    kword = kword.replace("[", "/[");  
    kword = kword.replace("]", "/]");  
    kword = kword.replace("%", "/%");  
    kword = kword.replace("&","/&");  
    kword = kword.replace("_", "/_");  
    kword = kword.replace("(", "/(");  
    kword = kword.replace(")", "/)"); 

class ProcessAVInfo(object):

    def __init__(self, flist, data_dir, csvname):
        self.flist = flist
        import sqlite3
        self.con = sqlite3.connect('newbilibili.sqlite')
        self.cur = self.con.cursor()
        self.data_dir = data_dir
        self.csv_file = csvname
        self.run()
        
    def process_one(self, content):
        
        pq = pyquery.PyQuery(content)
        c_dict = {}
        try:
            c_dict['tags'] = pq('meta[name=keywords]').attr('content')
            c_dict['description'] = pq('meta[name=description]').attr('content')
            c_dict['av'] = self.av
            c_dict['type'] = ','.join([ i.text for i in pq('.tminfo a[property="v:title"]') ])
            return (c_dict['av'], c_dict['tags'], c_dict['description'], c_dict['type'])
        except Exception as e:
            print 'fail on %s prase' % self.av
            return None
         
        #self._insert_row(c_dict)
            
    def read_file(self, filename):
        
        self.av = filename.split('.')[0]
        filename = os.path.join(self.data_dir, filename)
        return ungz_as_utf8(filename)
        
    def save_csv(self, total_list):
        f = open(self.csv_file, 'wb')
        c_writer = csv.writer(f, dialect='excel',
                                quotechar='|',)
        c_writer.writerow(('av', 'tags', 'description', 'type',))
        c_writer.writerows(total_list)
        
    def _insert_row(self, c_dict):
        query = """
        UPDATE bilibili
        SET tags='%(tags)s', description='%(description)s', type='%(type)s'
        WHERE av='%(av)s';
        """ % c_dict
        #print query
        self.cur.execute(query, )
        
        
    def run(self):
        import cPickle
        if not self.flist:
            raise ValueError('flist argument must be a filepath list')
        count  = 0
        total = len(self.flist)
        total_list = []
        for f in self.flist:
            result = self.process_one(self.read_file(f))
            if result:
                total_list.append(result)
            count += 1
            if count%100 == 0:
                self.con.commit()
                print "[info] %s/%s rows inserted!" % (count, total)
        f_raw = cPickle.dumps(total_list)
        open('fraw.data', 'w').write(f_raw)
        self.save_csv(total_list)
            
        
def process_list(filename):
    content = read_as_utf8(filename)
    pq = pyquery.PyQuery(content)
    video_list = []
    for i in pq('.resource-dq-box li'):
        video = {}
        video['href'] = pyquery.PyQuery(i)('.resource-dq-item a').attr('href')
        print video
        video_list.append(video)
    return video_list

def process_detail(filename):
    content = read_as_utf8(filename)
    doc = pyquery.PyQuery(content)
    if not doc:
        return None

    info = doc('.resource-detail-txt li')
    result = {}
    result['res'] = filename.split('/')[-1].split('.')[0]
    result['name'] = unicode(doc('.resource-detail-box h2 a')[0].text_content())
    if len(info) == 7:
        
        result['pub_date'] = unicode(info[0].text_content().split(u'：')[1])
        result['type'] = unicode(info[1].text_content().split(u'：')[1])
        result['director'] = unicode(info[2].text_content().split(u'：')[1])
        result['heros'] = unicode(info[3].text_content().split(u'：')[1])
        result['description'] = unicode(info[6].text_content())
    else:
        result['pub_date'] = unicode(info[0].text_content().split(u'：')[1])
        result['type'] = unicode(info[1].text_content().split(u'：')[1])
        result['description'] = unicode(info[-1].text_content())
    result['links'] = []
    if doc('a.resource-download-name'):
        for item in pyquery.PyQuery(doc("dd.resource-item")):
            count = 0
            for lkitem in pyquery.PyQuery(item)('a.resource-download-name'):
                if count > 0:
                    break
                link = {}
                link['name'] = unicode(pyquery.PyQuery(lkitem).attr('title'))
                link['link'] = unicode(pyquery.PyQuery(lkitem).attr('href'))
                result['links'].append(link)
                count += 1

    return result

def get_detail():
    data_dir = 'detail_data'
    filelist = os.listdir(data_dir)
    result_list = []
    for fname in filelist:
        fpath = os.path.join(data_dir, fname)
        result = process_detail(fpath)
        if result:
            result_list.append(result)
    return result_list


def main():
    flist = os.listdir('data')
    ProcessAVInfo(flist, 'data', 'bilibiliextend.csv')

if __name__ == '__main__':
    main()



 
        
        
        
        
        
        
        
        
