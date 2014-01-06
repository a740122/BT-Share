#!/usr/bin/env python
# encoding: utf-8
import logging
import traceback
import thread
import tornado
from datetime import datetime
from multiprocessing import Pipe


def email2name(request, email):
    return request.user_manager.get_name(email)


def email2id(request, email):
    return request.user_manager.get_id(email)


def format_time(request, num):
    try:
        result = datetime.fromtimestamp(num).date()
    except:
        result = ""
    return result


def safe_input(raw_input):
    """
        SAFE!
    """
    safe_input = raw_input
    return safe_input


# use closure and decorator to create singleton
def singleton(cls):
    instances = {}

    def getinstance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    return getinstance


class AsyncProcessMixin(object):
    def call_subprocess(self, func, callback=None, args=[], kwargs={}):
        self.ioloop = tornado.ioloop.IOLoop.instance()
        self.pipe, child_conn = Pipe()

        def wrap(func, pipe, args, kwargs):
            try:
                pipe.send(func(*args, **kwargs))
            except Exception, e:
                logging.error(traceback.format_exc())
                pipe.send(e)

        self.ioloop.add_handler(self.pipe.fileno(),
                                self.async_callback(self.on_pipe_result, callback),
                                self.ioloop.READ)
        thread.start_new_thread(wrap, (func, child_conn, args, kwargs))

    def on_pipe_result(self, callback, fd, result):
        try:
            ret = self.pipe.recv()
            if isinstance(ret, Exception):
                raise ret

            if callback:
                callback(ret)
        finally:
            self.ioloop.remove_handler(fd)

ui_methods = {
    "email2name": email2name,
    "email2id": email2id,
    "format_time": format_time,
}
