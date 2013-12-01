# -*- coding: utf-8 -*-
'''
Created on 2013/6/12

@author: LSJ
'''
from sqlalchemy import Column, func
from sqlalchemy.types import Integer, String, DateTime, BigInteger, Text
from sqlalchemy.orm import relationship
from model.base import Model, Base
from sqlalchemy.sql.expression import desc, and_
import datetime
import model.TermRelationships
import model.TermTaxonomy

class Post(Model,Base):

    __tablename__ = "py_posts"
    ID = Column(BigInteger, primary_key=True)
    post_author = Column("post_author", BigInteger, default=0)
    post_date = Column("post_date", DateTime, default=str(datetime.datetime.now()))
    post_content = Column("post_content", Text, default="")
    post_title = Column("post_title", Text, default="")
    post_status = Column("post_status", String(20) ,default="public")
    comment_status = Column("comment_status", String(20), default="open")
    post_password = Column("post_password", String(64), default="")
    post_modified = Column('post_modified',DateTime ,default=str(datetime.datetime.now()))
    post_parent = Column("post_parent",BigInteger, default=0)
    permalink = Column("permalink", String(255), default="")
    menu_order = Column("menu_order", Integer, default=0)
    deleted = Column("deleted", Integer, default=0)
    post_type = Column("post_type", String(20), default="post")
    # comment_count = Column("comment_count", BigInteger, default=0)
    user = relationship("User", primaryjoin="Post.post_author==User.ID", foreign_keys=post_author, lazy="joined")
    def getByPageSlug(self, slug, userid):
        conditions = []
        if userid > 0:
            conditions.append((self.__class__.post_status != 'private') | (self.__class__.post_author == userid))
            conditions.append((self.__class__.deleted == 0) | (self.__class__.post_author == userid))
        else:
            conditions.append(self.__class__.post_status != 'private')
            conditions.append(self.__class__.deleted == 0)
        conditions.append(self.__class__.post_type == 'page')
        conditions.append(self.__class__.permalink == slug)
        conditions.append(self.__class__.permalink != "")
        conditions.append(self.__class__.permalink != None)
        filters = and_(*conditions)
        s = self.session
        q = s.query(Post)
        d = q.filter(filters).first()
        s.close()
        return d
    def isPageSlugUnique(self,slug):
        if slug == '':
            return False
        # print acc, email
        s = self.session
        q = s.query(func.count(self.__class__.ID))
        r = q.filter(self.__class__.permalink == slug).first()
        s.close()
        total =0
        if r:
            total=r[0]
        if total == 0:
            return True
        return False
    def getByPageID(self, uid, userid, isAdmin=False, close=True):
        conditions = []
        if not isAdmin:
            if userid > 0:
                conditions.append((self.__class__.post_status != 'private') | (self.__class__.post_author == userid))
                conditions.append((self.__class__.deleted == 0) | (self.__class__.post_author == userid))
            else:
                conditions.append(self.__class__.post_status != 'private')
                conditions.append(self.__class__.deleted == 0)

        conditions.append(self.__class__.post_type == 'page')
        conditions.append(self.__class__.ID == uid)
        filters = and_(*conditions)
        s = self.session
        q = s.query(Post)
        d = q.filter(filters).first()
        if close:
            s.close()
        return d
    def getDeletedPage(self, k, start, limit):
        s = self.session
        total=0
        conditions = []
        conditions.append(self.__class__.deleted ==1)
        conditions.append(self.__class__.post_type == 'page')
        if k != "":
            conditions.append((self.__class__.post_title.like("%"+k+"%")) | (self.__class__.post_content.like("%"+k+"%")))
        filters = and_(*conditions)
        r = []
        tmp = s.query(func.count(self.__class__.ID)).filter(filters).first()
        if not tmp is None:
            total = tmp[0]
        if total >0:
            r = s.query(self.__class__).filter(filters).order_by(desc(self.__class__.post_date)).offset(start).limit(limit).all()
        ret = dict(total=total,data=r)
        s.close()
        return ret
    def adminSearchPage(self, k, start, limit):
        s = self.session
        total=0
        conditions = []
        conditions.append(self.__class__.deleted ==0)
        conditions.append(self.__class__.post_type == 'page')
        if k != "":
            conditions.append((self.__class__.post_title.like("%"+k+"%")) | (self.__class__.post_content.like("%"+k+"%")))
        filters = and_(*conditions)
        r = []
        tmp = s.query(func.count(self.__class__.ID)).filter(filters).first()
        if not tmp is None:
            total = tmp[0]
        if total >0:
            r = s.query(self.__class__).filter(filters).order_by(desc(self.__class__.post_date)).offset(start).limit(limit).all()
        ret = dict(total=total,data=r)
        s.close()
        return ret
    def getPostByIDforPwdCheck(self,uid, pwd):
        conditions = []
        conditions.append(self.__class__.post_status == 'protect')
        conditions.append(self.__class__.deleted == 0)
        conditions.append(self.__class__.post_type == 'post')
        conditions.append(self.__class__.ID == uid)
        conditions.append(self.__class__.post_password == pwd)
        filters = and_(*conditions)
        s = self.session
        q = s.query(Post.ID)
        d = q.filter(filters).first()
        s.close()
        return d
    def getPostShortInfo(self,uid):
        conditions = []
        conditions.append(self.__class__.post_status != 'private')
        conditions.append(self.__class__.deleted == 0)
        conditions.append(self.__class__.post_type == 'post')
        conditions.append(self.__class__.ID == uid)
        filters = and_(*conditions)
        s = self.session
        q = s.query(Post)
        d = q.filter(filters).first()
        s.close()
        return d
    def getByPostID(self, uid, userid, close=True):
        conditions = []
        if userid > 0:
            conditions.append((self.__class__.post_status != 'private') | (self.__class__.post_author == userid))
            conditions.append((self.__class__.deleted == 0) | (self.__class__.post_author == userid))
        else:
            conditions.append(self.__class__.post_status != 'private')
            conditions.append(self.__class__.deleted == 0)

        conditions.append(self.__class__.post_type == 'post')
        conditions.append(self.__class__.ID == uid)
        filters = and_(*conditions)
        s = self.session
        q = s.query(Post, model.TermTaxonomy.TermTaxonomy).\
            outerjoin(model.TermRelationships.TermRelationships).\
            outerjoin(model.TermTaxonomy.TermTaxonomy)
        d = q.filter(filters).all()
        #process data into array
        if d:
            tmp={}
            tmp['Post']=d[0].Post
            tmp['Categories']=[]
            tmp['Tags']=[]
            for r in d:
                if r.TermTaxonomy:
                    if r.TermTaxonomy.taxonomy == 'category':
                        tmp['Categories'].append({"id":r.TermTaxonomy.ID,"slug":r.TermTaxonomy.slug})
                    else:
                        tmp['Tags'].append({"id":r.TermTaxonomy.ID,"slug":r.TermTaxonomy.slug})
        else:
            tmp=None
        if close:
            s.close()
        return tmp

    def getByID(self, uID, close=True):
        s = self.session
        q = s.query(Post, model.TermTaxonomy.TermTaxonomy).\
            outerjoin(model.TermRelationships.TermRelationships).\
            outerjoin(model.TermTaxonomy.TermTaxonomy)
        d = q.filter(self.__class__.ID == uID).all()
        #process data into array
        if d:
            tmp={}
            tmp['Post']=d[0].Post
            tmp['Categories']=[]
            tmp['Tags']=[]
            for r in d:
                if r.TermTaxonomy:
                    if r.TermTaxonomy.taxonomy == 'category':
                        tmp['Categories'].append({"id":r.TermTaxonomy.ID,"slug":r.TermTaxonomy.slug})
                    else:
                        tmp['Tags'].append({"id":r.TermTaxonomy.ID,"slug":r.TermTaxonomy.slug})
        else:
            tmp=None
        if close:
            s.close()
        return tmp

    def getByCategory(self, start, limit, name, userid=0):
        s = self.session
        result={}
        result['data'] = []
        result['total'] = self.__getCountByTerm(name,'category', userid)
        if result['total'] >0:
            result['data']= self.__getByTerm(start,limit,name,'category',userid)
        s.close()
        return result
    def getByTag(self, start, limit, name, userid=0):
        s = self.session
        result={}
        result['data'] = []
        result['total'] = self.__getCountByTerm(name,'post_tag', userid)
        if result['total'] >0:
            result['data']= self.__getByTerm(start,limit,name,'post_tag',userid)
        s.close()
        return result
    def __getCountByTerm(self, name, type, userid):
        s = self.session
        conditions = []
        if userid > 0:
            conditions.append((self.__class__.post_status != 'private') | (self.__class__.post_author == userid))
            conditions.append((self.__class__.deleted == 0) | (self.__class__.post_author == userid))

        else:
            conditions.append(self.__class__.post_status != 'private')
            conditions.append(self.__class__.deleted == 0)


        conditions.append(self.__class__.post_type == 'post')
        conditions.append(model.TermTaxonomy.TermTaxonomy.slug == name)
        conditions.append(model.TermTaxonomy.TermTaxonomy.taxonomy == type)
        filters = and_(*conditions)
        q = s.query(func.count(Post.ID)).\
            join(model.TermRelationships.TermRelationships).\
            join(model.TermTaxonomy.TermTaxonomy)
        r = q.filter(filters).one()
        s.close()
        return r[0]
    def __getByTerm(self, start, limit, name, type, userid):
        s = self.session
        conditions = []
        if userid > 0:
            conditions.append((self.__class__.post_status != 'private') | (self.__class__.post_author == userid))
            conditions.append((self.__class__.deleted == 0) | (self.__class__.post_author == userid))

        else:
            conditions.append(self.__class__.post_status != 'private')
            conditions.append(self.__class__.deleted == 0)

        conditions.append(self.__class__.post_type == 'post')
        conditions.append(model.TermTaxonomy.TermTaxonomy.slug == name)
        conditions.append(model.TermTaxonomy.TermTaxonomy.taxonomy == type)

        filters = and_(*conditions)

        q = s.query(Post, model.TermTaxonomy.TermTaxonomy).\
            join(model.TermRelationships.TermRelationships).\
            join(model.TermTaxonomy.TermTaxonomy)
        r = q.filter(filters)\
            .order_by(desc(self.__class__.post_date)).offset(start).limit(limit).all()
        s.close()
        return r
    def getByAuthorID(self, id, start, limit, userid=0, isAdmin=False):
        s = self.session
        total=0
        conditions = []
        if not isAdmin:
            if userid > 0:
                conditions.append((self.__class__.post_status != 'private') | (self.__class__.post_author == userid))
                conditions.append((self.__class__.deleted == 0) | (self.__class__.post_author == userid))
            else:
                conditions.append(self.__class__.post_status != 'private')
                conditions.append(self.__class__.deleted == 0)

        conditions.append(self.__class__.post_author == id)
        conditions.append(self.__class__.post_type == 'post')
        filters = and_(*conditions)
        r = s.query(func.count(self.__class__.ID)).filter(filters).first()
        if not r is None:
            total = r[0]
        if total ==0:
            r=[]
        else:
            r = s.query(self.__class__).filter(filters).order_by(desc(self.__class__.post_date)).offset(start).limit(limit).all()
        ret = dict(total=total,data=r)
        s.close()
        return ret
    def getDeletedPost(self, k, start, limit):
        s = self.session
        total=0
        conditions = []
        conditions.append(self.__class__.deleted ==1)
        conditions.append(self.__class__.post_type == 'post')
        if k != "":
            conditions.append((self.__class__.post_title.like("%"+k+"%")) | (self.__class__.post_content.like("%"+k+"%")))
        filters = and_(*conditions)
        r = []
        tmp = s.query(func.count(self.__class__.ID)).filter(filters).first()
        if not tmp is None:
            total = tmp[0]
        if total >0:
            r = s.query(self.__class__).filter(filters).order_by(desc(self.__class__.post_date)).offset(start).limit(limit).all()
        ret = dict(total=total,data=r)
        s.close()
        return ret
    def getRSS(self, start, limit):
        s = self.session
        conditions = []
        conditions.append(self.__class__.post_status == 'public')
        conditions.append(self.__class__.deleted ==0)
        conditions.append(self.__class__.post_type == 'post')
        filters = and_(*conditions)
        r = s.query(self.__class__).filter(filters).order_by(desc(self.__class__.post_date)).offset(start).limit(limit).all()
        s.close()
        return r
    def searchByKeyword(self, k, start, limit, userid=0, isAdmin=False):
        s = self.session
        total=0
        conditions = []
        if not isAdmin:
            if userid > 0:
                conditions.append((self.__class__.post_status != 'private') | (self.__class__.post_author == userid))
                conditions.append((self.__class__.deleted ==0) | (self.__class__.post_author == userid))
            else:
                conditions.append(self.__class__.post_status != 'private')
                conditions.append(self.__class__.deleted ==0)
        else:
            conditions.append(self.__class__.deleted ==0)

        conditions.append(self.__class__.post_type == 'post')
        if k != "":
            conditions.append((self.__class__.post_title.like("%"+k+"%")) | (self.__class__.post_content.like("%"+k+"%")))
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

    def getCountByAuthorID(self, id):
        s = self.session
        conditions = []
        conditions.append(self.__class__.post_author == id)
        conditions.append(self.__class__.post_type == 'post')
        filters = and_(*conditions)
        r = s.query(func.count(self.__class__.ID)).filter(filters).first()
        t = 0
        if r:
            t = r[0]
        s.close()
        return t

    def setRecyclePostsByIDs(self, ids, value):
        if not ids:
            return
        stmt = self.__table__.update().where(self.__class__.ID.in_(ids)).values(deleted=value)
        s=self.session
        try:
            s.execute(stmt)
            s.commit()
        except:
            pass
        finally:
            s.close()

    def getTermsIDsByPostsIDs(self, ids):
        if not ids:
            return
        s = self.session
        ids = s.query(Post.ID, model.TermRelationships.TermRelationships.term_taxonomy_id).\
            join(model.TermRelationships.TermRelationships).filter(self.__class__.ID.in_(ids)).all()
        termIDS = []
        for termId in ids:
            termIDS.append(termId[1])
        s.close()
        return termIDS

    def delPostsByIDs(self, ids):
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

    def __repr__(self):
        return "Post"
 


