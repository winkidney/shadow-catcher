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


def get_session():
    Session = sessionmaker(bind=DEFAULT_ENGINE)
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
    tags = Column(Text)



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
