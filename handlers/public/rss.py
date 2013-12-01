from handlers.base import BaseHandler
from model.Post import Post
from libs import pyUtility, pyCache
class RSSHandler(BaseHandler):
    def get(self):
        limit= 30
        res=Post().getRSS(0,limit)
        d = []
        if res:
            for tRec in res:
                tmp = tRec.row2dict()
                tmp['user'] = tRec.user
                tmp['summary'] = pyUtility.remove_html_tags(tmp['post_content'])
                d.append(tmp)
        dic={}
        dic['title']='RSS'
        dic['description']= pyCache.WebOptions['description']
        dic['posts']=d
        dic['webrootlink']=self.webroot_url("",True)
        r = self.render_string("public/rss.html", **dic)
        self.set_header("Content-Type", "text/xml")
        self.finish(r)

        # self.render("public/rss.html", **dic)
