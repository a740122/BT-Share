#!/usr/bin/env python
# encoding: utf-8

#persitent layer
import redis
import txmongo
import logger

import config


# a mongo db wrapper
class MongoDb(object):

    def __init__(self):
        pass

    def get_instance(self):
        pass

    def save_routing_table(self):
        pass

    def get_routing_table(self):
        pass

    def save_source(self):
        pass

    def get_source(self):
        pass


# a cache layer
class RedisCache(object):

    def __init__(self, db=None):
        self.db = db
        self.rdCache = redis

    def save_all_nodes(self, node_id=None, host=None, port=None):
        pass

    def get_all_nodes(self, node_id=None):
        pass

    def save_resource(self, source_hash=None, nodes_list=None):
        pass

    def get_resouce(self, souce_hash=None):
        pass

    def save_resource_to_db(self):
        pass
