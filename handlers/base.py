# -*- coding: utf-8 -*-
import json
from settings import settings
from session.redis import Session
import re
from libs import pyUtility, pyEnum, pyCache
import time
from tornado.web import RequestHandler, HTTPError
class BaseHandler(RequestHandler):
    """A class to collect common handler methods - all other handlers should
    subclass this one.
    """
    def __init__(self, *argc, **argkw):
        super(BaseHandler, self).__init__(*argc, **argkw)
        self.ui['webroot_url'] = self.webroot_url  # adding new function to template for usage
        self.ui['current_path'] = self.requestPath  # adding new function to template for usage
        self.ui['is_login'] = self.isLogin()
        self.ui['web_title'] = self.web_title()
        self.ui['web_description'] = pyCache.WebOptions['description']
        self.ui['web_site_name'] = pyCache.WebOptions['site_name']
        self.ui['current_ver'] = pyCache.WebOptions['version']
        self.ui['is_manager'] = self.isManager()
        self.ui['is_admin'] = self.isAdmin()
        self.updateUserStatus()

        # this one would execute any url #
        # print "Client::::"+self.requestPath
    def render(self, template_name, **kwargs):
        """
        if your wanna to do page cache your can do it here
        """
        if self.isUnderMantenance():
            self.redirect(self.webroot_url("static/maintenance.html"))
            return
        super(BaseHandler, self).render(template_name, **kwargs)
    def isUnderMantenance(self):
        isUnder = pyCache.WebOptions['under_maintenance']
        if isUnder != '1':
            return False
        user = self.get_current_user()
        if user['role'] == pyEnum.AccountRole.Admin:
            return False
        webroot = "/"
        if "webroot_path" in self.settings:
            webroot = self.settings['webroot_path']
        path = str(self.requestPath)
        if  path.startswith(webroot+"admin/") or path.startswith(webroot+"auth/login/"):
            return False
        return True
    def isAdmin(self):
        if self.isLogin():
            user = self.get_current_user()
            if user['role'] == pyEnum.AccountRole.Admin:
                return True
        return False
    def isManager(self):
        if self.isLogin():
            user = self.get_current_user()
            if user['role'] == pyEnum.AccountRole.Admin or user['role'] == pyEnum.AccountRole.Manager:
                return True
        return False
    def isLogin(self):
        uid = self.userID
        if uid <=0:
            return False
        return True
    def updateUserStatus(self):
        uid = self.userID
        dd={}
        dd["update"] = time.time()
        dd["activity"] = self.requestPath
        jstr = json.dumps(dd)
        self.redis.setex("user:"+str(uid),300,jstr)

    def getOnlineUserByID(self,id):
        s = self.redis.get("user:"+str(id))
        r= None
        if s:
            r = pyUtility.jsonDecode(s)
        return r
    def delOnlineStatus(self):
        uid = self.userID
        if uid == 0:
            return
        self.redis.delete("user:"+str(uid))
    def webroot_url(self, path, include_host=None):
        """Returns a root URL for the given relative static file path.    
        """
        # self.require_setting("webroot_path")
        if include_host is None:
            include_host = getattr(self, "include_host", False)
        if include_host:
            base = self.request.protocol + "://" + self.request.host
        else:
            base = ""
        webroot = ""
        if "webroot_path" in self.settings:
            webroot = self.settings['webroot_path']
        return base + webroot + path

    def web_title(self):
        return pyCache.WebOptions['web_title']

    def get_webroot_url(self):
        webroot = ""
        if "webroot_path" in self.settings:
            webroot = self.settings['webroot_path']
        return webroot
    def get_permission(self):
        """
        Get Default Permission
        """
        permission = {'edit':False,'add':False,'del':False,'read':True}
        login = self.get_current_user()
        if login['role'] == pyEnum.AccountRole.Admin\
            or login['role'] == pyEnum.AccountRole.Manager:
            permission['edit'] = True
            permission['add'] = True
            permission['del'] = True

        return permission
    @property
    def userID(self):
        u = self.get_current_user()
        if u is None:
            return 0
        if 'ID' in u:
            return u['ID']
        return 0

    def set_current_user(self, user):
        self.session['user'] = user

    def get_current_user(self):
        if self.session:
            if 'user' in self.session:
                return self.session['user']
        u = {"ID": -1,"user_login":"guest","role":"guest", "display_name":"Guest"}
        if self.session:
            self.session['user'] = u
        return u
    """
        get http request
    """
    def get_request(self, name, default=None):
        v = self.get_argument(name, default)
        v = v.strip()
        if v == "":
            v = default
        return v
    def get_int_request(self, name, default=0):
        v= self.get_argument(name, default)
        return pyUtility.str2int(v)
    """
        This one will return the path with "/" in the end of string
    """
    @property
    def requestPath(self):
        v = self.request.path
        if not v.endswith("/"):
            v=v+"/"
        else:
            v=re.sub('\/{2,}','/',v)
        return v
    @property
    def redis(self):
        return self.application.redis_cache
    @property
    def session(self):
        sessionid = self.get_secure_cookie(settings['session_name'])
        s = Session(self.application.session_store, sessionid)
        if sessionid is None:
            self.set_secure_cookie(settings['session_name'], s.sessionid)
        return s

    @property
    def isAjax(self):
        if "X-Requested-With" in self.request.headers and self.request.headers['X-Requested-With'] == "XMLHttpRequest":
            return True
        return False

    def load_json(self):
        """Load JSON from the request body and store them in
        self.request.arguments, like Tornado does by default for POSTed form
        parameters.

        If JSON cannot be decoded, raises an HTTPError with status 400.
        """
        try:
            self.request.arguments = json.loads(self.request.body)
        except ValueError:
            msg = "Could not decode JSON: %s" % self.request.body

            raise HTTPError(400, msg)

    def get_json_argument(self, name, default=None):
        """Find and return the argument with key 'name' from JSON request data.
        Similar to Tornado's get_argument() method.
        """
        if default is None:
            default = self._ARG_DEFAULT
        if not self.request.arguments:
            self.load_json()
        if name not in self.request.arguments:
            if default is self._ARG_DEFAULT:
                msg = "Missing argument '%s'" % name

                raise HTTPError(400, msg)

            return default
        arg = self.request.arguments[name]

        return arg

    def write_error(self, status_code, **kwargs):
        print('In get_error_html. status_code: {0}'.format(status_code))
        if status_code in [403, 404, 500, 503]:
            self.render('404.html')
        else:
            self.write('BOOM!')

    def print_result(self, success, msg, next_move=False):
        url = self.get_webroot_url()
        ajaxReturn = {}
        if next_move:
            url = next_move
        if self.isAjax:
            ajaxReturn['success'] = success
            ajaxReturn['msg'] = msg
            ajaxReturn['url'] = url
            self.finish(json.dumps(ajaxReturn))
        else:
            self.redirect(url)
    def on_finish(self):
        pass
