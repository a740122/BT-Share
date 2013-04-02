#coding:utf8

# """
# database.py
# ~~~~~~~~~~~~~

# 该模块提供爬虫所需的mongo数据库的创建、连接、断开，以及数据的存储功能。
# """

from pymongo import Connection
from pymongo.errors import ConnectionFailure
import logging
log = logging.getLogger('Main.spider')


class Database(object):
    def __init__(self, host='localhost', port=27017):
        try:
            self.conn = Connection(host='localhost', port=27017)
        except ConnectionFailure, e:
            log.error("connection error")
            self.conn = None

    def isConn(self):
        if self.conn:
            return True
        else:
            return False

    def saveData(self, db='', collection='', query='', document=''):
        dbh = self.conn[db]
        if dbh[collection].find_one(query):
            dbh[collection].update(query ,{"$set":document})
        else:
            dbh[collection].save(document, safe=True)

    def getAllData(self, db='', collection=''):
        if self.conn and db and collection:
            return self.conn[db][collection].find()
        else:
            return []

    def close(self):
        if self.conn:
            self.conn.close()
        else:
            pass

    def saveMedia(self, ):
        pass
