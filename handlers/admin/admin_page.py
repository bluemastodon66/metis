from handlers.base import BaseHandler
from model.TermTaxonomy import TermTaxonomy
from model.TermRelationships import TermRelationships
from model.Post import Post
from handlers.module import loginRequired

from libs import pyUtility, pyEnum


class PagesAdminHandler(BaseHandler):
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
        if mod=="delete":
            parameters="mod=delete"
            mode='delete'
            res=Post().getDeletedPage(keyword,start,limit)
        else:
            mode='normal'
            parameters="mod=normal"
            res=Post().adminSearchPage(keyword,start,limit)
            parameters=parameters+"&k="+keyword
        pagers = pyUtility.generate_paging_data(start=start,limit=limit,total=res['total'])
        d = []
        if res['data']:
            for tRec in res['data']:
                tmp = tRec.row2dict()
                tmp['user'] = tRec.user
                d.append(tmp)
        dic= {}
        dic['title']='Page List'
        dic['posts']= d
        dic['mode'] = mode
        dic['total']=res['total']
        dic['parameter']= parameters
        dic['nextmove']="admin/pages/"
        dic['pages']= pagers
        dic['keyword']=keyword
        self.render("admin/admin_pages.html", **dic)

    def post(self):
        nextmove = self.get_request("nextmove","")
        act=self.get_request("action","")
        ids=self.get_arguments("post_ids","")
        if act == "delete":
            terms = Post().getTermsIDsByPostsIDs(ids)
            Post().delPostsByIDs(ids)
            TermRelationships().removeAllByPostsIDs(ids)
            if terms:
                TermTaxonomy().calculatePostCountByTermIDs(terms)
        if act == 'recycle':
            Post().setRecyclePostsByIDs(ids, 1)
        if act == 'derecycle':
            Post().setRecyclePostsByIDs(ids, 0)

        self.redirect(self.webroot_url("admin/pages/?"+nextmove))




def getPostStatus(v):
    if v == 'protect':
        return 'protect'
    if v == 'private':
        return 'private'
    return 'public'