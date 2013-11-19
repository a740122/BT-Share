#!/usr/bin/env python
# encoding: utf-8

import inspect, os


ROOT_PATH = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) # script directory

MONGO_SETTING = {

}

REDIS_SETTING = {


}

try:
    from local_settings import *
except:
    pass
