#encoding:utf-8
import os
import inspect

SITE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))))

# mongodb
MONGODB_SETTINGS = {
    'host': 'localhost',
    'port': 27017,
    'max_pool': 300,
    "database": "bt_tornado",
}

# pagination
BT_PAGE_SIZE = 20
BT_MAX_ENTRY_NUM = 5 * BT_PAGE_SIZE

try:
    from local_settings import *
except:
    pass
