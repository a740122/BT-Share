#!/usr/bin/env python
# encoding: utf-8
import traceback

from tornado.web import RequestHandler
from tornado.options import options


class BaseHandler(RequestHandler):

    def render_string(self, template_name, **kwargs):
        kwargs["options"] = options
        return super(BaseHandler, self).render_string(template_name, **kwargs)

    def get_current_user(self):
        pass

    def write_error(self, status_code, **kwargs):
        """

        Arguments:
        - `self`:
        - `status_code`:
        - `**kw`:
        """

        if self.settings.get("debug") and "exc_info" in kwargs:
            #in debug mode
            self.set_header("Content-Type", "text/plain")
            self.set_status(status_code)

            exc_info = kwargs["exc_info"]
            trace_info = ''.join(["%s<br/>" % line for line in traceback.format_exception(*exc_info)])
            request_info = ''.join(["<strong>%s</strong>: %s<br/>" % (k, self.request.__dict__[k]) for k in self.request.__dict__.keys()])
            error = exc_info[1]

            self.set_header('Content-Type', 'text/html')
            self.finish("""<html>
                        <title>%s</title>
                         <body>
                            <h2>Error</h2>
                            <p>%s</p>
                            <h2>Traceback</h2>
                            <p>%s</p>
                            <h2>Request Info</h2>
                            <p>%s</p>
                         </body>
                       </html>""" % (error, error,
                                     trace_info, request_info))
        else:
            self.redirect("/404")

    @property
    def seed_model(self):
        return self.application.seed_model

    @property
    def search_engine(self):
        return self.application.search_engine

    @property
    def loader(self):
        return self.application.loader
