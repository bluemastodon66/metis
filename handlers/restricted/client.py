# -*- coding: utf-8 -*-
"""
Client Related Functionality
"""
from handlers.base import BaseHandler
from model.User import User
from handlers.module import loginRequired
import random
import time
import tornado.web
from libs.pyEmail import SingleMail
from libs import pyUtility, pyEnum
class SettingClientHandler(BaseHandler):
    @loginRequired (roles = [pyEnum.AccountRole.Normal, pyEnum.AccountRole.Manager],chkActivate=False)
    def get(self):
        r = random.randint(1,9999)
        s = self.session
        self.render("restricted/client/setting.html", user= self.get_current_user(),rand=r, title="Setting")
    @loginRequired (roles = [pyEnum.AccountRole.Normal, pyEnum.AccountRole.Manager],chkActivate=False)
    def post(self):

        email = self.get_request("email", "")
        user_url = self.get_request("personal_url", "")
        displayName = self.get_request("display_name", "")
        password = self.get_request("password", "")
        crsf = self.get_request("_xsrf","")
        user_crsf = self.get_cookie("_xsrf","unknown")
        self.clear_cookie("_xsrf")
        if crsf != user_crsf or user_crsf =="unknown":
            self.print_result(False, "Xsrf protected!")
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

        current = self.get_current_user()
        if current['user_email'] != email:
            """
                Check if email has been taken or not
            """
            if not User().isEmailUnique(email):

                self.print_result(False, "Email Has been used")
                return
        user = User().getByID(current['ID'], False)
        if user:
            if not password == "":
                newPwd = user.getEncodeStr(password)
                if newPwd != user.user_pass:
                    user.user_pass = newPwd
            user.user_email = email
            user.user_url = user_url
            user.display_name = displayName
            newUserData = user.row2dict()
            if user.update():
                self.set_current_user(newUserData)
                self.print_result(True, "Done")
            else :
                self.print_result(False, "Failed to Update DB")
        else:
            # find failed
            self.print_result(False, "Can not find any record")


class ResendActivatedKeyHandler(BaseHandler):
    @loginRequired (roles = [pyEnum.AccountRole.Normal, pyEnum.AccountRole.Manager],chkActivate=False)
    def get(self):
        r = random.randint(1,9999)
        s = self.session
        self.render("restricted/client/resend_activated_key.html", user= self.get_current_user(),rand=r, title="Resend Activation Key")
    @loginRequired (roles = [pyEnum.AccountRole.Normal, pyEnum.AccountRole.Manager],chkActivate=False)
    def post(self):
        validcode = self.get_request("validcode", "")
        if "validcode" in self.session:
            if validcode != self.session['validcode'] :
                self.print_result(False, "ValidCode is incorrect!!")
                return
        else:
            self.print_result(False, "ValidCode is incorrect!!")
            return
        user = User().getByID(self.userID, False)
        if  user :
            # found it
            # send email
            activationKey = user.getEncodeStr(str(user.user_login)+"-"+ str(time.time()))
            user.user_activation_key = activationKey
            if user.update() :
                self.print_result(True, "Done")
                """
                    Send Email to register
                """
                msg = self.render_string("email/register.html",activationKey=activationKey, login_user = user.user_login, website_url= self.webroot_url("", True), web_title = self.web_title() )
                subject = "["+self.web_title()+"] ReSend Activation Key"
                qm = SingleMail.get_instance()
                qm.send_email(user.user_email,subject, msg, 'html')

            else :
                self.print_result(False, "Failed to Update DB")

        else:
            # find failed
            self.print_result(False, "Can not find any record")
