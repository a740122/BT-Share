#!/usr/bin/env python
# encoding: utf-8
import re
from tornado.web import UIModule

from conf.config import BT_PAGE_SIZE


#TODO it is may not be good to put it here to make the pager class scattered
class Pagination(UIModule):

    def render(self, page, uri,list_rows=BT_PAGE_SIZE):

        def gen_page_list(current_page = 1, total_page = 1, list_rows = BT_PAGE_SIZE):
            #TODO add ajax pager support
           return range(1, total_page + 1)

        def build_uri(uri, param, value):
            regx = re.compile("[\?&](%s=[^\?&]*)" % param)
            find = regx.search(uri)
            split = "&" if re.search(r"\?", uri) else "?"
            if not find: return "%s%s%s=%s" % (uri, split, param, value)
            return re.sub(find.group(1), "%s=%s" % (param, value), uri)

        return self.render_string("pagination.html",page = page, uri = uri, gen_page_list = gen_page_list, list_rows = list_rows,build_uri=build_uri)


#TODO add tags support
# class TagsModule(UIModule):
#     def render(self, tags):
#         if not tags:
#             return u"无"
#         result = []
#         for tag in tags:
#             result.append("""<a href="/tag/%s">%s</a>""" % (tag, tag))
#         return u", ".join(result)


# class TagListModule(UIModule):
#     # @mem_cache(60*60)
#     def render(self):
#         def size_type(count):
#             if count < 10:
#                 return 1
#             elif count < 100:
#                 return 2
#             else:
#                 return 3

#         tags = self.handler.task_manager.get_tag_list()
#         return self.render_string("tag_list.html",
#                                   tags=tags,
#                                   size_type=size_type)
