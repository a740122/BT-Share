#!/usr/bin/env python
# encoding: utf-8

from pymongo import Connection

def get_id(collection=None):
    value = db_to["ids"].find_and_modify(
        {"name": collection}, {"$inc": {"value": 1}}, new=True, upsert=True)
    return value["value"]

conn = Connection(host='localhost', port=27017)
db_from = conn['bt_share']
db_to = conn['bt_tornado']

datas = db_from["test"].find()
new_datas = []

for doc in datas:
    doc["_id"] = get_id("seed")
    new_datas.append(doc)

for newdata in new_datas:
   db_to['seed'].save(newdata)
