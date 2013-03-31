# #coding:utf8

# """
# database.py
# ~~~~~~~~~~~~~

# 该模块提供爬虫所需的mongo数据库的创建、连接、断开，以及数据的存储功能。
# """

from pymongo import Connection
from pymongo.errors import ConnectionFailure

class Database(object):
    def __init__(self):
        try:
            self.conn = Connection(host='localhost', port=27017)
        except ConnectionFailure, e:
            self.conn = None

    def isConn(self):
        if self.conn:
            return True
        else:
            return False

    def saveData(self, url='', db='', collection='',document=''):
        if self.conn:
            dbh = self.conn[db]
            if dbh[collection].find_one({"id":document['id']}):
                dbh[collection].update({"id":document['id']},{"$set":document})
            else:
                dbh[collection].save(document, safe=True)
        else:
            # do log
            pass

    def getAllData(self, db='', collection=''):
        if self.conn and db and collection:
            return self.conn[db][collection].find()
        else:
            return []

    def close(self):
        if self.conn:
            pass
        else :
            pass

    def saveMedia(self, ):
        pass
