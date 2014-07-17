#!/usr/local/bin/python2.7
# encoding: utf-8
'''
src.contrib.bilibili.processor - process the existed html data.

@author:     winkidney

'''

import pyquery,os,csv



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
        except:
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
        
def main():
    
    dir_list = os.listdir('L_data/')
    dir_list.remove('test')
    for dir in dir_list:
        p = Processor('L_data/'+dir+'/', dir+'.csv')
        p.run()




 
        
        
        
        
        
        
        
        