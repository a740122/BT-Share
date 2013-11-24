#!/usr/bin/env python
# encoding: utf-8
import re
import tornado

from libs.segment import seg_txt_search
from libs.util import singleton

@singleton
class SearchEngine(object):

    def __init__(self, loaded_model):
        self.loaded_model = loaded_model

    @tornado.gen.coroutine
    def search_seeds(self, q, current_page=1):
        if not q: raise tornado.gen.Return(None)
        if isinstance(q, unicode):
            q = q.encode("utf-8")

        keywords = [seg
                    for seg in seg_txt_search(q)
                    if len(seg) > 1]

        search_text = re.compile("|".join(keywords), re.IGNORECASE)

        params = {"name": {"$regex": search_text}}

        result = yield self.loaded_model["seed"].get_seeds(parameters=params, current_page=current_page)
        raise tornado.gen.Return(result)

    @tornado.gen.coroutine
    def search_seeds_count(self, q):
        if not q: raise tornado.gen.Return(None)
        if isinstance(q, unicode):
            q = q.encode("utf-8")
        keywords = [seg
                    for seg in seg_txt_search(q)
                    if len(seg) > 1]
        params = {"name": {"$all": keywords}}

        result = yield self.loaded_model["seed"].get_count(params)
        raise tornado.gen.Return(result)
