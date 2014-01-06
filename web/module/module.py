#!/usr/bin/env python
# encoding: utf-8
import re
from tornado.web import UIModule

from conf.config import BT_PAGE_SIZE


#TODO it is may not be good to put it here to make the pager class scattered
class Pagination(UIModule):

    def render(self, page, uri, list_rows=BT_PAGE_SIZE):

        def gen_page_list(current_page=1, total_page=1, list_rows=BT_PAGE_SIZE):
            #TODO add ajax pager support
            return range(1, total_page + 1)

        def build_uri(uri, param, value):
            regx = re.compile("[\?&](%s=[^\?&]*)" % param)
            find = regx.search(uri)
            split = "&" if re.search(r"\?", uri) else "?"
            if not find:
                return "%s%s%s=%s" % (uri, split, param, value)
            return re.sub(find.group(1), "%s=%s" % (param, value), uri)

        return self.render_string("pagination.html", page=page, uri=uri, gen_page_list=gen_page_list, list_rows=list_rows, build_uri=build_uri)
