#encoding:utf-8
#
SITE_ROOT = "/Users/admin/code/bt-share/"

# mongodb
MONGODB_SETTINGS = {
    'host': '127.0.0.1',
    'port': 11217,
    'max_pool': 300,
    "database": "bt_tornado",
}

# pagination
BT_PAGE_SIZE = 20
BT_MAX_ENTRY_NUM = 1000 * BT_PAGE_SIZE

try:
    from local_settings import *
except:
    pass
