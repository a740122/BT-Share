#encoding:utf-8
import sys

from datetime import datetime
import pymongo
from pymongo import Connection
from pymongo.errors import ConnectionFailure

from tornado.options import options

connection = pymongo.Connection()
database = connection['bt_tornado']
