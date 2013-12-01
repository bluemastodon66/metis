from handlers.base import BaseHandler
from model.Post import Post
from model.TermTaxonomy import TermTaxonomy
from libs import pyUtility
import math

class PageShowHandler(BaseHandler):
    def get(self,id):
        self.showByID(id)
    def post(self, id):
        pwd = self.get_request("password","")
        pwd = pyUtility.md5(pwd)
        self.showByID(id, pwd)


    def showByID(self, id, pwd=None):
        error = None
        permission = self.get_permission()
        unlock = False
        userid = self.userID
        d=Post().getByPageSlug(id, userid)
        data=None
        uid=0
        if d:
            data=d
            uid=data.ID
            unlock=self.checkLock(data, pwd)
            if data.post_author == userid:
                permission['edit']=True
                permission['del']=True
        tags = TermTaxonomy().getTags()
        for tag in tags['data']:
            score = math.floor( float(tag['count']) / float(tags['counts']) * 140 + 95)
            tag['size'] = str(score) + "%"

        p=dict(
            title='View Page',
            data=data,
            error=error,
            uid=str(uid),
            unlock=unlock,
            permission=permission,
            categories=TermTaxonomy().getCategories(),
            tags=tags['data']
        )
        self.render("page/single.html",**p)

    def checkLock(self,d, pwd=None):
        if d.post_status != 'protect':
            return True
        unlock = False
        if 'post_id_'+str(d.ID) in self.session:
            unlock=True
        if not unlock and pwd:
            postPwd = d.post_password
            unlock = postPwd == pwd
            if unlock:
                self.session['post_id_'+str(d.ID)] = 1
        return unlock
