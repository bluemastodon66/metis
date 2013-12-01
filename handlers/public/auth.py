# -*- coding: utf-8 -*-
from handlers.base import BaseHandler
from model.User import User
from tornado.escape import url_escape
import hashlib
import time
import random
from libs.pyEmail import SingleMail
from libs import pyUtility,pyCache

class ResetPwdHandler(BaseHandler):
    def get(self):
        tid = self.get_request("id", "")
        p = dict(
            title='Reset Password',
            login_name="",
            token="",
            isError=True
        )
        if (id != ""):
            user = User().getByResetToken(tid)
            if not user is None:
                thisNow = int(time.time())
                if user.reset_expired >= thisNow:
                    p['isError'] = False
                    p['login_name'] = user.user_login
        self.render("public/reset_password.html", **p)

        # @tornado.web.asynchronous

    def post(self):
        token = self.get_request("Login[token]", None)
        newPass = self.get_request("Login[pass]", "")
        if token == "" or newPass == "" or len(newPass) < 4:
            self.print_result(False, "Incorrect parameters")
            return
        user = User().getByResetToken(token, False)
        if user:
            # found it
            # send email
            user.user_pass = user.getEncodeStr(newPass)

            p = dict(
                newPass=newPass,
                login_user=user.user_login,
                admin_email=pyCache.WebOptions['admin_email'],
                website_url=self.webroot_url("", True)
            )
            msg = self.render_string("email/pass_has_changed.html", **p)
            subject = "[" + self.web_title() + "] Password Has Change"
            user.user_reset_token = ""
            user.reset_expired = 0
            if user.update():
                qm = SingleMail.get_instance()
                qm.send_email(user.user_email, subject, msg, 'html')
                self.print_result(True, "Done")
            else:
                self.print_result(False, "Failed to Update DB")

        else:
            # find failed
            self.print_result(False, "Can not find any record via this Email")


class ActivateAccountHandler(BaseHandler):
    def get(self):
        tid = self.get_request("id", "")
        user = None
        if (id != ""):
            user = User().getByActivateToken(tid, False)
        success = False
        login = ""
        if not user is None:
            user.user_status = 1
            user.user_activation_key = ""
            login = user.user_login
            if user.update():
                success = True
        self.render("public/activate_account.html", login_name=login, title="Activate Account", isSuccess=success)


class LostPwdHandler(BaseHandler):
    def get(self):
        r = random.randint(1, 9999)
        nextmove = self.get_request("next", "")
        self.render("public/lost_password.html", title="Lost Password", rand=r, nextmove=nextmove)

    # @tornado.web.asynchronous
    def post(self):
        email = self.get_request("Login[email]", None)
        validcode = self.get_request("Login[validcode]", "")
        if not pyUtility.isEmail(email):
            self.print_result(False, "The Format of Email is incorrect!!")
            return
        if "validcode" in self.session:
            if validcode != self.session['validcode']:
                self.print_result(False, "ValidCode is incorrect!!")
                return
        else:
            self.print_result(False, "ValidCode is incorrect!!")
            return
        if not email or email is None:
            self.print_result(False, "Email Is Empty!")
            return

        user = User().getByEmail(email, False)
        if user:
            # found it
            # send email

            token = hashlib.md5(email + str(random.randint(1000, 9999))).hexdigest()
            p = dict(
                login_user=user.user_login,
                reset_token=token,
                admin_email=pyCache.WebOptions['admin_email'],
                website_url=self.webroot_url("", True)
            )
            msg = self.render_string("email/pass_reset.html", **p)
            subject = "[" + self.web_title() + "] Password Update"
            user.user_reset_token = token
            user.reset_expired = int(time.time()) + 60 * 60 * 2 # expired time: 2 hours
            if user.update():
                qm = SingleMail.get_instance()
                qm.send_email(email, subject, msg, 'html')
                self.print_result(True, "Done")
            else:
                self.print_result(False, "Failed to Update DB")
        else:
            # find failed
            self.print_result(False, "Can not find any record via this Email")


class LoginHandler(BaseHandler):
    def get(self):
        r = random.randint(1, 9999)
        nextmove = self.get_request("next", "")
        username = self.get_cookie("login_name", "")
        self.render("public/login.html", title="Login", rand=r, login_name=username, nextmove=nextmove)

    def post(self):
        username = self.get_request("Login[username]", None)
        nextmove = self.get_request("nextmove", "")
        pwd = self.get_request("Login[password]", None)
        remember = self.get_request("Login[remember]", None)
        validcode = self.get_request("Login[validcode]", "")

        if not pyUtility.isAccountLegal(username):
            self.print_result(False, "User Or Password is incorrect!!")
            return
        if "validcode" in self.session:
            if validcode != self.session['validcode']:
                self.print_result(False, "ValidCode is incorrect!!", True)
                return
        else:
            self.print_result(False, "ValidCode is incorrect!!", True)
            return

        if not remember is None and remember:
            self.set_cookie("login_name", url_escape(username))
        else:
            self.clear_cookie("login_name")
            # login process
        if not username or not pwd or username is None or pwd is None:
            self.print_result(False, "UserName Or Password Is Empty!")
            return
        user = User().Login(username, pwd)
        if user:
            # login success
            # save session
            if user.user_status==2:
                self.print_result(False,"Account has been locked")
                return
            self.set_current_user(user.row2dict())
            self.print_result(True, "Authorized", nextmove)
        else:
            # login failed
            self.print_result(False, "User Or Password Is Wrong", self.get_webroot_url()+"auth?next=" + url_escape(nextmove))


class RegisterHandler(BaseHandler):
    def get(self):
        canRegister = pyCache.WebOptions['users_can_register']
        r = random.randint(1, 9999)
        self.render("public/register.html", title="Register", rand=r, canRegister= (canRegister == '1') )

    def post(self):
        canRegister = pyCache.WebOptions['users_can_register']
        if canRegister !='1':
            self.print_result(False, "registration is now closed!")
            return

        account = self.get_request("account", "")
        email = self.get_request("email", "")
        url = self.get_request("personal_url", "", False)
        displayName = self.get_request("display_name", "")
        password = self.get_request("password", "")
        validcode = self.get_request("valid_code", "")

        if not pyUtility.isAccountLegal(account):
            self.print_result(False, "The Format of Account is wrong!")
            return
        if not pyUtility.isEmail(email):
            self.print_result(False, "The Format of Email is wrong!")
            return

        if not url =="":
            tmp = url.lower()
            if not tmp.startswith("http"):
                url = "http://"+url
            if not pyUtility.isURL(url):
                self.print_result(False, "The Format of URL is wrong!")
                return

        if account == "" or email == "" or password == "" or validcode == "":
            self.print_result(False, "some of fields can not be blank")
            return
        if "registercode" in self.session:
            if validcode != self.session['registercode']:
                del self.session['registercode']
                self.print_result(False, "Validation Code is incorrect!")
                return
        else:
            self.print_result(False, "Validation Code is empty!")
            return
            # register process
        del self.session['registercode']

        chk = User().isUnique(acc=account, email=email)
        if not chk:
            self.print_result(False, "Account or Email has been used, Try another one!")
            return

        user = User()
        user.user_login = account
        user.user_email = email
        user.user_pass = user.getEncodeStr(password)
        user.user_url = url
        user.display_name = displayName
        # ts = str(time.time())
        activationKey = user.getEncodeStr(str(account) + "-secret-")
        user.user_activation_key = activationKey
        if user.save() >0:
            self.print_result(True, "The Register Letter Has been sent to your email.")
            """
                Send Email to register
            """
            p = dict(
                activationKey=activationKey,
                login_user=account,
                admin_email=pyCache.WebOptions['admin_email'],
                website_url=self.webroot_url("", True)
            )
            msg = self.render_string("email/register.html", **p)
            subject = "[" + self.web_title() + "] Thank you for joining us"
            qm = SingleMail.get_instance()
            qm.send_email(email, subject, msg, 'html')
        else:
            self.print_result(False, "Error, When save to db")


class LogoutHandler(BaseHandler):
    def get(self):
        self.delOnlineStatus()
        self.session.clear()
        self.redirect(self.get_webroot_url())
