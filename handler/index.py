#!/usr/bin/env python
# encoding: utf-8
from .base import BaseHandler
# from libs.cache import mem_cache


class IndexHandler(BaseHandler):

    def get(self):
        #TODO support feed
        feed = self.get_argument("feed", None)
        if feed == 'rss':
            self.render("feed.html")
            return

        current_page = int(self.get_argument("p", 1))
        result = self.seed_model.get_seeds(current_page=current_page)
        result["no_result"] = "嗷嗷，暂时木有内容哦～"

        self.render("index.html", **result)


class FeedHandler(BaseHandler):
    def get(self):
        self.redirect("/?feed=rss", True)


# class SitemapHandler(BaseHandler):
#     def get(self):
#         taskids = self.task_manager.get_task_ids()
#         tags = self.task_manager.get_tag_list()
#         self.render("sitemap.xml", taskids=taskids, tags=tags)


# class TagHandler(BaseHandler):
#     def get(self, tag):
#         if not self.has_permission("view_tasklist"):
#             self.set_status(403)
#             self.render("view_tasklist.html")
#             return

#         feed = self.get_argument("feed", None)
#         tasks = self.task_manager.get_task_list(t=tag, limit=TASK_LIMIT)
#         if feed:
#             self.set_header("Content-Type", "application/atom+xml")
#             self.render("feed.xml", tasks=tasks)
#         else:
#             self.render("index.html", tasks=tasks, query={"t": tag})


# class NoIEHandler(BaseHandler):
#     def get(self):
#         self.render("no-ie.html")
