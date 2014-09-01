#!/usr/local/bin/python2.7
# encoding: utf-8
'''
shadow_catcher.contrib.bilibili.processor - process the existed html data.

@author:     winkidney
'''
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql.expression import Insert
import pyquery, os, csv
from shadow_catcher.SClib.base import ungz_as_utf8

def g_kw(kword):
    kword = kword.replace("/", "//");  
    kword = kword.replace("'", "''");  
    kword = kword.replace("[", "/[");  
    kword = kword.replace("]", "/]");  
    kword = kword.replace("%", "/%");  
    kword = kword.replace("&", "/&");
    kword = kword.replace("_", "/_");  
    kword = kword.replace("(", "/(");  
    kword = kword.replace(")", "/)"); 

class Processor(object):
    """
        The html file processor for bilibili
        Return a ( av_code, played, stars, title, author, date) list.
    """
    def __init__(self, root_dir, save_as):
        """
            root_dir : root dir of the html file.
            save_as : the csv filename.
        """
        self.root_dir = root_dir
        self.csv_file = save_as
    
    def read_file(self, filename):
        "return unicode object"
        page_file = open(filename,'rb')
        content = page_file.read().decode('utf-8')
        return content
    
    def _prase_number(self, number_str):
        if '万' in number_str:
                number_str = number_str.replace('万','')
                number = int(float(number_str)*10000)
        elif '--' in number_str:
            number = 0
        else:
            number = int(number_str)
        return number
    
    def prase(self, content):
        """
            content : str or unicode object
        """
        try:
            pq = pyquery.PyQuery(content)
            av_list = []
            for video in pq("li.l1").items():
                av_code = video('.title').attr('href').split('/')[-2]
                played = self._prase_number(video('.gk').html())
                stars = self._prase_number(video('.sc').html())
                comments = self._prase_number(video(".dm").html())
                date =  video('.date').html()
                title = video('.title').html().encode('utf-8')
                author = video('.up').attr('href').split('/')[-1]
                aitem = (av_code, played, stars, comments, title, author, date)
                av_list.append(aitem)
        except Exception:
            return []
        return av_list

    def save_csv(self, total_list):
        f = open(self.csv_file, 'wb')
        c_writer = csv.writer(f, dialect='excel',
                                )
        c_writer.writerow(('AV号', '播放次数', '收藏数', '弹幕数', '标题', 'up主', '日期'))
        c_writer.writerows(total_list)

    def run(self):
        file_list = os.listdir(self.root_dir)
        total_list = []
        for fname in file_list:
            path = self.root_dir+fname
            content = self.read_file(path)
            av_list = self.prase(content)
            total_list.extend(av_list)
            print "[info] : %s processed!" % fname
        self.save_csv(total_list)
        print "%s saved!" % self.csv_file


class ProcessAVInfo(object):

    def __init__(self, flist, data_dir, csvname):
        self.flist = flist
        import sqlite3
        self.con = sqlite3.connect('newbilibili.sqlite')
        self.cur = self.con.cursor()
        self.data_dir = data_dir
        self.csv_file = csvname
        
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
        SET tags=?, description=?, type=?
        WHERE av=?;
        """ % c_dict
        #print query
        self.cur.execute(query)
        
        
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


def convert_to_sqlite():
    """
    :type session : sqlalchemy.orm.session
    :return:
    """
    import cPickle as Pickle
    from storage import BVideo, get_session
    session = get_session('sqlite:///newbilibili.sqlite')
    data = Pickle.load(open('fraw.data', 'rb'))
    count = 1
    total = len(data)
    for video in data:
        #print video[0]
        b = session.query(BVideo).filter_by(av=video[0]).first()
        b.tags = video[1]
        b.description = video[2]
        b.type = video[3]
        session.flush()
        session.commit()
        if count % 100 == 0:


            print "[info] %(count)s/%(total)s inserted!" % {'count': count, 'total': total, }

        count += 1


@compiles(Insert)
def append_string(insert, compiler, **kw):
    s = compiler.visit_insert(insert, **kw)
    if 'append_string' in insert.kwargs:
        return s + " " + insert.kwargs['append_string']
    return s


def hex_buffer(buf):
    retstr=''.join(map(lambda c:'\\x%02x'%ord(c),buf))
    retstr="E'"+retstr+"'"
    return retstr

def insert_or_update():
    import cPickle as Pickle
    from sqlalchemy import create_engine
    from storage import BVideo
    engine_r = create_engine('sqlite:///bilibili.sqlite', echo=True)
    engine_t = create_engine('sqlite://bilibili_per.sqlite')



def main():
    flist = os.listdir('data')
    ProcessAVInfo(flist, 'data', 'bilibiliextend.csv')

if __name__ == '__main__':
    main()



 
        
        
        
        
        
        
        
        
