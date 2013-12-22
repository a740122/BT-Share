#!/usr/bin/env python
# encoding: utf-8
import tornado

from .base import BaseHandler


class DetailHandler(BaseHandler):

    @tornado.web.asynchronous
    @tornado.gen.engine
    def get(self, filename):
        context = {}
        source_info = None

        if not filename:
            raise tornado.web.HTTPError(404)

        #TODO security check here

        try:
            query = {"_id":filename} if filename else {}
        except:
            raise tornado.web.HTTPError(404)

        source_info = yield self.seed_model.get(query)

        if not source_info:
            raise tornado.web.HTTPError(404)

        context['source_info'] = source_info

        self.render("detail.html",**context)
