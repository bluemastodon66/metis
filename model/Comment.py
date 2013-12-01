# -*- coding: utf-8 -*-
'''
Created on 2013/6/12

@author: LSJ
'''
from sqlalchemy import Column, ForeignKey, func, and_,desc
from sqlalchemy.types import String, DateTime, BigInteger, Text
from sqlalchemy.orm import relationship
from model.base import Model, Base
import datetime

class Comment(Model,Base):

    __tablename__ = "py_comments"
    ID = Column(BigInteger, primary_key=True)
    post_id = Column("post_id", BigInteger, ForeignKey('py_posts.ID'))
    user_id = Column("user_id", BigInteger, default=0)
    date = Column("date", DateTime, default=str(datetime.datetime.now()))
    content = Column("content", Text, default="")
    author = Column("author", String(100), default="unknown")
    email = Column("email", String(100) ,default="unknown")
    url = Column("url", String(200), default="")
    IP = Column("IP", String(100), default="unknown")
    agent = Column("agent",String(255), default="unknown")
    user = relationship("User", primaryjoin="Comment.user_id==User.ID", foreign_keys=user_id, lazy="joined")

    def getByID(self,uid, close=True):
        s=self.session
        tmp=s.query(Comment).filter(self.__class__.ID==uid).first()
        if close:
            s.close()
        return tmp
    def searchByKeyword(self, k, start, limit, userid=0):
        s = self.session
        total=0
        conditions = []
        if userid > 0:
                conditions.append(self.__class__.user_id == userid)
        if k != "":
            conditions.append((self.__class__.content.like("%"+k+"%")) | (self.__class__.IP.like("%"+k+"%")))
        filters = and_(*conditions)
        r = []
        tmp = s.query(func.count(self.__class__.ID)).filter(filters).first()
        if not tmp is None:
            total = tmp[0]
        if total >0:
            r = s.query(self.__class__).filter(filters).order_by(desc(self.__class__.date)).offset(start).limit(limit).all()
        ret = dict(total=total,data=r)
        s.close()
        return ret
    def getCountByPostID(self,uid):
        s = self.session
        q = s.query(func.count(self.__class__.post_id))
        r = q.filter(self.__class__.post_id == uid).one()
        s.close()
        return r[0]

    def removeAllByArray(self, ids):
        if not ids:
            return False
        stmt = self.__table__.delete().where(self.__class__.ID.in_(ids))
        s=self.session
        try:
            s.execute(stmt)
            s.commit()
            flag=True
        except:
            flag=False
        finally:
            s.close()
        return flag

    def getList(self, start, limit, postID):
        s = self.session
        total=0
        conditions = []
        conditions.append(self.__class__.post_id == postID)
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
        return "Comment"
 


