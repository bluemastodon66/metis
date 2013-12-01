from handlers.base import BaseHandler
from model.Post import Post
from model.TermTaxonomy import TermTaxonomy
from libs import pyUtility
import math
class WelcomeHandler(BaseHandler):
    def get(self):
        limit= 5
        res=Post().searchByKeyword("",0,limit, self.userID)
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
        # Tags
        tags = TermTaxonomy().getTags()
        for tag in tags['data']:
            score = math.floor( float(tag['count']) / float(tags['counts']) * 140 + 95)
            tag['size'] = str(score) + "%"
        dic={}
        dic['tags'] = tags['data']
        dic['title']='Welecome'
        dic['categories'] = TermTaxonomy().getCategories()
        dic['posts']=d
        self.render("public/welcome.html", **dic)
    def on_finish(self):
        pass
