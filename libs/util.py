#encoding:utf-8
import logging
import traceback
import thread
import tornado
from time import time
from datetime import datetime
from multiprocessing import Pipe
from libs.config import *


units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
def format_size(request, size):
    i = 0
    while size > 1024:
        size /= 1024
        i += 1
    return "%d%s" % (size, units[i])

d_status = {
        "finished": u"完成",
        "downloading": u"下载中",
        "waiting": u"队列中",
        "failed": u"下载失败",
        "paused": u"暂停中",
}
def format_download_status(request, status):
    return d_status.get(status, u"未知状态")

def email2name(request, email):
    return request.user_manager.get_name(email)

def email2id(request, email):
    return request.user_manager.get_id(email)

def format_time(request,num):
    try:
        result = datetime.fromtimestamp(num).date()
    except:
        result = ""
    return result

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


def pages(database='',collection='seed', current_page = 1, query = {} , list_rows = ITEM_LIMIT):

    result_set = database.db[collection].find(query)
    count = result_set.count()

    pages = count / list_rows
    pages = pages + 1 if not count % list_rows == 0 else pages
    if(pages == 0): pages = 1
    if(current_page < 1): current_page = 1
    if(current_page > pages): current_page = pages
    start = (current_page - 1) * list_rows
    end = list_rows
    previous_page = current_page - 1 if current_page > 1 else 1
    next_page = current_page + 1 if current_page < pages else pages

    result = {}

    result["seeds"] = result_set.skip(start).limit(end)

    result["page"] = {
        "prev": previous_page,
        "next": next_page,
        "current": current_page,
        "pages": pages,
        "total": count,
    }

    result['query'] = query

    return result


ui_methods = {
        "format_size": format_size,
        "format_status": format_download_status,
        "email2name": email2name,
        "email2id": email2id,
        "format_time":format_time,
}
