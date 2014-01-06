#!/usr/bin/env python
# encoding: utf-8
import tornado
from tornado import gen

from .base import BaseHandler
#from libs.cache import mem_cache


class IndexHandler(BaseHandler):

    @tornado.web.asynchronous
    @gen.engine
    def get(self):
        #TODO support feed
        feed = self.get_argument("feed", None)
        if feed == 'rss':
            self.render("feed.html")
            return

        current_page = int(self.get_argument("p", 1))
        result = yield self.seed_model.get_seeds(current_page=current_page)
        result["no_result"] = "嗷嗷，暂时木有内容哦～"

        self.render("index.html", **result)


class FeedHandler(BaseHandler):
    def get(self):
        self.redirect("/?feed=rss", True)
