#!/usr/bin/env python
# encoding: utf-8
import os
import tornado
from tornado import web
from tornado.ioloop import IOLoop
from tornado.options import define, options
from tornado.httpserver import HTTPServer

import handler.index
import handler.common
import handler.detail
import handler.search
import module
from libs.loader import Loader
from libs.util import ui_methods
from libs.log_manager import LogManager
from database import Database
from model.search_engine import SearchEngine

define("debug", default=True, help="debug mode")
define("f", default="conf/config.py", help="config file")
define("port", default=8880, help="the port tornado listen to")
define("bind_ip", default="0.0.0.0", help="the bind ip")
define("ga_account", default="", help="account of google analytics")
define("site_name", default="BT_Share", help="site name used in description")
define("cookie_secret", default="61oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o", help="key for HMAC")
define("cache_enabled", default=True, help="enable mem cache")
define("using_xss", default=False, help="use xss or cross-cookie")
define("using_xsrf", default=False, help="using xsrf to prevent cross-site request forgery")
define("reg_key", default=None, help="if setted new user is not allowed except login with '/login?key=<reg_key>'.")


class Application(web.Application):
    def __init__(self):
        """
        """
        handlers = [
            (r"/", handler.index.IndexHandler),
            (r"/feed", handler.index.FeedHandler),
            (r"/404", handler.common.Better404),
            (r"/detail/(\w+)", handler.detail.DetailHandler),
            (r"/search/q_([^\s]*)", handler.search.SearchHandler),
            (r"/.*", handler.common.Better404),
            ## TODO may implement
            #(r"/sitemap\.xml", handler.index.SitemapHandler),
            # (r"/tag/(.+)", handler.index.TagHandler),
            # (r"/noie", handler.index.NoIEHandler),
            # (r"/auth/login", AuthLoginHandler),
            # (r"/auth/logout", AuthLogoutHandler),
        ]
        ui_modules = {
            "pagination": module.Pagination,
            # "tagsmodule": TagsModule,
            # "TagList": TagListModule,
        }
        settings = dict(
            debug=options.debug,
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "pub"),
            cookie_secret=options.cookie_secret,
            xsrf_cookies=False,
            autoescape=None,
            login_url="/auth/login",
            ui_modules=ui_modules,
            ui_methods=ui_methods,
        )
        super(Application, self).__init__(handlers, **settings)

        self.db = Database.get_instance()

        # Have one global loader for loading models and handlers
        self.loader = Loader(self.db)

        # Have one global model for db query
        self.seed_model = self.loader.use("seed.model")

        # Have one gloabl search engine to serve the search serive
        self.search_engine = SearchEngine(self.loader.loaded["model"])

        self.log_manager = LogManager(logFile="application.log",
                                      logLevel=5, logTree="Main")

        self.log_manager.logger.info(
            "load finished! listening on %s:%s"
            % (options.bind_ip, options.port))


def main():
    tornado.options.parse_command_line()
    if options.f:
        tornado.options.parse_config_file(options.f)

    http_server = HTTPServer(Application(), xheaders=True)

    http_server.bind(options.port, options.bind_ip)
    http_server.start()

    IOLoop.instance().start()

if __name__ == "__main__":
    main()
