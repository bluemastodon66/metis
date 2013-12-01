from handlers.base import BaseHandler
from model.TermTaxonomy import TermTaxonomy
from model.TermRelationships import TermRelationships
from model.Post import Post
from model.Media import Media
from handlers.module import loginRequired

from libs import pyUtility, pyEnum
import datetime

class TopicsEditHandler(BaseHandler):
    @loginRequired ()
    def get(self, id):
        pics = Media().searchByKeyword("",0,1,self.userID)
        paginate = pyUtility.generate_paging_data(start=0,limit=1,total=pics['total'])

        nextmove = self.get_request("nextmove","")
        user = self.get_current_user()
        catOptions=[]
        data = None
        categories=[]
        tags=[]
        if id !=0:
            if (user['role'] == pyEnum.AccountRole.Admin or user['role'] == pyEnum.AccountRole.Manager):
                r=Post().getByID(id)
            else:
                r=Post().getByPostID(id)
            if r:
                data=r['Post']
                ckmap={}
                tags=r['Tags']
                categories=r['Categories']
                for item in r['Categories']:
                        ckmap[str(item['id'])]=True
                cat = TermTaxonomy().getByTaxnonomyName("category")
                for c in cat:
                    ckStr=""
                    if str(c['ID']) in ckmap:
                        ckStr="checked"
                    catOptions.append({'ID':c['ID'],'slug':c['slug'], 'chk':ckStr})
        dic=dict()
        dic['title'] = "Post Edit"
        dic['isAdd'] = False
        dic['data'] = data
        dic['categories']=categories
        dic['nextmove']=nextmove
        dic['tags']=tags
        dic['catOptions']=catOptions

        dic['pics'] = pics['data']
        dic['picsTotal'] = pics['total']
        dic['pages'] = paginate

        self.render("topic/add_edit.html", **dic)
    @loginRequired ()
    def post(self, id):
        title = self.get_request("post_title","untitled")
        content = self.get_request("post_content","")
        post_status = self.get_request("post_status","public")
        post_status = getPostStatus(post_status)
        post_password = self.get_request("post_password","")
        post_tags = self.get_request("post-tags","")
        catgory_array = self.get_arguments("post-category","") # array
        post_delete = self.get_int_request("p_delete",0)
        comment_status = self.get_request("p_feedback","")
        nextmove = self.get_request("nextmove","")
        if comment_status !="open":
            comment_status ="close"

        content = pyUtility.html_purify(content)
        user = self.get_current_user()
        crsf = self.get_request("_xsrf","")
        user_crsf = self.get_cookie("_xsrf","unknown")
        self.clear_cookie("_xsrf")

        if crsf != user_crsf or user_crsf =="unknown":
            self.redirect(self.webroot_url("topic/"))
            return

        r = None
        dic = dict()
        if id !=0:
            if (user['role'] == pyEnum.AccountRole.Admin or user['role'] == pyEnum.AccountRole.Manager):
                r=Post().getByID(id, False)
            else:
                r=Post().getByPostID(id, self.userID, False)

        if r == None:
            dic['title'] = "Post Edit"
            dic['error'] = "The record can not be found or you don't have permission to edit it."
            dic['isAdd'] = False
            dic['data'] = None
            self.render("topic/add_edit.html", **dic)
            return

        if post_status == 'protect':
            r['Post'].post_password = pyUtility.md5(post_password)

        r['Post'].post_title = title
        r['Post'].post_content = content
        r['Post'].post_status = post_status
        r['Post'].post_modified = str(datetime.datetime.now())
        r['Post'].deleted = post_delete
        r['Post'].comment_status = comment_status
        if not r['Post'].update():
            dic['error'] = "Post Edit Failed!!"
            dic['isAdd'] = False
            dic['data'] = None
            dic['nextmove'] =nextmove
            self.render("topic/add_edit.html", **dic)
            return
        # org cats and tags
        org_terms = []
        for tag in r['Tags']:
            org_terms.append(tag['id'])
        for cat in r['Categories']:
            org_terms.append(cat['id'])



        # add cats/tags and add relations
        tags = post_tags.split(',')
        tags_array =[]
        for tag in tags:
            tag = tag.strip()
            if tag == "":
                continue
            tags_array.append(tag)

        termsIDs = []
        if tags_array:
            TermTaxonomy().insertTags(tags_array)
            tagIDs = TermTaxonomy().getTagIDsByArray(tags_array)
            termsIDs = termsIDs + tagIDs
        if catgory_array:
            termsIDs = termsIDs + catgory_array
        termsIDs = list(set(termsIDs))
        if termsIDs != org_terms:
            TermRelationships().removeAllByPostID(id)
            TermRelationships().addPostTermRelations(id,termsIDs)
            # ReCalculate Count
            updateIDs = list(set(termsIDs+org_terms))
            TermTaxonomy().calculatePostCountByTermIDs(updateIDs)
        if nextmove:
            self.redirect(self.webroot_url(nextmove))
        else:
            self.redirect(self.webroot_url("topic/show/"+str(id)))
class TopicsAddHandler(BaseHandler):
    @loginRequired (roles = [pyEnum.AccountRole.Manager])
    def get(self):
        pics = Media().searchByKeyword("",0,1,self.userID)
        paginate = pyUtility.generate_paging_data(start=0,limit=1,total=pics['total'])
        nextmove = self.get_request("nextmove","")
        catOptions=[]
        cat = TermTaxonomy().getByTaxnonomyName("category")
        for c in cat:
            catOptions.append({'ID':c['ID'],'slug':c['slug'], 'chk':""})

        dic=dict()
        dic['title'] = "Post Add"
        dic['isAdd'] = True
        dic['data'] = None
        dic['tags']=[]
        dic['catOptions'] = catOptions
        dic['nextmove'] = nextmove
        dic['pics'] = pics['data']
        dic['picsTotal'] = pics['total']
        dic['pages'] = paginate

        self.render("topic/add_edit.html", **dic)
    @loginRequired (roles = [pyEnum.AccountRole.Manager])
    def post(self):
        title = self.get_request("post_title","untitled")
        content = self.get_request("post_content","")
        content = pyUtility.html_purify(content)
        post_status = self.get_request("post_status","public")
        post_status = getPostStatus(post_status)
        post_password = self.get_request("post_password","")
        post_tags = self.get_request("post-tags","")
        catgory_array = self.get_arguments("post-category","") # array
        comment_status = self.get_request("p_feedback","")
        nextmove = self.get_request("nextmove","")
        if comment_status !="open":
            comment_status ="close"


        ndata = Post()
        if post_status == 'protect':
            ndata.post_password = pyUtility.md5(post_password)
        ndata.post_title = title
        ndata.post_type = 'post'
        ndata.post_author = self.userID
        ndata.post_content = content
        ndata.post_status = post_status
        ndata.comment_status = comment_status
        newID = ndata.save()
        if newID <= 0:
            dic=dict()
            dic['title'] = "Post Add"
            dic['error'] = "Post Add Failed!!"
            dic['isAdd'] = False
            dic['data'] = None
            dic['nextmove'] = nextmove
            self.render("topic/add_edit.html", **dic)
            return

        # add tags and add relations
        tags = post_tags.split(',')
        tags_array=[]
        for tag in tags:
            tag = tag.strip()
            if tag == "":
                continue
            tags_array.append(tag)

        termsIDs = []
        if tags_array:
            TermTaxonomy().insertTags(tags_array)
            tagIDs = TermTaxonomy().getTagIDsByArray(tags_array)
            termsIDs = termsIDs + tagIDs
        if catgory_array:
            termsIDs = termsIDs + catgory_array
        termsIDs = list(set(termsIDs))
        if termsIDs:
            TermRelationships().removeAllByPostID(newID)
            TermRelationships().addPostTermRelations(newID,termsIDs)
            # ReCalculate Count
            TermTaxonomy().calculatePostCountByTermIDs(termsIDs)
        if nextmove:
            self.redirect(self.webroot_url(nextmove))
        else:
            self.redirect(self.webroot_url("topic/show/"+str(newID)))




def getPostStatus(v):
    if v == 'protect':
        return 'protect'
    if v == 'private':
        return 'private'
    return 'public'