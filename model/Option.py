# -*- coding: utf-8 -*-
'''
Created on 2013/6/12

@author: LSJ
'''
from sqlalchemy import Column
from sqlalchemy.types import BigInteger,String,Text
from model.base import Model, Base
class Option(Model,Base):
    __tablename__ = "py_options"
    ID = Column(BigInteger, primary_key=True)
    option_name = Column("option_name", String(64))
    option_value = Column("option_value", Text)
    def getByName(self, name, close=True):
        s = self.session
        q = s.query(self.__class__)
        d = q.filter(self.__class__.option_name == name).first()
        if close:
            s.close()
        if d is None:
            return None
        return d
    def getAll(self,limit):
        s = self.session
        q = s.query(self.__class__)
        r = {}
        tmp = q.limit(limit).all()
        s.close()
        if tmp:
            for t in tmp:

                v={}
                v['ID']=t.ID
                v['value']=t.option_value
                r[t.option_name]=v
        return r
    def __repr__(self):
        return "Option"