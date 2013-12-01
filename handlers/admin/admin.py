# -*- coding: utf-8 -*-
from handlers.base import BaseHandler
from model.User import User
from handlers.module import loginRequired
import math
from libs import pyUtility, pyEnum, pyCache
from model.Option import Option
class AdminHandler(BaseHandler):
    @loginRequired (roles = [pyEnum.AccountRole.Admin])
    def get(self):               
        user = self.get_current_user()
        tmp = User().getStatGrpByRole()
        statRole = []
        statTotalRole = 0
        if not tmp is None:
            for r in tmp:
                statTotalRole+=r[0]
                data = {}
                data['count'] = r[0]
                data['role'] = r[1]
                statRole.append(data)
        tmp = User().getRecentJoinMembers()
        recentJoin = []
        if not tmp is None:
            for r in tmp:
                data = {}
                data['name'] = r.user_login
                data['date'] = r.user_registered
                data['ID'] = r.ID
                recentJoin.append(data)
        p=dict(
            title='Control Console',
            onlineCount=self.session.getCount(),
            user=user,
            statRole=statRole,
            statTotalRole=statTotalRole,
            recentJoin=recentJoin
        )
        self.render("admin/main.html",**p)
# User Accounts
class AdminUserHandler(BaseHandler):
    @loginRequired (roles = [pyEnum.AccountRole.Admin])
    def get(self):
        self.ui['convert_status'] = pyEnum.GetAccountStatus
        act = self.get_request("act","")
        start = self.get_int_request("s",0)
        keyword = self.get_request("k","")
        id = self.get_request("id","")
        limit= 50
        if start < 0:
            start=0
        if act == "role":
            parameters="act=role&id="+id
            res = User().searchByRole(id,start,limit)
        else:
            parameters="k="+keyword
            res = User().searchByKeyword(keyword,start, limit)
        total = res['total']
        data = res['data']

        pagers = pyUtility.generate_paging_data(start=start,limit=limit,total=total)

        users = []
        counter = 1 + int(math.floor(start/limit)) * limit
        if not data is None:
            for r in data:
                tmp = r.row2dict()
                tmp["no"] = counter
                counter+=1
                users.append(tmp)
        p=dict(
            title='User Management',
            users=users,
            act=act,
            id=id,
            parameters=parameters,
            keyword=keyword,
            pages=pagers,
            totalAccount=total
        )
        self.render("admin/users.html",**p)
    def post(self):
        nextmove = self.get_request("nextmove","")
        act=self.get_request("action","")
        ids=self.get_arguments("author_ids","")
        if act == "delete":
            User().delUsersByIDs(ids)
        if act == 'enable':
            User().setStatusUsersByIDs(ids, 1)
        if act == 'disable':
            User().setStatusUsersByIDs(ids, 2)

        self.redirect(self.webroot_url("admin/users/?"+nextmove))


        pass

class AdminUserAddHandler(BaseHandler):
    @loginRequired (roles = [pyEnum.AccountRole.Admin])
    def get(self):
        self.ui['convert_status'] = pyEnum.GetAccountStatus
        p=dict(
            isAdd=True,
            title='Add User Account',
            actionUrl= self.get_webroot_url()+"admin/users/add/",
            roles=pyEnum.AccountRole.List,
            defaultStatus=pyEnum.GetAccountStatus(1),
            defaultRole=pyEnum.AccountRole.Normal,
            user_status=pyEnum.AccountStatus()
        )
        self.render("admin/user_add_edit.html",**p)
    @loginRequired (roles = [pyEnum.AccountRole.Admin])
    def post(self):
        user_account = self.get_request("account","")
        email = self.get_request("email", "")
        user_url = self.get_request("personal_url", "")
        displayName = self.get_request("display_name", "")
        password = self.get_request("password", "")
        role = self.get_request("role","")
        status = self.get_int_request("status",0)
        if user_account == "":
            self.print_result(False, "User Account Cannot be blank!")
            return
        if user_url != "":
            tmp = user_url.lower()
            if not tmp.startswith("http"):
                user_url = "http://"+user_url
            if not pyUtility.isURL(user_url):
                self.print_result(False, "The Format of URL is wrong!")
                return
        if email == "":
            self.print_result(False, "Email Cannot be blank!")
            return
        if not pyUtility.isEmail(email):
            self.print_result(False, "Email Format is incorrect!")
            return
        if password == "":
            self.print_result(False, "Password is empty!")
            return
        user_account = user_account.lower()
        email = email.lower()
        if not pyUtility.isAccountLegal(user_account):
            self.print_result(False, "The Format of Account is not legal")
            return
        if not User().isUnique(email=email, acc=user_account):
            self.print_result(False, "Account or Email Has been used")
            return
        user = User()
        newPwd = user.getEncodeStr(password)
        user.user_login = user_account
        user.user_pass = newPwd
        user.user_email = email
        user.user_url = user_url
        user.role = role
        user.user_status = status
        user.display_name = displayName
        newID = user.save()
        if newID >0:
            self.print_result(True, "Done", self.get_webroot_url()+"admin/users/")
        else:
            self.print_result(False, "Failed to Add Account to DB")


class AdminUserEditHandler(BaseHandler):
    @loginRequired (roles = [pyEnum.AccountRole.Admin])
    def get(self):
        id = self.get_int_request("id",0)
        self.ui['convert_status'] = pyEnum.GetAccountStatus
        u=None
        if id!=0:
            u=User().getByID(id)
        p=dict(
            title='Edit User Account',
            isAdd=False,
            actionUrl= self.get_webroot_url()+"admin/users/edit/",
            user=u,
            roles=pyEnum.AccountRole.List,
            user_status=pyEnum.AccountStatus()
        )
        self.render("admin/user_add_edit.html",**p)
    @loginRequired (roles = [pyEnum.AccountRole.Admin])
    def post(self):
        uid = self.get_request("id","")
        email = self.get_request("email", "")
        user_url = self.get_request("personal_url", "")
        displayName = self.get_request("display_name", "")
        password = self.get_request("password", "")
        role = self.get_request("role","")
        status = self.get_int_request("status",0)
        if uid =="":
            self.print_result(False,"error id is empty")
            return

        if user_url != "":
            tmp = user_url.lower()
            if not tmp.startswith("http"):
                user_url = "http://"+user_url
            if not pyUtility.isURL(user_url):
                self.print_result(False, "The Format of URL is wrong!")
                return
        if email == "":
            self.print_result(False, "Email Cannot be blank!")
            return
        if not pyUtility.isEmail(email):
            self.print_result(False, "Email Format is incorrect!")
            return

        user = User().getByID(uid, False)
        if not user:
            user.close()
            self.print_result(False, "Can not find any record")
            return
        if user.user_email != email:
            """
                Check if email has been taken or not
            """
            if not User().isEmailUnique(email, False):
                self.print_result(False, "Email Has been used")
                return
        if not password == "":
            newPwd = user.getEncodeStr(password)
            if newPwd != user.user_pass:
                user.user_pass = newPwd
        user.user_email = email
        user.user_url = user_url
        user.role = pyEnum.GetAccountRole(role)
        user.user_status = pyEnum.GetAccountStatusID(status)
        user.display_name = displayName
        if user.update():
            self.print_result(True, "Done", self.webroot_url("admin/users/edit/?id="+uid))
        else :
            self.print_result(False, "Failed to Update DB")

class AdminWebOptionHandler(BaseHandler):
    @loginRequired (roles = [pyEnum.AccountRole.Admin])
    def get(self):
        s = Option().getAll(100)
        p={}
        p['title']='Web Options'
        p['data']=s
        self.render("admin/web_option.html",**p)
    def post(self):

        web_title = self.get_request("web_title","")
        site_name = self.get_request("site_name","")
        description = self.get_request("description","")
        admin_email = self.get_request("admin_email","")
        version = self.get_request("version","")
        flag1 = self.get_request("users_can_register","")
        flag2 = self.get_request("under_maintenance","")

        thumb_width = self.get_int_request("thumb_width",50)
        thumb_height = self.get_int_request("thumb_height",0)
        if thumb_width < 50:
            thumb_width = 50
        if thumb_height !=0 and thumb_height < 50:
            thumb_height = 50

        if flag1:
            register="1"
        else:
            register="0"
        if flag2:
            um="1"
        else:
            um="0"

        if self.addOrUpdate("web_title",web_title):
            pyCache.WebOptions['web_title']=web_title
        if self.addOrUpdate("site_name",site_name):
            pyCache.WebOptions['site_name']=site_name
        if self.addOrUpdate("description",description):
            pyCache.WebOptions['description']=description
        if self.addOrUpdate("admin_email",admin_email):
            pyCache.WebOptions['admin_email']=admin_email
        if self.addOrUpdate("version",version):
            pyCache.WebOptions['version']=version
        if self.addOrUpdate("users_can_register",register):
            pyCache.WebOptions['users_can_register']=register
        if self.addOrUpdate("under_maintenance",um):
            pyCache.WebOptions['under_maintenance']=um

        if self.addOrUpdate("thumb_width", thumb_width):
            pyCache.WebOptions['thumb_width'] = thumb_width
        if self.addOrUpdate("thumb_height", thumb_height):
            pyCache.WebOptions['thumb_height'] = thumb_height



        self.redirect(self.webroot_url("admin/web_option/"))

    def addOrUpdate(self,op,val):
        s = Option().getByName(op, False)
        if s:
            s.option_value = val
            return s.update()
        else:
            u = Option()
            u.option_name=op
            u.option_value=val
            return u.save()
