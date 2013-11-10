#!/usr/bin/env python
# encoding: utf-8
import re

from seed import Seed
from libs.segment import seg_txt_search


#TODO reconstruct
class SearchEngine(object):
    @property
    def seed_dal(self): return Seed()

    def search_seeds(self, q, current_page=1):
        if not q: return None
        if isinstance(q, unicode):
            q = q.encode("utf-8")

        keywords = [seg
                    for seg in seg_txt_search(q)
                    if len(seg) > 1]

        search_text = re.compile("|".join(keywords), re.IGNORECASE)

        params = {"name": {"$regex": search_text}}

        return self.seed_dal.get_seeds(parameters=params, current_page=current_page)

    def search_seeds_count(self, q):
        if not q: return 0
        if isinstance(q, unicode):
            q = q.encode("utf-8")
        keywords = [seg
                    for seg in seg_txt_search(q)
                    if len(seg) > 1]
        params = {"name": {"$all": keywords}}
        return self.seed_dal.get_count(params)
