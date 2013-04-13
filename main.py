#encoding:utf8
import os
import tornado
import sys
sys.path.insert(0, os.getcwd())

from tornado import web
from tornado.ioloop import IOLoop, PeriodicCallback
from tornado.options import define, options
from tornado.httpserver import HTTPServer

define("f", default="tornado_config.cfg", help="config file path")
define("debug", default=True, help="debug mode")
define("port", default=8880, help="the port tornado listen to")
define("bind_ip", default="0.0.0.0", help="the bind ip")
define("ga_account", default="", help="account of google analytics")
define("site_name", default="BT_Share", help="site name used in description")
define("cookie_secret", default="61oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o",
       help="key for HMAC")
define("cache_enabled", default=True,
       help="enable mem cache")
define("using_xss", default=False,
       help="use xss or cross-cookie")
define("using_xsrf", default=False,
       help="using xsrf to prevent cross-site request forgery")
define("reg_key", default=None,
       help="if setted new user is not allowed \
       except login with '/login?key=<reg_key>'.")

class Application(web.Application):
    def __init__(self):
        """"""
        from handlers import handlers, ui_modules
        from libs.util import ui_methods
        from db.Database import Database
        from libs.user_manager import UserManager
        from libs.log_manager import LogManager

        settings = dict(
            debug=options.debug,
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "pub"),
            cookie_secret=options.cookie_secret,
            login_url="/auth/login",

            ui_modules=ui_modules,
            ui_methods=ui_methods,
        )
        super(Application, self).__init__(handlers, **settings)

        self.database = Database(db='bt_tornado')
        self.user_manager = UserManager(self.database)
        self.log_manager = LogManager(logFile="application.log",
                                      logLevel=5, logTree="Main")
        self.log_manager.logger.info(
            "load finished! listening on %s:%s"
            % (options.bind_ip, options.port))


def main():
    tornado.options.parse_command_line()
    if options.f:
        tornado.options.parse_config_file(options.f)
    tornado.options.parse_command_line()

    http_server = HTTPServer(Application(), xheaders=True)
    http_server.bind(options.port, options.bind_ip)
    http_server.start()

    IOLoop.instance().start()

if __name__ == "__main__":
    main()
