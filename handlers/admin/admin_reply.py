from handlers.base import BaseHandler
from model.Comment import Comment
from handlers.module import loginRequired

from libs import pyUtility, pyEnum



class ReplyAdminHandler(BaseHandler):
    @loginRequired (roles = [pyEnum.AccountRole.Admin])
    def get(self):
        start = self.get_int_request("s",0)
        keyword=self.get_request("k","")
        act=self.get_request("act","")
        id=self.get_int_request("id",0)
        errorCode=self.get_int_request("error",0)
        error=None
        if errorCode==1:
            error="Failed to update DB"
        if errorCode==2:
            error="Delete failed"
        nextmove=""
        editData=None
        hasUser=False
        limit= 50
        if start < 0:
            start=0

        if act=="user":
            parameters="act=user&id="+str(id)
            res=Comment().searchByKeyword("",start,limit, id)
        else:
            if act=="edit":
                editData=Comment().getByID(id)
                if editData.user:
                    hasUser=True
                    nextmove="act=edit&id="+str(id)
            parameters="act="
            res=Comment().searchByKeyword(keyword,start,limit,0)
            parameters=parameters+"&k="+keyword
        pagers = pyUtility.generate_paging_data(start=start,limit=limit,total=res['total'])
        d = []
        if res['data']:
            for tRec in res['data']:
                tmp = tRec.row2dict()
                tmp['user'] = tRec.user
                tmp['summary'] = pyUtility.remove_html_tags(tmp['content'])
                d.append(tmp)
        dic= {}
        dic['title']='Reply List'
        dic['records']= d
        dic['error'] = None
        dic['editData']= editData
        dic['hasUser']=hasUser
        dic['uid']=str(id)
        dic['total']=res['total']
        dic['parameter']= parameters
        dic['nextmove']=nextmove
        dic['pages']= pagers
        dic['keyword']=keyword
        self.render("admin/admin_replies.html", **dic)

    def post(self):
        nextmove = self.get_request("nextmove","")
        id=self.get_int_request("commentID",0)
        email=self.get_request("reply_email","unknown")
        author=self.get_request("reply_author","unknown")
        url=self.get_request("reply_url","")
        content=self.get_request("reply_content","")
        act=self.get_request("act","")
        ids=self.get_arguments("ids","")
        error="0"
        if act == "delete":
            if not Comment().removeAllByArray(ids):
                error="2"
        if act == 'edit':
            r=Comment().getByID(id)
            if r:
                error="0"
                if not r.user:
                    r.email=email
                    r.author=author
                r.url=url
                r.content=content
                if r.save() <=0:
                    error="1"
            else:
                error="1"
        self.redirect(self.webroot_url("admin/replies/?error="+error+"&"+nextmove))
