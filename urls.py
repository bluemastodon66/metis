from handlers.public.welcome import WelcomeHandler

from handlers.base import BaseHandler

from handlers.public.topic import TopicHandler, TopicsMadeByUserHandler, TopicsFilterByTagHandler, TopicsFilterByCatHandler, TopicShowHandler
from handlers.restricted.topic_admin import TopicsAddHandler,TopicsEditHandler
from handlers.public.session_captcha import ValidCodeCaptchaHandler, RegisterCaptchaHandler
from handlers.public.auth import LoginHandler,LogoutHandler,LostPwdHandler,RegisterHandler,ResetPwdHandler,ActivateAccountHandler
from handlers.restricted.client import ResendActivatedKeyHandler,SettingClientHandler
from handlers.admin.admin import AdminHandler,AdminUserAddHandler,AdminUserEditHandler,AdminUserHandler,AdminWebOptionHandler
from handlers.admin.admin_term import AdminCategoriesHandler,AdminTagsHandler
from handlers.admin.admin_reply import ReplyAdminHandler
from handlers.admin.admin_topic import TopicsAdminHandler
from handlers.admin.admin_page import PagesAdminHandler
from handlers.public.reply import ReplyHandler, ReplyAddHandler
from handlers.restricted.term_admin import TermSearchHandler
from handlers.public.page import PageShowHandler
from handlers.restricted.page_admin import PageAddHandler,PageEditHandler
from handlers.public.rss import RSSHandler

from handlers.admin.admin_media import MediaAdminHandler, MediaAdminDeleteHandler, MediaAdminEditHandler
from handlers.restricted.media_admin import MediaAPIHandler
class ErrorHandler(BaseHandler):
    def get(self, *argc):
        self.render("404.html")


url_patterns = [

    (r"/", WelcomeHandler),
    (r"/session_captcha/validcode/", ValidCodeCaptchaHandler),
    (r"/session_captcha/register/", RegisterCaptchaHandler),
    (r"/admin[/]{0,}", AdminHandler),
    (r"/admin/users[/]{0,}", AdminUserHandler),
    (r"/admin/users/edit[/]{0,}", AdminUserEditHandler),
    (r"/admin/users/add[/]{0,}", AdminUserAddHandler),
    (r"/admin/topics[/]{0,1}", TopicsAdminHandler),
    (r"/admin/replies[/]{0,1}", ReplyAdminHandler),
    (r"/admin/pages[/]{0,1}",PagesAdminHandler),
    (r"/admin/categories[/]{0,}", AdminCategoriesHandler),
    (r"/admin/tags[/]{0,}", AdminTagsHandler),
    (r"/admin/web_option[/]{0,}", AdminWebOptionHandler),

    (r"/admin/media[/]{0,1}",MediaAdminHandler),
    (r"/admin/media/delete/([\d]+)[/]{0,1}", MediaAdminDeleteHandler),
    (r"/admin/media/edit/([\d]+)[/]{0,1}", MediaAdminEditHandler),

    (r"/auth/login[/]{0,}", LoginHandler),
    (r"/auth/lost_password[/]{0,}", LostPwdHandler),
    (r"/auth/reset_pass[/]{0,}", ResetPwdHandler),
    (r"/auth/activate[/]{0,}", ActivateAccountHandler),
    (r"/auth/register[/]{0,}", RegisterHandler),
    (r"/auth/logout_process[/]{0,}", LogoutHandler),

    (r"/client/resend_activate[/]{0,}", ResendActivatedKeyHandler),
    (r"/client/setting[/]{0,}", SettingClientHandler),
    (r"/media/api/([\d]+)", MediaAPIHandler),


    (r"/topic[/]{0,}", TopicHandler),
    (r"/topic/show/([\d]+)[/]{0,1}", TopicShowHandler),

    (r"/topic/user/([\d]+)[/]{0,1}", TopicsMadeByUserHandler),
    (r"/topic/tag/(.+)", TopicsFilterByTagHandler),
    (r"/topic/cat/(.+)", TopicsFilterByCatHandler),
    (r"/topic/edit/([\d]+)[/]{0,1}", TopicsEditHandler),
    (r"/topic/add[/]{0,1}", TopicsAddHandler),
    (r"/topic/term[/]{0,1}", TermSearchHandler),

    (r"/reply[/]{0,1}", ReplyHandler),
    (r"/reply/add/([\d]+)[/]{0,1}", ReplyAddHandler),


    (r"/page/([a-zA-Z\-0-9\.:,_/]+)", PageShowHandler),
    (r"/pages/add[/]{0,1}", PageAddHandler),
    (r"/pages/edit/([\d]+)[/]{0,1}", PageEditHandler),
    (r"/rss[/]{0,1}", RSSHandler),

    (r"/(.*)", ErrorHandler)

]
