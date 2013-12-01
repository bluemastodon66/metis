# -*- coding: utf-8 -*-
'''
Created on 2013/6/12

@author: LSJ
'''
from sqlalchemy import Column, func
from sqlalchemy.types import BigInteger,String,Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import desc, and_
from model.base import Model, Base
import datetime
class Media(Model,Base):
    __tablename__ = "py_media"
    ID = Column(BigInteger, primary_key=True)
    name = Column("name", String(200), default="")
    related_path = Column("related_path", String(255), default="")
    upload_date = Column("upload_date", DateTime, default=str(datetime.datetime.now()))
    description = Column("description", Text, default="")
    size = Column("size",BigInteger, default=0)
    type = Column("type", String(100), default="")
    author_id = Column("author_id",BigInteger, default=0)
    resolution = Column("resolution", String(50), default="")
    user = relationship("User", primaryjoin="Media.author_id==User.ID", foreign_keys=author_id, lazy="joined")

    def getByID(self, id, close=True):
        s = self.session
        r = s.query(self.__class__).filter(self.__class__.ID == id).first()
        if close:
            s.close()
        return r
    def delByIDs(self, ids):
        if not ids:
            return
        stmt = self.__table__.delete().where(self.__class__.ID.in_(ids))
        s=self.session
        try:
            s.execute(stmt)
            s.commit()
        except:
            pass
        finally:
            s.close()
    def searchByKeyword(self, k, start, limit, userid=0):
        s = self.session
        total=0
        conditions = []
        if userid >0:
            conditions.append(self.__class__.author_id == userid)
        if k != "":
            conditions.append((self.__class__.name.like("%"+k+"%")) | (self.__class__.description.like("%"+k+"%")))
        filters = and_(*conditions)
        r = []
        tmp = s.query(func.count(self.__class__.ID)).filter(filters).first()
        if not tmp is None:
            total = tmp[0]
        if total >0:
            r = s.query(self.__class__).filter(filters).order_by(desc(self.__class__.ID)).offset(start).limit(limit).all()
        ret = dict(total=total,data=r)
        s.close()
        return ret
    def __repr__(self):
        return "Media"