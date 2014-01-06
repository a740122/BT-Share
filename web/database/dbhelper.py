#!/usr/bin/env python
# encoding: utf-8

import motor
import pymongo
import tornado
from pymongo.son_manipulator import AutoReference, NamespaceInjector

from conf.config import MONGODB_SETTINGS


class Database(object):

    #Singleton design pattern
    @classmethod
    def get_instance(cls):
        if not hasattr(cls, '_instance'):
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        host = MONGODB_SETTINGS['host']
        port = MONGODB_SETTINGS['port']
        max_pool = MONGODB_SETTINGS['max_pool']
        self.connection = motor.MotorClient(host, port, max_pool).open_sync()
        self.db = self.connection[MONGODB_SETTINGS["database"]]
        self.db.add_son_manipulator(NamespaceInjector())
        self.db.add_son_manipulator(AutoReference(self.db))

    @tornado.gen.coroutine
    def insert(self, table, documents):
        """

        Arguments:
        - `self`:
        - `table`:
        - `documents`:
        """
        result = yield motor.Op(self.db[table].insert, documents)
        raise tornado.gen.Return(result)

    @tornado.gen.coroutine
    def query(self, table, parameters, sort, offset, limit, order=pymongo.DESCENDING, fields=None):
        """

        Arguments:
        - `self`:
        - `table`:
        - `parameters`:
        - `sort`:
        - `offset`:
        - `limit`:
        - `fields`:
        """
        result = yield motor.Op(self.db[table].find(parameters, fields).skip(offset).limit(limit).sort(sort, order).to_list)
        raise tornado.gen.Return(result)

    @tornado.gen.coroutine
    def get_count(self, table, parameters):
        """

        Arguments:
        - `self`:
        - `table`:
        - `parameters`:
        """
        result = yield motor.Op(self.db[table].find(parameters).count)
        raise tornado.gen.Return(result)

    @tornado.gen.coroutine
    def get_id(self, table):
        """

        Arguments:
        - `self`:
        - `table`:
        """
        value = yield motor.Op(self.db["ids"].find_and_modify({"name": table}, {"$inc": {"value": 1}}, new=True, upsert=True))
        raise tornado.gen.Return(value["value"])

    @tornado.gen.coroutine
    def find_one(self, table, parameters):
        """

        Arguments:
        - `self`:
        - `table`:
        - `parameters`:
        """
        result = yield motor.Op(self.db[table].find_one, parameters)
        raise tornado.gen.Return(result)

    @tornado.gen.coroutine
    def update(self, table, parameters, update, safe=True):
        """

        Arguments:
        - `self`:
        - `table`:
        - `parameters`:
        - `update`:
        - `safe`:
        """

        result = yield motor.Op(self.db[table].update(parameters, update, safe))
        raise tornado.gen.Return(result)

    def dereference(self, dbref):
        """

        Arguments:
        - `self`:
        - `dbref`:
        """
        return self.db.dereference(dbref)

    @tornado.gen.coroutine
    def remove(self, table, parameters):
        """

        Arguments:
        - `self`:
        - `table`:
        - `parameters`:
        """
        result = yield motor.Op(self.db[table].remove, parameters)
        raise tornado.gen.Return(result)
