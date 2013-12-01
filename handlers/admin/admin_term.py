# -*- coding: utf-8 -*-
from handlers.base import BaseHandler
from model.TermTaxonomy import TermTaxonomy
from model.TermRelationships import TermRelationships

from handlers.module import loginRequired
from libs import pyEnum, pyUtility
import math
class AdminCategoriesHandler(BaseHandler):

    @loginRequired (roles = [pyEnum.AccountRole.Admin])
    def get(self):
        start = self.get_int_request("s",0)
        keyword = self.get_request("k","")
        act = self.get_request("act","")
        id = self.get_int_request("id",0)
        errorCode = self.get_int_request("error",0)
        parameters=""
        formData = None
        if act=="edit" and id >0:
            tmp=TermTaxonomy().getCategoryByID(id)
            if tmp:
                formData=tmp.row2dict()
                parameters="?act=edit&id="+str(id)
        else:
            act="add"
            parameters = "?act=add"
        limit=20

        records = TermTaxonomy().searchCategoryByKeyword(keyword,start,limit)
        total = records['total']

        if total > limit:
            pagers = pyUtility.generate_paging_data(start=start,limit=limit,total=total)
        else:
            pagers = []

        data = []
        counter = 1 + int(math.floor(start/limit)) * limit
        if not records is None:
            for r in records['data']:
                tmp = r.row2dict()
                tmp["no"] = counter
                counter+=1
                data.append(tmp)
        error=None
        if errorCode==1:
            error="error when update, some field must be unique"
        if errorCode==2:
            error="error when add, some fields must be unique"

        p=dict(
            title='Category Management',
            records=data,
            error=error,
            parameters=parameters,
            formData=formData,
            act=act,
            keyword=keyword,
            pages=pagers,
            totalData=total
        )
        self.render("admin/admin_category.html",**p)
    def post(self):
        slug = self.get_request("slug","")
        description = self.get_request("description","")
        nextmove = self.get_request("nextmove","")
        act = self.get_request("act","")
        id = self.get_int_request("id",0)
        ids = self.get_arguments("ids")

        error=0
        if act=="delete":
            nextmove="?act="
            if ids:
                TermTaxonomy().delByIDs(ids)
                TermRelationships().removeAllByTermsIDs(ids)
        else:
            if slug =="":
                error=1
            else:
                error=0
                if act == "edit":
                    old = TermTaxonomy().getCategoryByID(id, False)
                    if old:
                        old.slug = slug
                        old.description = description
                        if not old.update():
                            error=1
                if act == "add":
                    nextmove="?act=add"
                    newone = TermTaxonomy()
                    newone.slug = slug
                    newone.taxonomy = 'category'
                    newone.description = description
                    if newone.save() <=0:
                        error=2
                    else:
                        error=2
                if act == "delete":
                    nextmove="?act=del"
        self.redirect(self.get_webroot_url()+"admin/categories/"+nextmove+"&error="+str(error))



class AdminTagsHandler(BaseHandler):
    @loginRequired (roles = [pyEnum.AccountRole.Admin])
    def get(self):
        start = self.get_int_request("s",0)
        keyword = self.get_request("k","")
        act = self.get_request("act","")
        id = self.get_int_request("id",0)
        errorCode = self.get_int_request("error",0)
        parameters=""
        formData = None
        if act=="edit" and id >0:
            tmp=TermTaxonomy().getTagByID(id)
            if tmp:
                formData=tmp.row2dict()
                parameters="?act=edit&id="+str(id)
        else:
            act="add"
            parameters = "?act=add"
        limit=10

        records = TermTaxonomy().searchTagByKeyword(keyword,start,limit)
        total = records['total']

        if total > limit:
            pagers = pyUtility.generate_paging_data(start=start,limit=limit,total=total)
        else:
            pagers = []

        data = []
        counter = 1 + int(math.floor(start/limit)) * limit
        if not records is None:
            for r in records['data']:
                tmp = r.row2dict()
                tmp["no"] = counter
                counter+=1
                data.append(tmp)
        error=None
        if errorCode==1:
            error="error when update, some field must be unique"
        if errorCode==2:
            error="error when add, some fields must be unique"

        p=dict(
            title='Category Management',
            records=data,
            error=error,
            parameters=parameters,
            formData=formData,
            act=act,
            keyword=keyword,
            pages=pagers,
            totalData=total
        )
        self.render("admin/admin_tag.html",**p)
    def post(self):
        slug = self.get_request("slug","")
        nextmove = self.get_request("nextmove","")
        act = self.get_request("act","")
        id = self.get_int_request("id",0)
        ids = self.get_arguments("ids")
        error=0
        if act=="delete":
            nextmove="?act="
            if ids:
                TermTaxonomy().delByIDs(ids)
                TermRelationships().removeAllByTermsIDs(ids)

        else:
            if slug =="":
                error=1
            else:
                error=0
                if act == "edit":
                    old = TermTaxonomy().getTagByID(id, False)
                    if old:
                        old.slug = slug
                        if not old.update():
                            error=1
                if act == "add":
                    nextmove="?act=add"
                    newone = TermTaxonomy()
                    newone.slug = slug
                    newone.taxonomy = 'post_tag'
                    if newone.save() <=0:
                        error=2
        self.redirect(self.get_webroot_url()+"admin/tags/"+nextmove+"&error="+str(error))


