#!/usr/bin/env python
# encoding: utf-8
import os
import inspect

SITE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))))

MONGO = {
    'host': '127.0.0.1',
    'port': 27017,
    'db': 'test'
}

# how long would we wait the request of torrent
REQUEST_TIMEOUT = 10 # secs

# how many items should we update in an update task
UPDATE_NUM = 1000

try:
    from local_settings import *
except:
    pass
