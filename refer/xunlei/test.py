#/bin/usr/env python
#encoding: utf8
#author: binux<17175297.hk@gmail.com>

import re
import time
import json
import logging
import requests
import xml.sax.saxutils
from hashlib import md5
from random import random, sample
from urlparse import urlparse
from pprint import pformat
from jsfunctionParser import parser_js_function_call

CHECK_URL = 'http://login.xunlei.com/check?u=%(username)s&cachetime=%(cachetime)d'


def test():
    session = requests.Session()
    r = session.get(CHECK_URL % {"username":"vtmers2012@gmail.com","cachetime":time.time()})
    import pdb
    pdb.set_trace()
    print (dir(r))

#test()

def test2():
    VERIFY_CODE = 'http://verify2.xunlei.com/image?cachetime=%s'
    session = requests.Session()
    r = session.get( VERIFY_CODE % time.time() )
    return r.content

print test2()
