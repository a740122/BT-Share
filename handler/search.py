#!/usr/bin/env python
# encoding: utf-8
import tornado

from .base import BaseHandler
from libs import util
# from libs.cache import mem_cache


class SearchHandler(BaseHandler):

    @tornado.web.asynchronous
    @tornado.gen.engine
    def get(self, query):
        context ={}
        query = util.safe_input(query)
        current_page = int(self.get_argument("p",1))

        result = yield self.search_engine.search_seeds(query, current_page)
        if result:
            context.update(result)
        context['query'] = {"q": query}
        context['no_result'] = "暂无数据，试试其他关键词吧＝)"

        self.render("search.html", **context)
