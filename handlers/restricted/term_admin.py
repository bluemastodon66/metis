from handlers.base import BaseHandler
from model.TermTaxonomy import TermTaxonomy
from handlers.module import loginRequired

from libs import pyEnum
import json


class TermSearchHandler(BaseHandler):
    @loginRequired ()
    def get(self):
        keyword = self.get_request("term","").strip()
        s=[]
        if len(keyword) >=1:
            s = TermTaxonomy().searchByName(keyword)
        self.write(json.dumps(s))