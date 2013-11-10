#!/usr/bin/env python
# encoding: utf-8

import datetime
from bson.dbref import DBRef
from bson.timestamp import Timestamp
from pymongo import DESCENDING, ASCENDING

from database import Database
from conf.config import BT_PAGE_SIZE, BT_MAX_ENTRY_NUM


class Model(object):

    def __init__(self, database, table):
        self.database = database
        self.table = table

    @property
    def db(self):
        """

        Arguments:
        - `self`:
        """
        return Database(self.database)

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

    def insert(self, parameters):
        """

        Arguments:
        - `self`:
        - `documents`:
        """
        return self.db.insert(self.table, parameters)

    def get(self, parameters):
        """

        Arguments:
        - `self`:
        - `parameters`:
        """
        return self.db.find_one(self.table, parameters)

    def get_id(self):
        """

        Arguments:
        - `self`:
        """
        return self.db.get_id(self.table)

    def query(self, parameters, offset=0, limit=None, sort=None, order=DESCENDING, fields=None):
        """

        Arguments:
        - `self`:
        - `parameters`:
        - `offset`:
        - `limit`:
        - `sort`:
        - `fields`:
        """
        result = []
        cursor = self.db.query(self.table, parameters, sort, offset, limit, order, fields)

        if cursor and cursor.count():
            result = [item for item in cursor]
        return result


    def get_count(self, parameters={}):
        """

        Arguments:
        - `self`:
        - `parameters`:
        """
        return self.db.get_count(self.table, parameters)

    def remove(self, parameters):
        """

        Arguments:
        - `self`:
        - `parameters`:
        """
        return self.db.remove(self.table, parameters)

    def update(self, parameters, update):
        return self.db.update(self.table, parameters, update)


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
