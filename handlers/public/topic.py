from handlers.base import BaseHandler
from model.User import User
from model.Post import Post
from model.TermTaxonomy import TermTaxonomy
from model.Comment import Comment
from libs import pyUtility
import math
class TopicHandler(BaseHandler):
    def get(self):
        start = self.get_int_request("s",0)
        keyword=self.get_request("k","")
        limit=5
        if start < 0:
            start=0
        res=Post().searchByKeyword(keyword,start,limit, self.userID)
        pagers = pyUtility.generate_paging_data(start=start,limit=limit,total=res['total'])

        d = []
        if res['data']:
            for tRec in res['data']:
                tmp = tRec.row2dict()
                tmp['user'] = tRec.user
                tmp['unlock'] = True
                if tmp['post_status'] == 'protect':
                    if 'post_id_'+str(tmp['ID']) not in self.session:
                        tmp['unlock'] = False
                tmp['summary'] = pyUtility.remove_html_tags(tmp['post_content'])
                d.append(tmp)

         # TAGS
        tags = TermTaxonomy().getTags()
        for tag in tags['data']:
            score = math.floor( float(tag['count']) / float(tags['counts']) * 140 + 95)
            tag['size'] = str(score) + "%"

        dic= {}

        dic['title']='Post List'
        dic['posts']= d
        dic['tags'] = tags['data']
        dic['categories'] = TermTaxonomy().getCategories()
        dic['total']=res['total']
        dic['pages']= pagers
        dic['keyword']=keyword
        self.render("topic/main.html", **dic)


class TopicShowHandler(BaseHandler):
    def get(self, id):
        errorCode = self.get_int_request("error",0)
        cs = self.get_int_request("cs",0)
        error = None
        if errorCode == 1:
            error="Failed to add comment, make sure the format is right"
        if errorCode == 2:
            error="Post doesn't exist anymore"
        if errorCode == 3:
            error="Comment has been closed"

        permission = self.get_permission()
        userTopicCount=0
        online=False
        unlock = False
        post_tags=[]
        post_categories=[]
        userid = self.userID
        d=Post().getByPostID(id, userid)
        data=None
        if d:
            data=d['Post']
            unlock=self.checkLock(d['Post'])
            if d['Post'].post_author == userid:
                permission['edit']=True
                permission['del']=True
            if d['Post'].user:
                userTopicCount=Post().getCountByAuthorID(d['Post'].post_author)
                tmp=self.getOnlineUserByID(d['Post'].post_author)
                if tmp:
                    online=True
            post_tags=d['Tags']
            post_categories=d['Categories']
         # TAGS
        tags = TermTaxonomy().getTags()
        for tag in tags['data']:
            score = math.floor( float(tag['count']) / float(tags['counts']) * 140 + 95)
            tag['size'] = str(score) + "%"

        # Comments
        limit=10
        comments = Comment().getList(cs,limit,id)
        if comments['total'] > limit:
            paginate = pyUtility.generate_paging_data(start=cs,limit=limit,total=comments['total'])
        else:
            paginate =None

        p=dict(
            title='View Post',
            data=data,
            error=error,
            uid=str(id),
            comments=comments['data'],
            totalComment=comments['total'],
            paginate=paginate,
            nextmove='id='+str(id),
            post_tags=post_tags,
            post_categories=post_categories,
            unlock=unlock,
            permission=permission,
            isOnline=online,
            userTopicCount=userTopicCount,
            categories=TermTaxonomy().getCategories(),
            tags=tags['data']
        )
        self.render("topic/single.html",**p)
    def checkLock(self,d):
        if d.post_status != 'protect':
            return True
        unlock = False
        if 'post_id_'+str(d.ID) in self.session:
            unlock=True
        return unlock
    def post(self,id):
        pwd = self.get_request("password","")
        pwd = pyUtility.md5(pwd)
        s = Post().getPostByIDforPwdCheck(id, pwd)
        if s:
            self.session['post_id_'+str(id)] = 1
        self.redirect(self.webroot_url("topic/show/"+str(id)))

class TopicsMadeByUserHandler(BaseHandler):
    def get(self, id):
        start = self.get_int_request("s",0)
        limit=20
        if start < 0:
            start=0
        res=Post().getByAuthorID(id,start,limit, self.userID)
        pagers = pyUtility.generate_paging_data(start=start,limit=limit,total=res['total'])
        user=User().getByID(id)
        d = []
        if res['data']:
            for tRec in res['data']:
                tmp = tRec.row2dict()
                tmp['unlock'] = True
                if tmp['post_status'] == 'protect':
                    if 'post_id_'+str(tmp['ID']) not in self.session:
                        tmp['unlock'] = False
                tmp['user'] = tRec.user
                tmp['summary'] = pyUtility.remove_html_tags(tmp['post_content'])
                d.append(tmp)

        # TAGS
        tags = TermTaxonomy().getTags()
        for tag in tags['data']:
            score = math.floor( float(tag['count']) / float(tags['counts']) * 140 + 95)
            tag['size'] = str(score) + "%"
        dic={}
        dic['title']="User's Posts"
        dic['posts']=d
        dic['total']=res['total']
        dic['author']=str(id)
        dic['user']=user
        dic['pages']= pagers
        dic['tags']= tags['data']
        dic['categories'] = TermTaxonomy().getCategories()
        self.render("topic/user_topics.html", **dic)

class TopicsFilterByTagHandler(BaseHandler):
     def get(self, name):
        start = self.get_int_request("s",0)
        userid = self.userID
        limit=20
        if start < 0:
            start=0

        res=Post().getByTag(start,limit, name, userid)
        pagers = pyUtility.generate_paging_data(start=start,limit=limit,total=res['total'])
        d = []
        if res['data']:
            for tRec in res['data']:
                tmp = tRec.Post.row2dict()
                tmp['unlock'] = True
                if tmp['post_status'] == 'protect':
                    if 'post_id_'+str(tmp['ID']) not in self.session:
                        tmp['unlock'] = False
                tmp['user'] = tRec.Post.user
                tmp['summary'] = pyUtility.remove_html_tags(tmp['post_content'])
                d.append(tmp)
        # TAGS
        tags = TermTaxonomy().getTags()
        for tag in tags['data']:
            score = math.floor( float(tag['count']) / float(tags['counts']) * 140 + 95)
            tag['size'] = str(score) + "%"
        dic={}
        dic['title']="Posts with tag"
        dic['posts']=d
        dic['total']=res['total']
        dic['parameters']= name
        dic['keyword']=name
        dic['pages']= pagers
        dic['tags'] = tags['data']
        dic['categories'] = TermTaxonomy().getCategories()
        self.render("topic/tag_topics.html", **dic)

class TopicsFilterByCatHandler(BaseHandler):
     def get(self, name):
        start = self.get_int_request("s",0)
        userid = self.userID
        limit=20
        if start < 0:
            start=0
        res=Post().getByCategory(start,limit, name, userid)
        pagers = pyUtility.generate_paging_data(start=start,limit=limit,total=res['total'])
        d = []
        if res['data']:
            for tRec in res['data']:
                tmp = tRec.Post.row2dict()
                tmp['unlock'] = True
                if tmp['post_status'] == 'protect':
                    if 'post_id_'+str(tmp['ID']) not in self.session:
                        tmp['unlock'] = False
                tmp['user'] = tRec.Post.user
                tmp['summary'] = pyUtility.remove_html_tags(tmp['post_content'])
                d.append(tmp)
        # TAGS
        tags = TermTaxonomy().getTags()
        for tag in tags['data']:
            score = math.floor( float(tag['count']) / float(tags['counts']) * 140 + 95)
            tag['size'] = str(score) + "%"
        dic= {}
        dic['title']="Posts with tag"
        dic['posts']=d
        dic['keyword']=name
        dic['total']=res['total']
        dic['parameters']= name
        dic['pages']= pagers
        dic['tags']=tags['data']
        dic['categories'] = TermTaxonomy().getCategories()
        self.render("topic/category_topics.html", **dic)
