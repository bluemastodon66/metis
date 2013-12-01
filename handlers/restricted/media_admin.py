from handlers.base import BaseHandler
from model.Media import Media
from handlers.module import loginRequired
from libs import pyUtility
import Image
class MediaAPIHandler(BaseHandler):
    @loginRequired ()
    def get(self, s):
        pics = Media().searchByKeyword("",s,1,self.userID)
        paginate = pyUtility.generate_paging_data(start=s,limit=1,total=pics['total'])
        dic={}
        dic['pics'] = pics['data']
        dic['picsTotal'] = pics['total']
        dic['pages'] = paginate
        self.render("media/partial_pics.html", **dic)


