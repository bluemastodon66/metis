# -*- coding: utf-8 -*-
'''
Created on 2013/6/12

@author: LSJ
'''
from sqlalchemy import Column, ForeignKey
from sqlalchemy.types import Integer, BigInteger
from model.base import Model, Base
from sqlalchemy.sql.expression import and_
class TermRelationships(Model,Base):
    __tablename__ = 'py_term_relationships'
    ID = Column(Integer, primary_key=True)
    object_id = Column("object_id",BigInteger, ForeignKey('py_posts.ID'))
    term_taxonomy_id = Column("term_taxonomy_id",BigInteger, ForeignKey('py_term_taxonomy.term_taxonomy_id'))
    term_order = Column("term_order", Integer(11), default=0)
    def delPostTermRelations(self, postID, termIDs):
        s = self.session
        conditions = []
        conditions.append(self.__class__.object_id == postID)
        conditions.append(self.__class__.term_taxonomy_id.in_(termIDs))
        filters = and_(*conditions)
        try:
            s.execute(self.__table__.delete().where(filters))
            s.commit()
        except:
            pass
        finally:
            s.close()

    def addPostTermRelations(self, postID, termIDs):
        if not termIDs:
            return
        sql_express=[]
        for term in termIDs:
            sql_express.append({'object_id':postID,'term_taxonomy_id':term,'term_order':0})
        s = self.session
        try:
            s.execute(self.__table__.insert(),sql_express)
            s.commit()
        except:
            pass
        finally:
            s.close()
    def removeAllByTermsIDs(self, ids):
        s = self.session
        try:
            s.execute(self.__table__.delete().where(self.__class__.term_taxonomy_id.in_(ids)))
            s.commit()
        except:
            pass
        finally:
            s.close()
    def removeAllByPostsIDs(self, postIDs):
        s = self.session
        try:
            s.execute(self.__table__.delete().where(self.__class__.object_id.in_(postIDs)))
            s.commit()
        except:
            pass
        finally:
            s.close()
    def removeAllByPostID(self, postID):
        s = self.session
        try:
            s.execute(self.__table__.delete().where(self.__table__.c.object_id == postID))
            s.commit()
        except:
            pass
        finally:
            s.close()
    def __repr__(self):
        return "TermRelationships"
 





