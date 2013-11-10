#!/usr/bin/env python
# encoding: utf-8

from model import Model
from conf.config import BT_PAGE_SIZE

class Seed(Model):

    def __init__(self, database="bt_tornado", table="seed"):
        super(Seed, self).__init__(database, table)

    def get_seeds(self, current_page=1, parameters={}, limit=BT_PAGE_SIZE, sort="_id"):
        result = {}
        # TODO change 2 to 1 check
        count = self.get_count(parameters)
        offset = (current_page-1) * limit

        result["seeds"] = self.query(parameters, offset=offset, limit=limit, sort=sort)
        result["page"] = self.pages(current_page=current_page, count=count)

        return result
