from handlers.base import BaseHandler
from model.TermTaxonomy import TermTaxonomy
from model.TermRelationships import TermRelationships
from model.Post import Post
from handlers.module import loginRequired

from libs import pyUtility, pyEnum

class TopicsAdminHandler(BaseHandler):
    @loginRequired (roles = [pyEnum.AccountRole.Manager])
    def get(self):
        start = self.get_int_request("s",0)
        keyword=self.get_request("k","")
        act=self.get_request("act","")
        mod=self.get_request("mod","")
        id=self.get_int_request("id",0)
        mode=''

        limit= 50
        if start < 0:
            start=0
        if act=="user":
            parameters="act=user&id="+str(id)
            res=Post().getByAuthorID(id,start,limit, id, True)
        else:
            if mod=="delete":
                parameters="mod=delete"
                mode='delete'
                res=Post().getDeletedPost(keyword,start,limit)
            else:
                mode='normal'
                parameters="mod=normal"
                res=Post().searchByKeyword(keyword,start,limit, 0, True)

            parameters=parameters+"&k="+keyword
        pagers = pyUtility.generate_paging_data(start=start,limit=limit,total=res['total'])
        d = []
        if res['data']:
            for tRec in res['data']:
                tmp = tRec.row2dict()
                tmp['user'] = tRec.user
                d.append(tmp)
        dic= {}
        dic['title']='Post List'
        dic['posts']= d
        dic['mode'] = mode
        dic['total']=res['total']
        dic['nextmove']='admin/topics/'
        dic['parameter']= parameters
        dic['pages']= pagers
        dic['keyword']=keyword
        self.render("admin/admin_topics.html", **dic)

    def post(self):
        nextmove = self.get_request("nextmove","")
        act=self.get_request("action","")
        ids=self.get_arguments("post_ids","")
        if act == "delete":
            Post().delPostsByIDs(ids)
        if act == 'recycle':
            Post().setRecyclePostsByIDs(ids, 1)
        if act == 'derecycle':
            Post().setRecyclePostsByIDs(ids, 0)

        self.redirect(self.webroot_url("admin/topics/?"+nextmove))


