# -*- coding: utf-8 -*-
'''
Created on 2013/10/30
Init Connent To DB
@author: LSJ
'''


admin_account = "admin"
admin_pass = "1234"
admin_email = "admin@email.com"
from settings import options
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, func
from sqlalchemy.types import BigInteger, String,Text, DateTime, Integer, Enum
import datetime
from libs import pyUtility
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
    def insertMultiple(self, records):
        if not self.db.session:
            return False
        if not records:
            return
        sql_express=[]
        for t in records:
            sql_express.append({'option_name':t['key'],'option_value':t['val']})
        s = self.db.session
        try:
            s.execute(self.__table__.insert(),sql_express)
            s.commit()
        except:
            pass
            s.close()
class User(Base):
    db=Db()
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
    def isUnique(self, acc, email):
        if not self.db.session:
            return False
        s = self.db.session
        q = s.query(func.count(self.__class__.ID))
        r = q.filter((self.__class__.user_login == acc) | (self.__class__.user_email == email)).first()
        total = 0
        if not r is None:
            total = r[0]
        if total == 0:
            return True
        return False
    def save(self):
        if not self.db.session:
            return False
        db = Db()
        flag =0
        try:
            db.session.add(self)
            db.session.commit()
            flag=self.ID
        except:
            db.session.rollback()
        finally:
            db.session.close()
        return flag
    def getEncodeStr(self, pwd):
        return pyUtility.md5(pwd)
print ""
print ""
print "*************************"
print "* installation begins"
print "-------------------------"
rec = Option().getAll(100)
if not rec:
    newData=[]
    newData.append({'key':'web_title','val':'Metis'})
    newData.append({'key':'site_name','val':'Metis'})
    newData.append({'key':'description','val':'Metis Blog'})
    newData.append({'key':'users_can_register','val':'1'})
    newData.append({'key':'version','val':'1.0'})
    newData.append({'key':'thumb_width','val':'100'})
    newData.append({'key':'thumb_height','val':'0'})
    newData.append({'key':'admin_email','val':admin_email})
    Option().insertMultiple(newData)
    print "Initialize...."

print "* checking admin account"

chk = User().isUnique("admin","admin@email.com")
if chk:
    print "* there is no admin account. Let's create one"
    user = User()
    newPwd = user.getEncodeStr(admin_pass)
    user.user_login = admin_account
    user.user_pass = newPwd
    user.user_email = admin_email
    user.user_url = ""
    user.role = 'admin'
    user.user_status = 1
    user.display_name = "Super User"
    newID = user.save()
    if newID >0:
        print "* Admin User Created"
        print "* install successfully"
    else:
        print "* Error:: Creating Admin User Has failed"
else:
    print "* Admin Account has existed"
    print "* You may have already installed before."
print "-------------------------"

print ""
print ""
