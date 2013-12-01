#!/usr/bin/env python

import tornado.httpserver
import tornado.ioloop
import tornado.web
from tornado.options import options
import sys, traceback
from settings import settings
from urls import url_patterns
import redis
from session.redis import RedisSessionStore
import logging
from libs.pyEmail import SingleMail
import init



class TornadoApp(tornado.web.Application):
    isSuccess=False
    def __init__(self):
        SingleMail.get_instance().init(settings['smtp_host'], settings['smtp_account'], settings['smtp_password'], settings['web_site_email'],settings['smtp_port'])
        tornado.web.Application.__init__(self, url_patterns, **settings)
        self.redis = redis.StrictRedis(host=options.redis_host, port=options.redis_port, 
                                       db=options.redis_db,password=options.redis_auth)
        try:
            self.redis.echo("t")
        except:
            print "[Error] connect to redis server failed"
            return
        self.redis_cache = redis.StrictRedis(host=options.redis_host, port=options.redis_port,
                                       db=options.redis_cache_db,password=options.redis_auth)
        self.session_store = RedisSessionStore(self.redis,**settings)
        self.isSuccess=True
def starWebService():
    app = TornadoApp()
    if not app.isSuccess:
        return
    print "************** Start WebServer ********************"
    print "***************************************************"
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    logging.info("Tornado server started\nPort: {0}\nDebug Mode: {1}".format(options.port, options.debug))
    try:
        tornado.ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        logging.info("Shutdown requested...exiting")
    except Exception:
        traceback.print_exc(file=sys.stdout)
def main():
    if init.isStarted():
        starWebService()
    else:
        print "[Error] Init Failed"
    sys.exit(0)
if __name__ == "__main__":
    main()
