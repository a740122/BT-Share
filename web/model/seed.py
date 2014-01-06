#!/usr/bin/env python
# encoding: utf-8
import tornado

from model import Model
from conf.config import BT_PAGE_SIZE


class SeedModel(Model):

    def __init__(self, db=None, table="source_info"):
        self.db = db
        self.table = table
        super(SeedModel, self).__init__()

    @tornado.gen.coroutine
    def get_seeds(self, current_page=1, parameters={}, limit=BT_PAGE_SIZE, sort="_id", callback=None):
        result = {}
        count = yield self.get_count(parameters)
        offset = (current_page-1) * limit

        result["seeds"] = yield self.query(parameters, offset=offset, limit=limit, sort=sort)
        result["page"] = self.pages(current_page=current_page, count=count)
        raise tornado.gen.Return(result)
