#!/usr/bin/env python
# encoding: utf-8

from pymongo import Connection

def make_big_data():

    def get_id(collection=None):
        value = db_to["ids"].find_and_modify(
            {"name": collection}, {"$inc": {"value": 1}}, new=True, upsert=True)
        return value["value"]

    conn = Connection(host='localhost', port=27017)
    db_from = conn['bt_share']
    db_to = conn['bt_tornado']

    datas = db_from["seed"].find()
    # new_datas = []

    for doc in datas:
        doc["_id"] = get_id("seed")

    for newdata in datas:
        db_to['seed'].save(newdata)


for k in range(1, 10):
    make_big_data()
