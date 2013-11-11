#!/usr/bin/env python
# encoding: utf-8

import pymongo
from conf.config import MONGODB_SETTINGS
from pymongo.son_manipulator import AutoReference, NamespaceInjector


class Database(object):

    # def __new__(cls, *args, **kwargs):

    #     if not hasattr(cls, '_instance'):
    #         orig = super(Database, cls)
    #         cls._instance = orig.__new__(cls, *args, **kwargs)
    #     return cls._instance

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
        self.connection = pymongo.MongoClient(host, port, max_pool)
        self.db = self.connection[MONGODB_SETTINGS["database"]]
        self.db.add_son_manipulator(NamespaceInjector())
        self.db.add_son_manipulator(AutoReference(self.db))

    def insert(self, table, documents):
        """

        Arguments:
        - `self`:
        - `table`:
        - `documents`:
        """
        return self.db[table].insert(documents)

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
        cursor = self.db[table].find(parameters, fields).skip(offset).limit(limit)
        cursor.sort(sort, order)
        return cursor

    def get_count(self, table, parameters):
        """

        Arguments:
        - `self`:
        - `table`:
        - `parameters`:
        """
        return self.db[table].find(parameters).count()

    # auto increasing id for tables to avoid exploring _id to outside in case of attacks
    def get_id(self, table):
        """

        Arguments:
        - `self`:
        - `table`:
        """
        value = self.db["ids"].find_and_modify({"name": table}, {"$inc": {"value": 1}}, new=True, upsert=True)
        return value["value"]

    def find_one(self, table, parameters):
        """

        Arguments:
        - `self`:
        - `table`:
        - `parameters`:
        """
        return self.db[table].find_one(parameters)

    def update(self, table, parameters, update, safe=True):
        """

        Arguments:
        - `self`:
        - `table`:
        - `parameters`:
        - `update`:
        - `safe`:
        """

        return self.db[table].update(parameters, update, safe)

    def dereference(self, dbref):
        """

        Arguments:
        - `self`:
        - `dbref`:
        """
        return self.db.dereference(dbref)

    def remove(self, table, parameters):
        """

        Arguments:
        - `self`:
        - `table`:
        - `parameters`:
        """
        self.db[table].remove(parameters)
