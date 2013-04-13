#encoding:utf-8

from time import time
from tornado.web import RequestHandler
from tornado.options import options

class BaseHandler(RequestHandler):
    @property
    def database(self):
        return self.application.database

    @property
    def user_manager(self):
        return self.application.user_manager

    def render_string(self, template_name, **kwargs):
        kwargs["options"] = options
        return super(BaseHandler, self).render_string(template_name, **kwargs)

    def get_current_user(self):
        # fix cookie
        if self.request.cookies is None:
            return None
        email = self.get_secure_cookie("email")
        name = self.get_secure_cookie("name")
        if email and name:
            return {
                    "id": self.user_manager.get_id(email),
                    "email": email,
                    "name": name,
                   }
