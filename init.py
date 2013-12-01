# -*- coding: utf-8 -*-
'''
Created on 2013/10/30
Init Connent To DB
@author: LSJ
'''


from settings import options
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column
from sqlalchemy.types import BigInteger, String,Text
from libs import pyCache
Base = declarative_base()
class Db(object):
    engine = None
    session = None
    def __init__(self):
        print "[Info] connect to db"
        self.engine = create_engine("mysql://{0}:{1}@{2}/{3}?charset=utf8".format(options.mysql_user, options.mysql_password, options.mysql_host, options.mysql_database)
                            , pool_size=options.mysql_poolsize
                            , pool_recycle=3600
                            , encoding='utf-8'
                            , echo=options.debug
                            , echo_pool=options.debug)
        Session = sessionmaker(bind=self.engine)
        try:
            self.session = Session()
            Base.metadata.create_all(self.engine)
        except:
            print "[Error] connect to database failed"
            self.session = None
class Option(Base):
    db=Db()
    __tablename__ = "py_options"
    ID = Column(BigInteger, primary_key=True)
    option_name = Column("option_name", String(64))
    option_value = Column("option_value", Text)

    def getAll(self,limit):

        if not self.db.session:
            return False
        s = self.db.session
        r = s.query(self.__class__).limit(limit).all()
        s.close()
        return r

def isStarted():
    print "*************************"
    print "****** init start *******"
    print "*************************"
    query = Option()
    rec = query.getAll(100)

    if not rec:
        return False
    for t in rec:
        pyCache.WebOptions[t.option_name]=t.option_value
    return True
