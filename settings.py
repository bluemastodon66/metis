# import logging
import tornado.template
import os
from tornado.options import define, options

# Make filepaths relative to settings.
path = lambda root,*a: os.path.join(root, *a)
ROOT = os.path.dirname(os.path.abspath(__file__))

define("port", default=8888, help="run on the given port", type=int)
define("config", default=None, help="tornado config file")
define("debug", default=False, help="debug mode")

# DB Settings
define("mysql_host", default="127.0.0.1:3306", help="blog database host")
define("mysql_database", default="demo", help="database name")
define("mysql_user", default="demo", help="blog database user")
define("mysql_password", default="xxxxxx", help="blog database password")
define("mysql_poolsize", default=15, help="pool size for db")
# Redis Settings

define("redis_host", default="127.0.0.1", help="redis host")
define("redis_port", default= 6379, help="redis port")
define("redis_auth", default=None, help="password for redis")
# these two must be different
define("redis_db", default=2, help="which db")
define("redis_cache_db", default=3, help="cache db")

tornado.options.parse_command_line()

MEDIA_ROOT = path(ROOT, 'static')
TEMPLATE_ROOT = path(ROOT, 'templates')

# Deployment Configuration

class DeploymentType:
    PRODUCTION = "PRODUCTION"
    DEV = "DEV"
    SOLO = "SOLO"
    STAGING = "STAGING"
    dict = {
        SOLO: 1,
        PRODUCTION: 2,
        DEV: 3,
        STAGING: 4
    }

if 'DEPLOYMENT_TYPE' in os.environ:
    DEPLOYMENT = os.environ['DEPLOYMENT_TYPE'].upper()
else:
    DEPLOYMENT = DeploymentType.SOLO

settings = {}
settings['debug'] = DEPLOYMENT != DeploymentType.PRODUCTION or options.debug
settings['static_path'] = MEDIA_ROOT
settings['upload_dir'] = 'uploads/'
settings['upload_path'] = MEDIA_ROOT+ "/"+ settings['upload_dir']
settings['cookie_secret'] = "thisisyoursecret"
settings["session_name"] = 'session_id'
settings['session_timeout'] = 3600  # seconds
settings['session_prefix'] = "-metis-"
settings['xsrf_cookies'] = False
settings['template_loader'] = tornado.template.Loader(TEMPLATE_ROOT)
settings['webroot_path'] = "/"
settings['login_url'] = "auth/login/"
settings['xheaders'] = True

settings['web_site_email'] = "xxxx@gmail.com"
settings['smtp_host'] = "smtp.gmail.com"
settings['smtp_account'] = "xxxx@gmail.com"
settings['smtp_password'] = "****"
settings['smtp_port'] = 465

if options.config:
    tornado.options.parse_config_file(options.config)
