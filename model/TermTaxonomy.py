# -*- coding: utf-8 -*-
'''
Created on 2013/6/12

@author: LSJ
'''
from sqlalchemy import Column, func
from sqlalchemy.types import String, BigInteger, Text
from model.base import Model, Base
import model.TermRelationships
from sqlalchemy.sql.expression import and_, desc
import model.Post
class TermTaxonomy(Model,Base):
    __tablename__ = "py_term_taxonomy"
    ID = Column("term_taxonomy_id", BigInteger, primary_key=True)
    taxonomy = Column("taxonomy", String(32), default="")
    slug = Column("slug", String(200), default="")
    description = Column("description", Text, default="")
    parent = Column("parent", BigInteger, default=0)
    count = Column("count", BigInteger ,default=0)
    def before_update(self):
        pass
    def before_insert(self):
        pass
        #print "before inser"+ getattr(self, "description")
    def getTagByID(self, id, close=True):
        s = self.session
        q = s.query(TermTaxonomy)
        conditions = []
        conditions.append(self.__class__.taxonomy == 'post_tag')
        conditions.append(self.__class__.ID == id)
        filters = and_(*conditions)
        rec= q.filter(filters).first()
        result=[]
        if rec:
            result = rec
        if close:
            s.close()
        return result
    def getCategoryByID(self, id, close=True):
        s = self.session
        q = s.query(TermTaxonomy)
        conditions = []
        conditions.append(self.__class__.taxonomy == 'category')
        conditions.append(self.__class__.ID == id)
        filters = and_(*conditions)
        rec= q.filter(filters).first()
        result=[]
        if rec:
            result = rec
        if close:
            s.close()
        return result
    def getCategories(self):
        s = self.session
        q = s.query(TermTaxonomy)
        rec = q.filter(TermTaxonomy.taxonomy == 'category').order_by(TermTaxonomy.slug).limit(100).all()
        record = []
        for r in rec:
            record.append({'slug':r.slug,'count':r.count,'description':r.description})
        if record:
            record.sort(key=lambda d: d['slug'])
        s.close()
        return record
    def getTags(self):
        s = self.session
        q = s.query(TermTaxonomy)
        rec = q.filter(TermTaxonomy.taxonomy == 'post_tag', TermTaxonomy.count > 0).order_by(desc(TermTaxonomy.count)).limit(100).all()
        result = {}
        record = []
        total = 0
        for r in rec:
            total = total + r.count
            record.append({'slug':r.slug,'count':r.count,'description':r.description})
        if record:
            record.sort(key=lambda d: d['slug'])
        result['data'] = record
        result['counts'] = total
        s.close()
        return result
    def searchCategoryByKeyword(self, k, start, limit):
        s = self.session
        total=0
        conditions = []
        conditions.append(self.__class__.taxonomy == 'category')
        conditions.append(self.__class__.slug.like("%"+k+"%"))
        filters = and_(*conditions)
        r = []
        tmp = s.query(func.count(self.__class__.ID)).filter(filters).first()
        if not tmp is None:
            total = tmp[0]
        if total >0:
            r = s.query(self.__class__).filter(filters).order_by(desc(self.__class__.slug)).offset(start).limit(limit).all()
        ret = dict(total=total,data=r)
        s.close()
        return ret

    def searchTagByKeyword(self, k, start, limit):
        s = self.session
        total=0
        conditions = []
        conditions.append(self.__class__.taxonomy == 'post_tag')
        conditions.append(self.__class__.slug.like("%"+k+"%"))
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

    def searchByName(self, name):
        s = self.session
        q = s.query(TermTaxonomy)
        conditions = []
        conditions.append(self.__class__.taxonomy == 'post_tag')
        conditions.append(self.__class__.slug.like(name+"%"))
        filters = and_(*conditions)
        rec = q.filter(filters).limit(50).all()
        result = []
        for r in rec:
            result.append({"id":r.ID,"label":r.slug,"value":r.slug})
        s.close()
        return result
    def getTagIDsByArray(self, arr):
        s = self.session
        q = s.query(TermTaxonomy)
        conditions = []
        conditions.append(self.__class__.taxonomy == 'post_tag')
        conditions.append(self.__class__.slug.in_(arr))
        filters = and_(*conditions)
        rec= q.filter(filters).all()
        result=[]
        for r in rec:
            result.append(r.ID)
        s.close()
        return result
    def getCategoryIDsByArray(self, arr):
        s = self.session
        q = s.query(TermTaxonomy)
        conditions = []
        conditions.append(self.__class__.taxonomy == 'category')
        conditions.append(self.__class__.slug.in_(arr))
        filters = and_(*conditions)
        rec= q.filter(filters).all()
        result=[]
        for r in rec:
            result.append(r.ID)
        s.close()
        return result
    def insertTags(self, arr):
        s = self.session
        q = s.query(TermTaxonomy)
        conditions = []
        conditions.append(self.__class__.taxonomy == 'post_tag')
        conditions.append(self.__class__.slug.in_(arr))
        filters = and_(*conditions)
        r = q.filter(filters).all()
        s.close()
        slugs = []
        if r:
            for s in r:
                slugs.append(s.slug)
        newTags = list(set(arr) - set(slugs))
        if len(newTags) <=0:
            return
        sql_express=[]
        for tag in newTags:
            sql_express.append({'slug':tag,'taxonomy':'post_tag','description':'new'})

        s=self.session
        # bulk insert data # much faster
        try:
            s.execute(self.__table__.insert(),sql_express)
            s.commit()
        except:
            pass
        finally:
            s.close()
    def insertCategories(self, arr):
        s = self.session
        q = s.query(TermTaxonomy)
        conditions = []
        conditions.append(self.__class__.taxonomy == 'category')
        conditions.append(self.__class__.slug.in_(arr))
        filters = and_(*conditions)
        r = q.filter(filters).all()
        s.close()
        slugs = []
        if r:
            for s in r:
                slugs.append(s.slug)
        newCat = list(set(arr) - set(slugs))
        if len(newCat) <=0:
            return
        sql_express=[]
        for cat in newCat:
            sql_express.append({'slug':cat,'taxonomy':'category','description':'new'})
        s=self.session
        # bulk insert data # much faster
        try:
            s.execute(self.__table__.insert(),sql_express)
            s.commit()
        except:
            pass
        finally:
            s.close()
    def getByTaxnonomyName(self, name):
        s = self.session
        q = s.query(TermTaxonomy)
        d = q.filter(self.__class__.taxonomy == name).all()
        ret=[]
        if d:
            for c in d:
                tmp={}
                tmp['ID']=c.ID
                tmp['slug']=c.slug
                tmp['description']=c.description
                tmp['count']=c.count
                tmp['taxonomy']=c.taxonomy
                tmp['parent']= c.parent
                ret.append(tmp)
        s.close()
        return ret
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
    def calculatePostCountByTermIDs(self, arr):
        s = self.session
        q = s.query(TermTaxonomy,model.TermRelationships.TermRelationships.ID, func.count(TermTaxonomy.ID)).outerjoin(model.TermRelationships.TermRelationships)
        d = q.filter(TermTaxonomy.ID.in_(arr)).group_by(TermTaxonomy.slug).all()
        result = []
        for r in d:
            count = r[2]
            if r[1] is None:
                count = 0
            result.append({'id':r[0].ID,'count':count})

        if not result:
            return
        for r in result:
            s = self.session
            try:
                s.query(TermTaxonomy).filter(TermTaxonomy.ID == r['id']).update({"count": r['count']})
                s.commit()
            except:
                pass
            finally:
                s.close()




    def isNodeMovValid(self,name,nodID,patID):
        nodeID=str(nodID)
        parentID=str(patID)
        if parentID==0:
            return True
        if nodeID==parentID:
            return False
        rec=self.getByTaxnonomyName(name)
        mappingTab={}
        # get root node
        queueList=[]
        for r in rec:
            uid = str(r['ID'])
            if r['parent']==0:
                mappingTab[uid]={"path":"["+uid+"]","id":uid}
            else:
                queueList.append(r)
        counter=0
        while(len(queueList) > 0):
            if counter >=9999: # prevent infinite loops
                break
            counter+=1
            r=queueList.pop(0) # pop from begin , normally pop from end if no parameter
            uid = str(r.ID)
            pid = str(r.parent)
            if pid in mappingTab:
                d = mappingTab[pid]
                index = d['id']
                path=d['path']+"["+uid+"]"
                mappingTab[uid]={"path":path,"id":index}
            else:
                queueList.append(r)
        # print mappingTab
        if not parentID in mappingTab:
            return False
        targetPath=mappingTab[parentID]['path']
        if targetPath.find("["+nodeID+"]") != -1:
            return False
        return True


    def __repr__(self):
        return "TermTaxonomy"
 


