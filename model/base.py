'''
Created on 2013/6/13

@author: LSJ
'''
from tornado.options import options
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.interfaces import MapperExtension


Base = declarative_base()
 
class Singleton(object):
 
    '''
 
    Singelton class
 
    '''
 
    def __init__(self, decorated):
 
        self._decorated = decorated
 
    def instance(self, *args, **kwargs):
 
        try:
 
            return self._instance
 
        except AttributeError:
 
            self._instance = self._decorated(*args, **kwargs)
 
            return self._instance
 
    def __call__(self, *args, **kwargs):
 
        raise TypeError('Singletons must be accessed through the `Instance` method.')
 
@Singleton
 
class Db(object):
 
    '''
 
    The DB Class should only exits once, thats why it has the @Singleton decorator.
    To Create an instance you have to use the instance method:
        db = Db.instance()
    '''
    engine = None
    session = None
    def __init__(self):
        self.engine = create_engine("mysql://{0}:{1}@{2}/{3}?charset=utf8".format(options.mysql_user, options.mysql_password, options.mysql_host, options.mysql_database)
                            , pool_size=options.mysql_poolsize
                            , pool_recycle=3600
                            , encoding='utf-8'
                            , echo=options.debug
                            , echo_pool=options.debug)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        # # Create all Tables
        Base.metadata.create_all(self.engine)
        print "Create New Session For DB Connection"
    def instance(self, *args, **kwargs):
 
        '''
 
        Dummy method, cause several IDEs can not handel singeltons in Python
 
        '''
 
        pass

class BaseExtension(MapperExtension):
    """Base entension class for all entity """
    def before_insert(self, mapper, connection, instance):
        instance.before_insert()
    def before_update(self, mapper, connection, instance):
        pass
        print "after _begin"
class Model():
 
    '''
 
    This is a baseclass with delivers all basic database operations
 
    '''
    __mapper_args__ = { 'extension': BaseExtension() }

    def before_insert(self):
        pass
    def before_update(self):
        pass
    def row2dict(self):
        d = {}
        values = vars(self)
        for attr in self.__mapper__.columns.keys():
            if attr in values:
                d[attr]= values[attr]
        return d
    def save(self):
        db = Db.instance()
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
    def saveMultiple(self, objects=[]):
        db = Db.instance()
        try:
            db.session.add_all(objects)
            db.session.commit()
            flag=True
        except:
            db.session.rollback()
        finally:
            db.session.close()
        return flag
    def update(self):
        db = Db.instance()

        try:
            db.session.commit()
            flag=True
        except:
            flag=False
            db.session.rollback()
        finally:
            db.session.close()
        return flag
    def delete(self):
        db = Db.instance()
        try:
            db.session.delete(self)
            db.session.commit()
            flag=True
        except:
            flag=False
            db.session.rollback()
        finally:
            db.session.close()
        return flag
    def close(self):
        db = Db.instance()
        db.session.close()
    @property
    def session(self):
        db = Db.instance()
        return db.session
    def queryObject(self):
        db = Db.instance()
        return db.session.query(self.__class__)
 
