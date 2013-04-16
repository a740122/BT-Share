#encoding:utf-8
from tornado.web import HTTPError, UIModule
from tornado.options import options
from .base import BaseHandler
from libs import util
from libs.cache import mem_cache


class IndexHandler(BaseHandler):

    def get(self):
        feed = self.get_argument("feed", None)
        current_page = int(self.get_argument("p", 1))

        result = util.pages(self.database,
                            collection='seed',
                            current_page=current_page)

        result['no_result'] = "嗷嗷，暂时木有内容哦～"

        self.render("index.html", **result)


class FeedHandler(BaseHandler):
    def get(self):
        self.redirect("/?feed=rss", True)


class SitemapHandler(BaseHandler):
    def get(self):
        taskids = self.task_manager.get_task_ids()
        tags = self.task_manager.get_tag_list()
        self.render("sitemap.xml", taskids=taskids, tags=tags)


class TagHandler(BaseHandler):
    def get(self, tag):
        if not self.has_permission("view_tasklist"):
            self.set_status(403)
            self.render("view_tasklist.html")
            return

        feed = self.get_argument("feed", None)
        tasks = self.task_manager.get_task_list(t=tag, limit=TASK_LIMIT)
        if feed:
            self.set_header("Content-Type", "application/atom+xml")
            self.render("feed.xml", tasks=tasks)
        else:
            self.render("index.html", tasks=tasks, query={"t": tag})


class NoIEHandler(BaseHandler):
    def get(self):
        self.render("no-ie.html")


class TagsModule(UIModule):
    def render(self, tags):
        if not tags:
            return u"无"
        result = []
        for tag in tags:
            result.append("""<a href="/tag/%s">%s</a>""" % (tag, tag))
        return u", ".join(result)


class TagListModule(UIModule):
    # @mem_cache(60*60)
    def render(self):
        def size_type(count):
            if count < 10:
                return 1
            elif count < 100:
                return 2
            else:
                return 3

        tags = self.handler.task_manager.get_tag_list()
        return self.render_string("tag_list.html",
                                  tags=tags,
                                  size_type=size_type)


handlers = [
    (r"/", IndexHandler),
    (r"/noie", NoIEHandler),
    (r"/feed", FeedHandler),
    #(r"/sitemap\.xml", SitemapHandler),
    (r"/tag/(.+)", TagHandler),
]

ui_modules = {
    "TagsModule": TagsModule,
    "TagList": TagListModule,
}
