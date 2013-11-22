#!/usr/bin/env python
# encoding: utf-8
from __future__ import unicode_literals

import inspect, os

ROOT_PATH = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

MONGO_SETTING = {
    'host': 'localhost',
    'port': 27017,
    'db': 'test',
    'c_ranking_list': 'ranking_list',
    'c_group': 'ranking_group',
}

REDIS_SETTING = {
    'redis': {
        'host': '127.0.0.1',
        'port': 6379,
        'db': 0,
    },
    'key_prefix': 'Q2::'
}

try:
    from local_settings import *
except:
    pass
