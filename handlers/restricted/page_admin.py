from handlers.base import BaseHandler
from model.Post import Post
from model.Media import Media
from handlers.module import loginRequired
from libs import pyUtility, pyEnum
import datetime
class PageEditHandler(BaseHandler):
    @loginRequired (roles=[pyEnum.AccountRole.Manager])
    def get(self, id):

        pics = Media().searchByKeyword("",0,1,self.userID)
        paginate = pyUtility.generate_paging_data(start=0,limit=1,total=pics['total'])
        user = self.get_current_user()
        nextmove = self.get_request("nextmove","")
        data = None
        if id:
            if (user['role'] == pyEnum.AccountRole.Admin or user['role'] == pyEnum.AccountRole.Manager):
                data=Post().getByPageID(id,0,True)
            else:
                data=Post().getByPageID(id, user['ID'])
        dic=dict()
        dic['title'] = "Page Edit"
        dic['isAdd'] = False
        dic['nextmove'] = nextmove
        dic['data'] = data

        dic['pics'] = pics['data']
        dic['picsTotal'] = pics['total']
        dic['pages'] = paginate

        self.render("page/add_edit.html", **dic)
    @loginRequired (roles=[pyEnum.AccountRole.Manager])
    def post(self, id):
        title = self.get_request("post_title","untitled")
        content = self.get_request("post_content","")
        post_status = self.get_request("post_status","public")
        post_status = getPostStatus(post_status)
        post_password = self.get_request("post_password","")
        post_delete = self.get_int_request("p_delete",0)
        content = pyUtility.html_purify(content)
        permalink = self.get_request("post_permalink","")

        nextmove = self.get_request("nextmove","")

        if not pyUtility.isPermaLinkLegal(permalink) or permalink =="":
            dic=dict()
            dic['title'] = "Page Edit"
            dic['error'] = "Permalink is not legal."
            dic['isAdd'] = False
            dic['data'] = None
            dic['nextmove'] = nextmove
            self.render("page/add_edit.html", **dic)
            return

        user = self.get_current_user()
        r = None
        dic = dict()
        if id !=0:
            if (user['role'] == pyEnum.AccountRole.Admin or user['role'] == pyEnum.AccountRole.Manager):
                r=Post().getByPageID(id, 0, True, False)
            else:
                r=Post().getByPostID(id, user['ID'], False)
        if r == None:
            dic['title'] = "Page Edit"
            dic['error'] = "The record can not be found or you don't have permission to edit it."
            dic['isAdd'] = False
            dic['data'] = None
            dic['nextmove'] = nextmove
            self.render("page/add_edit.html", **dic)
            return

        if post_status == 'protect':
            r.post_password = pyUtility.md5(post_password)

        r.post_title = title
        r.post_content = content
        r.post_status = post_status
        r.post_modified = str(datetime.datetime.now())
        r.deleted = post_delete
        r.permalink = permalink
        if not r.update():
            dic['error'] = "Page Edit Failed!!"
            dic['isAdd'] = False
            dic['data'] = None
            dic['nextmove'] = nextmove
            self.render("topic/add_edit.html", **dic)
            return
        if nextmove:
            self.redirect(self.webroot_url(nextmove))
        else:
            self.redirect(self.webroot_url("page/"+permalink))
class PageAddHandler(BaseHandler):
    @loginRequired (roles = [pyEnum.AccountRole.Manager])
    def get(self):

        s = self.get_int_request("s",0)
        pics = Media().searchByKeyword("",s,1,self.userID)
        paginate = pyUtility.generate_paging_data(start=s,limit=1,total=pics['total'])
        nextmove = self.get_request("nextmove","")
        dic=dict()
        dic['title'] = "Page Add"
        dic['isAdd'] = True
        dic['nextmove'] = nextmove
        dic['pics'] = pics['data']
        dic['picsTotal'] = pics['total']
        dic['pages'] = paginate
        dic['data'] = None
        self.render("page/add_edit.html", **dic)
    @loginRequired (roles = [pyEnum.AccountRole.Manager])
    def post(self):
        title = self.get_request("post_title","untitled")
        t = self.get_request("post_content","")
        content = pyUtility.html_purify(t)
        t = self.get_request("post_status","public")
        post_status = getPostStatus(t)
        post_password = self.get_request("post_password","")
        permalink = self.get_request("post_permalink","")

        nextmove = self.get_request("nextmove","")
        if not pyUtility.isPermaLinkLegal(permalink) or permalink =="":
            dic=dict()
            dic['title'] = "Page Add"
            dic['error'] = "Permalink is not legal."
            dic['isAdd'] = True
            dic['data'] = None
            dic['nextmove'] = nextmove
            self.render("page/add_edit.html", **dic)
            return
        # check
        if not Post().isPageSlugUnique(permalink):
            dic=dict()
            dic['title'] = "Page Add"
            dic['error'] = "Permalink has been used."
            dic['isAdd'] = True
            dic['data'] = None
            dic['nextmove'] = nextmove
            self.render("page/add_edit.html", **dic)
            return
        ndata = Post()
        if post_status == 'protect':
            ndata.post_password = pyUtility.md5(post_password)
        ndata.post_title = title
        ndata.post_type = 'page'
        ndata.post_author = self.userID
        ndata.post_content = content
        ndata.permalink = permalink
        ndata.post_status = post_status
        ndata.comment_status = "close"
        if ndata.save()<=0:
            dic=dict()
            dic['title'] = "Page Add"
            dic['error'] = "Post Add Failed!!"
            dic['isAdd'] = True
            dic['data'] = None
            dic['nextmove'] = nextmove
            self.render("page/add_edit.html", **dic)
            return
        if nextmove:
            self.redirect(self.webroot_url(nextmove))
        else:
            self.redirect(self.webroot_url("page/"+permalink))






def getPostStatus(v):
    if v == 'protect':
        return 'protect'
    if v == 'private':
        return 'private'
    return 'public'