from handlers.base import BaseHandler
from model.Post import Post
from model.Comment import Comment
from libs import pyUtility
class ReplyHandler(BaseHandler):
    def get(self):
        # Comments
        id = self.get_int_request("id",0)
        cs = self.get_int_request("cs",0)
        limit=10
        comments = Comment().getList(cs,limit,id)
        if comments['total'] > limit:
            paginate = pyUtility.generate_paging_data(start=cs,limit=limit,total=comments['total'])
        else:
            paginate =None
        p={}
        p['title']='Comments'
        p['uid']=str(id)
        p['records']=comments['data']
        p['totalComment']=comments['total']
        p['paginate']=paginate
        self.render("topic/partial_replies.html",**p)
class ReplyAddHandler(BaseHandler):
    def post(self, id):
        reply_author = self.get_request("reply_author","")
        reply_email = self.get_request("reply_email","")
        reply_url = self.get_request("reply_url","")
        reply = self.get_request("reply_content","")
        reply_content = pyUtility.reply_purify(reply)
        crsf = self.get_request("_xsrf","")
        ip =self.request.remote_ip
        user_crsf = self.get_cookie("_xsrf","unknown")
        self.clear_cookie("_xsrf")
        if crsf != user_crsf or user_crsf =="unknown":
            self.redirect(self.get_webroot_url()+"topic/show/"+id+"/?error=1")
            return

        if id==0 or reply_author=="" or reply_email=="":
            self.redirect(self.get_webroot_url()+"topic/show/"+id+"/?error=1")
            return
        if not pyUtility.isEmail(reply_email):
            self.redirect(self.get_webroot_url()+"topic/show/"+id+"/?error=1")
            return
        if reply_url !="" and not pyUtility.isURL(reply_url):
            self.redirect(self.get_webroot_url()+"topic/show/"+id+"/?error=1")
            return

        # totalComments = Comment().getCountByPostID(id)
        r=Post().getPostShortInfo(id)
        if not r:
            self.redirect(self.get_webroot_url()+"topic/show/"+id+"/?error=2")
            return
        if r.comment_status == 'close':
            self.redirect(self.get_webroot_url()+"topic/show/"+id+"/?error=3")
            return


        if 'User-Agent' in self.request.headers:
            agent = self.request.headers['User-Agent']
        else:
            agent ="unknown"
        comment = Comment()
        comment.post_id = id
        comment.IP = ip
        comment.author = reply_author
        comment.content = reply_content
        comment.email = reply_email
        comment.agent = agent
        comment.url = reply_url
        comment.user_id = self.userID # current Logiin ID, guest id 0
        comment.save()
        self.redirect(self.get_webroot_url()+"topic/show/"+id)



