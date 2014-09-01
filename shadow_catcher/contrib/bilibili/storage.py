#!/usr/bin/env python
# coding:utf-8
# bilibili/storage.py - the storage api file.
# author : winkidney - 14-8-21
__author__ = 'winkidney'

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import (
    String,
    Integer,
    Text,
    Column,
    DateTime,
)
from sqlalchemy import create_engine
import csv
import datetime
DEFAULT_ENGINE = create_engine('sqlite:///bilibili.sqlite', echo=False)

Base = declarative_base()


def get_session(dbname=None):
    if dbname:
        engine = create_engine(dbname, echo=True, autoflush=False)
    else:
        engine = DEFAULT_ENGINE
    Session = sessionmaker(bind=engine)
    return Session()

class BVideo(Base):
    __tablename__ = 'bilibili'

    id = Column(Integer, autoincrement=True, primary_key=True)
    av = Column(String, unique=True)
    title = Column(String)
    up = Column(String)
    plays = Column(Integer, nullable=True, default=0)
    stars = Column(Integer, nullable=True, default=0)
    comments = Column(Integer, nullable=True,default=0)
    up_at = Column(DateTime, nullable=True)
    description = Column(Text)
    tags = Column(String)
    type = Column(String)



def create_table():
    Base.metadata.create_all(DEFAULT_ENGINE)

def import_data(csv_fname):
    csvfile = open(csv_fname, 'rb')
    csv_reader = csv.reader(csvfile)
    loop = 0
    Session = sessionmaker(bind=DEFAULT_ENGINE)
    session = Session()

    for row in csv_reader:
        if loop == 0:
            loop += 1
            continue
        if len(row[6]) < 5:
            up_at = None
        else:
            year, month, day = row[6].split(' ')[0].split('-')
            up_at = datetime.date(int(year), int(month), int(day))
        if session.query(BVideo).filter_by(av=row[0]).first():
            print '%s existed!' % row[0]
            continue
        video = BVideo(
            av=row[0],
            plays=row[1],
            stars=row[2],
            comments=row[3],
            title=row[4].decode('utf-8'),
            up=row[5],
            up_at=up_at,
        )
        session.add(video)
        print row[0],'done'
        loop += 1
    session.commit()
    print loop

def convert_to_raw():
    import cPickle
    session = get_session()
    b = BVideo
    results = session.query(BVideo).values(b.av, b.title,b.up,
                                           b.plays, b.stars, b.comments,
                                           b.up_at,b.description,
                                           b.tags, b.type)
    total_dict = {}
    for i in results:
        video = {}
        video['av'] = i[0]
        video['title'] = i[1]
        video['up'] = i[2]
        video['plays'] = i[3]
        video['stars'] = i[4]
        video['comments'] = i[5]
        video['up_at'] = i[6]
        video['description'] = i[7]
        video['tags'] = i[8]
        video['type'] = i[9]
        total_dict[video['av']] = video
    encoded_dict = cPickle.dumps(total_dict)
    f = open('raw_all.data', 'w')
    f.write(encoded_dict)
    return encoded_dict

def rebuild_extraw(total_data):
    import cPickle
    results = cPickle.load(open('raw_asdict.data', 'r'))
    for result in results:
        dit = total_data[result['av']]
        dit['tags'] = result['tags']
        dit['description'] = result['description']
        dit['type'] = result['type']
    return total_data

if __name__ == '__main__':
    create_table()
    import sys, os
    if len(sys.argv) < 2:
        print "Usage: %s csvfile" % sys.argv[0]
        exit()
    if os.path.isdir(sys.argv[1]):
        for fname in os.listdir(sys.argv[1]):
            if fname.endswith('csv'):
                import_data(os.path.join(sys.argv[1], fname))
        exit()
    import_data(sys.argv[1])
