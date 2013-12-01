'''
Created on 2013/6/14

@author: LSJ
'''
import functools
import urlparse
from urllib import urlencode
from tornado.web import HTTPError
from libs import pyEnum
import json
def loginRequired(method=None, roles=None, chkActivate=True):
    """Decorate methods with this to require that the user be logged in.   
    If the user is not logged in, they will be redirected to the configured
    `login url <RequestHandler.get_login_url>`.
    """
    if method is None :
        return functools.partial(loginRequired, roles=roles, chkActivate=chkActivate)
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):  
        # baseurl = self.webroot_url("",True)
        baseurl = self.webroot_url("")
        url = baseurl+self.get_login_url()
        if "?" not in url:
            if urlparse.urlsplit(url).scheme:
                # if login url is absolute, make next absolute too
                next_url = self.request.full_url()
            else:
                next_url = self.request.uri
            url += "?" + urlencode(dict(next=next_url))
        userInfo = self.current_user              
        if not userInfo :
            if self.request.method in ("GET", "HEAD", "POST"):
                if  self.isAjax :
                    o = {}
                    o['success'] = False
                    o['msg'] = _('AuthorizedRequired')
                    o['url'] = url
                    self.finish(json.dumps(o))  
                else:    
                    self.redirect(url)
                return
            raise HTTPError(403)
        else :
            if userInfo['ID'] <=0:
                if  self.isAjax :
                    o = {}
                    o['success'] = False
                    o['msg'] = _('AuthorizedRequired')
                    o['url'] = url
                    self.finish(json.dumps(o))
                else:
                    self.redirect(url)
                return


            if roles:
                if not userInfo['role'] in roles and userInfo['role'] != pyEnum.AccountRole.Admin:
                    if  self.isAjax :
                        o = {}
                        o['success'] = False
                        o['msg'] = _('AuthorizedRequired')
                        o['url'] = url
                        self.finish(json.dumps(o))  
                    else:    
                        self.redirect(baseurl+"static/denied.html")
                else:
                    if userInfo['user_status'] != 1 and chkActivate:
                        if  self.isAjax :
                            o = {}
                            o['success'] = False
                            o['msg'] = _('Account Is Not Activated')
                            o['url'] = url
                            self.finish(json.dumps(o))
                        else:
                            self.redirect(baseurl+"client/resend_activate/")

      
        return method(self, *args, **kwargs)
    return wrapper    