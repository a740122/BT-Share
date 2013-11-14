#!/usr/bin/env python
# encoding: utf-8

import datetime
import tornado
from bson.dbref import DBRef
from bson.timestamp import Timestamp
from pymongo import DESCENDING


# from database import Database
from conf.config import BT_PAGE_SIZE, BT_MAX_ENTRY_NUM


class Model(object):

    def __init__(self):
        pass

    def dbref(self, table, object_id):
        """

        Arguments:
        - `self`:
        - `table`:
        - `object_id`:
        """
        return DBRef(table, object_id)

    @property
    def timestamp(self):
        """

        Arguments:
        - `self`:

        """
        return Timestamp(datetime.datetime.now(), 0)

    @tornado.gen.coroutine
    def insert(self, parameters):
        """

        Arguments:
        - `self`:
        - `documents`:
        """
        result = yield self.db.insert(self.table, parameters)
        raise tornado.gen.Return(result)

    @tornado.gen.coroutine
    def get(self, parameters):
        """

        Arguments:
        - `self`:
        - `parameters`:
        """
        result = yield self.db.find_one(self.table, parameters)
        raise tornado.gen.Return(result)

    @tornado.gen.coroutine
    def get_id(self):
        """

        Arguments:
        - `self`:
        """
        result = yield self.db.get_id(self.table)
        raise tornado.gen.Return(result)

    @tornado.gen.coroutine
    def query(self, parameters, offset=0, limit=None, sort=None, order=DESCENDING, fields=None, callback=None):
        """

        Arguments:
        - `self`:
        - `parameters`:
        - `offset`:
        - `limit`:
        - `sort`:
        - `fields`:
        """
        result = yield self.db.query(self.table, parameters, sort, offset, limit, order, fields)
        raise tornado.gen.Return(result)

    @tornado.gen.coroutine
    def get_count(self, parameters={}):
        """

        Arguments:
        - `self`:
        - `parameters`:
        """
        result = yield self.db.get_count(self.table, parameters)
        raise tornado.gen.Return(result)
    @tornado.gen.coroutine
    def remove(self, parameters):
        """

        Arguments:
        - `self`:
        - `parameters`:
        """
        result = yield self.db.remove(self.table, parameters)
        raise tornado.gen.Return(result)

    @tornado.gen.coroutine
    def update(self, parameters, update):
        result = yield self.db.update(self.table, parameters, update)
        raise tornado.gen.Return(result)

    def pages(self, count=1, current_page=1, list_rows=BT_PAGE_SIZE, cheat=False):

        count = count if count < BT_MAX_ENTRY_NUM else BT_MAX_ENTRY_NUM
        pages = count / list_rows
        pages = pages + 1 if not count % list_rows == 0 else pages

        if(pages == 0): pages = 1
        if(current_page < 1): current_page = 1
        if(current_page > pages): current_page = pages

        previous_page = current_page - 1 if current_page > 1 else 1
        next_page = current_page + 1 if current_page < pages else pages

        result =  {  "prev": previous_page,
                     "next": next_page,
                     "current": current_page,
                     "pages": pages,
                     "total": count,
                 }

        return result
