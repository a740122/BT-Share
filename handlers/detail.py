#encoding:utf-8
import re
from bson import ObjectId

from tornado.web import HTTPError, UIModule
from tornado.options import options
from .base import BaseHandler
from libs import util
from libs.cache import mem_cache

class DetailHandler(BaseHandler):

    def get(self,source_name):

        context = {}

        #TODO
        query = source_name
        # query = re.compile(query,re.IGNORECASE)
        query = {"_id":ObjectId(query)} if query else {}

        source_info = self.database.db['seed'].find_one(query)

        context['source_info'] = source_info

        self.render("detail.html",**context)

handlers = [
        (r"/detail/(\w+)", DetailHandler),
]

ui_modules = {
}
