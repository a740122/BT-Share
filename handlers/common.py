#encoding:utf-8
import re
from tornado.web import UIModule
from libs.config import *

class Pagination(UIModule):

    def render(self, page, uri,list_rows=ITEM_LIMIT):

        def gen_page_list(current_page = 1, total_page = 1, list_rows = ITEM_LIMIT):
           if(total_page <= list_rows):
               return range(1, total_page + 1)

           if(current_page + list_rows > total_page):
               return range(total_page - list_rows + 1, list_rows + 1)

           return range(current_page, list_rows + 1)

        def build_uri(uri, param, value):
            regx = re.compile("[\?&](%s=[^\?&]*)" % param)
            find = regx.search(uri)
            split = "&" if re.search(r"\?", uri) else "?"
            if not find: return "%s%s%s=%s" % (uri, split, param, value)
            return re.sub(find.group(1), "%s=%s" % (param, value), uri)

        return self.render_string("pagination.html",page = page, uri = uri, gen_page_list = gen_page_list, list_rows = list_rows,build_uri=build_uri)


handlers = [

]

ui_modules = {
        "pagination":Pagination,
}
