#!/usr/bin/env python
# encoding: utf-8
import tornado

from .base import BaseHandler
from model import Seed


class DetailHandler(BaseHandler):

    @property
    def seed_dal(self): return Seed()

    def get(self, filename):
        context = {}
        source_info = None

        if not filename:
            raise tornado.web.HTTPError(404)

        try:
            query = {"_id":int(filename)} if filename else {}
        except:
            raise tornado.web.HTTPError(404)

        source_info = self.seed_dal.get(query)

        if not source_info:
            raise tornado.web.HTTPError(404)

        context['source_info'] = source_info

        self.render("detail.html",**context)
