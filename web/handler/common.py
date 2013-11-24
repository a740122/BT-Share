#!/usr/bin/env python
# encoding: utf-8
from .base import BaseHandler


class Better404(BaseHandler):

    def get(self):
        result = {}
        self.set_status(404)
        self.render("404.html", **result)
