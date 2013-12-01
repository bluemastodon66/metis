# -*- coding: utf-8 -*-
'''
Created on 2013/6/12

@author: LSJ
'''
from sqlalchemy import Column, func
from sqlalchemy.types import Integer,BigInteger, String, DateTime, Enum
from model.base import Model, Base
from libs import  pyUtility
import datetime
class User(Model,Base):
    __tablename__ = "py_users"
    ID = Column(BigInteger, primary_key=True)
    user_login = Column("user_login", String(30))
    user_pass = Column("user_pass", String(64)) 
    user_email = Column("user_email", String(100)) 
    user_url = Column("user_url", String(100), default="")
    user_registered = Column("user_registered", DateTime ,default=str(datetime.date.today())) 
    user_status = Column("user_status", Integer, default=0) 
    display_name = Column("display_name", String(50), default="unknown")
    user_activation_key = Column("user_activation_key", String(64), default="")
    user_reset_token = Column("user_reset_token", String(64), default="")
    reset_expired = Column("reset_expired", Integer, default=0)
    role = Column('role', Enum('normal','admin','manager'), default="normal")
    login_from = Column("login_from", String(20), default="local")

    def Login(self, acc, password):
        s = self.session
        q = s.query(self.__class__)
        d = q.filter(self.__class__.user_login == acc).first()
        s.close()
        if d is None:
            return None
        pwd = pyUtility.md5(password)
        if d.user_pass == pwd:
            return d
        return None
    def isEmailUnique(self,email, close=True):
        if email == '':
            return False
        s = self.session
        q = s.query(self.__class__)
        total = q.filter(self.__class__.user_email == email).count()
        if close:
            s.close()
        if total == 0:
            return True
        return False
    def isUnique(self,**props):
        email = props.get('email', '')
        acc = props.get('acc', '')
        if email == '' or acc == '':
            return False
        # print acc, email
        s = self.session
        q = s.query(func.count(self.__class__.ID))
        r = q.filter((self.__class__.user_login == acc) | (self.__class__.user_email == email)).first()
        total = 0
        if not r is None:
            total = r[0]
        s.close()
        #print total
        if total == 0:
            return True
        return False
    def getByID(self, uID, close=True):
        s = self.session
        q = s.query(self.__class__)
        d = q.filter(self.__class__.ID == uID).first()
        if close:
            s.close()
        return d
    def getByEmail(self, email, close=True):
        s = self.session
        q = s.query(self.__class__)
        user = q.filter(self.__class__.user_email == email).first()
        if close:
            s.close()
        if user is None:
            return None
        return user
    def getByResetToken(self, token, close=True):
        s = self.session
        q = s.query(self.__class__)
        d = q.filter(self.__class__.user_reset_token == token).first()
        if close:
            s.close()
        return d
    def getByActivateToken(self, token, close=True):
        s = self.session
        q = s.query(self.__class__)
        d = q.filter(self.__class__.user_activation_key == token).first()
        if close:
            s.close()
        return d
    def getStatGrpByRole(self):
        s = self.session
        r = s.query(func.count(self.__class__.ID), self.__class__.role).group_by(self.__class__.role).all()
        s.close()
        return r
    def searchByRole(self, k, start, limit):
        s = self.session
        total=0
        if k=="":
            total = self.getCount()
        else:
            r = s.query(func.count(self.__class__.ID)).filter(self.__class__.role == k).first()
            if not r is None:
                total = r[0]
        if total ==0:
            r=[]
        else:
            if k=="":
                r = s.query(self.__class__).order_by(self.__class__.user_registered).offset(start).limit(limit).all()
            else:
                r = s.query(self.__class__).filter(self.__class__.role == k).order_by(self.__class__.user_registered).offset(start).limit(limit).all()
        ret = dict(total=total,data=r)
        s.close()
        return ret
    def searchByKeyword(self, k, start, limit):
        s = self.session
        total=0
        if k=="":
            total = self.getCount()
        else:
            r = s.query(func.count(self.__class__.ID)).filter(self.__class__.user_login.like("%"+k+"%")).first()
            if not r is None:
                total = r[0]
        if total ==0:
            r=[]
        else:
            if k=="":
                r = s.query(self.__class__).order_by(self.__class__.user_registered).offset(start).limit(limit).all()
            else:
                r = s.query(self.__class__).filter(self.__class__.user_login.like("%"+k+"%")).order_by(self.__class__.user_registered).offset(start).limit(limit).all()
        ret = dict(total=total,data=r)
        s.close()
        return ret

    def getUsers(self, **kwargs):
        start = kwargs.get('start', 0)
        limit = kwargs.get('limit', 10)
        s = self.session
        q = s.query(self.__class__)
        r = q.order_by(self.__class__.user_registered).offset(start).limit(limit).all()
        s.close()
        return r
    def getCount(self):
        s = self.session
        r = s.query(func.count(self.__class__.ID)).first()
        t = 0
        if r:
            t = r[0]
        s.close()
        return t
    def getRecentJoinMembers(self):
        s = self.session
        q = s.query(self.__class__)
        r = q.order_by(self.__class__.user_registered).limit(10).all()
        s.close()
        return r
    def setStatusUsersByIDs(self, ids, value):
        if not ids:
            return
        stmt = self.__table__.update().where(self.__class__.ID.in_(ids)).values(user_status=value)
        s=self.session
        try:
            s.execute(stmt)
            s.commit()
        except:
            pass
        finally:
            s.close()
    def delUsersByIDs(self, ids):
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
    def getEncodeStr(self, pwd):
        return pyUtility.md5(pwd)
    def __repr__(self):
        return "User"
 
