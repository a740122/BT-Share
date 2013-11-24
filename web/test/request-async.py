#!/usr/bin/env python
# encoding: utf-8
#!/bin/env python

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.gen
import tornado.httpclient
import tornado.concurrent
import tornado.ioloop

import time

from pymongo import Connection

from tornado.options import define, options
define("port", default=8000, help="run on the given port", type=int)

#init db
c = Connection()
db = c["bt_tornado"]

class SleepHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    # @tornado.gen.coroutine
    def get(self):
        result = db.seed.find().limit(2000)
        for temp in result:
            # yield temp
            self.write(temp)
        self.finish()
        # yield tornado.gen.Task(db.seed.find(), None)
        # self.write("when i sleep 5s")
    # def get(self):
        # time.sleep(1000)
        # http = tornado.httpclient.AsyncHTTPClient()
        # http.fetch("http://friendfeed-api.com/v2/feed/bret",
                   # callback=self.on_response)
        # self.write("when i sleep 5s")

    def on_response(self, response):
        if response.error: raise tornado.web.HTTPError(500)
        json = tornado.escape.json_decode(response.body)
        self.write("Fetched " + str(len(json["entries"])) + " entries "
                   "from the FriendFeed API")
        self.finish()




class JustNowHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("i hope just now see you")

if __name__ == "__main__":
    tornado.options.parse_command_line()
    app = tornado.web.Application(handlers=[
            (r"/sleep", SleepHandler), (r"/justnow", JustNowHandler)])
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
