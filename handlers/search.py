#encoding:utf-8
import re

from tornado.web import HTTPError, UIModule
from tornado.options import options
from .base import BaseHandler
from libs.cache import mem_cache
from libs import util

class SearchHandler(BaseHandler):
    def get(self,query):
        query = util.safe_input(query)
        current_page = int(self.get_argument("p",1))
        query = re.compile(query,re.IGNORECASE)
        query = {"name":query} if query else {}
        result = util.pages(self.database,collection='seed',current_page=current_page, query=query)
        result['no_result'] = "暂无数据，试试其他关键词吧＝)"
        self.render("index.html",**result)


handlers = [
        (r"/search(?:/q_([^\s]*))?",SearchHandler),
]

ui_modules = {
}
