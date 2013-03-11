# Package:  spyda
# Date:     18th December 2012
# Author:   James Mills, j dot mills at griffith dot edu dot au

"""Spyda - Python Spider Tool and Library

spyda is a simple tool and library written in the `Python Programming Language`_ to crawl a given url whilst allowing you to restrict results to a specified
domain and optionally also perform pattern matching against urls crawled. spyda will report on any urls it was unable to crawl along with their status code
and store successfully cralwed links and their content in a directory structure that matches the domain and urls searched.

:copyright: CopyRight (C) 2012 by James Mills

.. _Python Programming Language: http://www.python.org/
"""

__author__ = "James Mills, j dot mills at griffith dot edu dot au"
__date__ = "9th January 2013"
__version__ = "0.0.2dev"


import sys
from collections import deque
from traceback import format_exc
from re import escape as escape_regex
from re import compile as compile_regex

from restclient import GET
from url import parse as parse_url
from nltk import clean_html as html_to_text
from lxml.html import tostring as doc_to_str
from lxml.html.soupparser import fromstring as html_to_doc

from lxml.html import HtmlElement
empty_doc = HtmlElement()
del HtmlElement

from .utils import is_url, unichar_to_text, unescape

HEADERS = {
    "User-Agent": "{0} v{1}".format(__name__, __version__)
}


def fetch_url(url):
    response, content = GET(url, headers=HEADERS, resp=True)
    if "content-type" in response and "charset=" in response["content-type"]:
        charset = response["content-type"].split("charset=")[1]
    else:
        charset = None

    return response, (content.decode(charset) if charset is not None else content)


def log(msg, *args, **kwargs):
    sys.stderr.write("{0:s}{1:s}".format(msg.format(*args), kwargs.get("n", "\n")))
    sys.stderr.flush()


def error(e):  # pragma: no cover
    log("ERROR: {0:s}", e)
    log(format_exc())


def status(msg, *args):
    log("\r\x1b[K{0:s}", msg.format(*args), n="")


def parse_html(html):
    return html_to_doc(html)


def doc_to_text(doc):
    return unichar_to_text(html_to_text(unescape(doc_to_str(doc))))


def get_links(html, badchars="\"' \v\f\t\n\r"):
    tags = parse_html(html).cssselect("a")
    hrefs = (tag.get("href") for tag in tags)
    return (href.strip(badchars) for href in hrefs if href is not None)


def crawl(root_url, allowed_urls=None, max_depth=0, patterns=None, verbose=False):
    """Crawl a given url recursively for urls.

    :param root_url: Root URL to start crawling from.
    :type  root_url: str

    :param allowed_urls: A list of allowed urls (matched by regex) to traverse.
                         By default a regex is compiled for the ``root_url`` and used.
    :type  allowed_urls: list or None

    :param max_depth: Maximum depth to follow, 0 for unlimited depth.
    :param max_depth: int

    :param patterns: A list of regex patterns to match urls against. If evaluates to ``False``, matches all urls.
    :type  patterns: list or None or False

    :param verbose: If ``True`` will print verbose logging
    :param verbose: bool

    :returns: A dict in the form {"error": set(...), "urls": set(...)}
              The errors set contains 2-item tuples of (status, url)
              The urls set contains 2-item tuples of (rel_url, abs_url)
    :rtype: dict

    In verbose mode the following single-character letters are used to denonate meaning for URLs being processed:
     - (I) (I)nvalid URL
     - (F) (F)ound a valid URL
     - (S) (S)een this URL before
     - (E) (E)rror fetching URL
     - (V) URL already (V)isitied
     - (O) URL (O)utside allowed domains

    Also in verbose mode each followed URL is printed in the form:
    <status> <reason> <type> <length> <link> <url>
    """

    patterns = [compile_regex(regex) for regex in patterns] if patterns else []
    root_url = parse_url(root_url)
    queue = deque([root_url])
    visited = []
    errors = []
    urls = []
    n = 0
    l = 0

    if not allowed_urls:
        allowed_urls = ["^{0:s}.*(?is)".format(escape_regex(root_url.utf8()))]

    allowed_urls = [compile_regex(regex) for regex in allowed_urls]

    while queue:
        try:
            if max_depth and n >= max_depth:
                break

            n += 1
            current_url = queue.popleft()
            _current_url = current_url.utf8()
            visited.append(_current_url)

            response, content = fetch_url(_current_url)

            if not response.status == 200:
                errors.append((response.status, _current_url))
                links = []
            else:
                links = list(get_links(content))

            verbose and log(
                " {0:d} {1:s} {2:s} {3:s} {4:d} {5:s}",
                response.status, response.reason,
                response["content-type"], response.get("content-length", ""),
                len(links), current_url.utf8()
            )

            for link in links:
                url = current_url.relative(link).defrag().canonical()
                _url = url.utf8()

                if _url in urls:
                    verbose and log("  (S): {0}", _url)
                    continue

                if url._scheme not in ("http", "https"):
                    verbose and log("  (I): {0}", _url)
                    continue

                if _url in visited:
                    verbose and log("  (V): {0}", _url)
                    continue

                if allowed_urls and not any((regex.match(_url) is not None) for regex in allowed_urls):
                    visited.append(_url)
                    verbose and log("  (O): {0}", _url)
                    continue

                queue.append(url)

                if patterns and not any((regex.match(_url) is not None) for regex in patterns):
                    verbose and log("  (P): {0}", _url)
                else:
                    verbose and log("  (F): {0}", _url)
                    urls.append(_url)
                    l += 1
            not verbose and status("Q: {0:d} F: {1:d} V: {2:d} L: {3:d}", len(queue), n, len(visited), l)
        except Exception as e:  # pragma: no cover
            error(e)
        except KeyboardInterrupt:  # pragma: no cover
            break

    return {
        "urls": urls,
        "errors": errors
    }


def extract(source, filters=None):
    filters = dict(filter.split("=") for filter in filters)
    content = fetch_url(source)[1] if is_url(source) else open(source, "r").read()
    result = {}
    for k, filter in filters.items():
        doc = parse_html(content)
        doc = (doc.cssselect(filter) or [empty_doc])[0]
        text = doc_to_text(doc)
        result[k] = text
    return result

    #return dict((k, unichar_to_text(unescape(doc_to_text((parse_html(content).cssselect(v) or [empty_doc])[0])))) for k, v in filters.items())


__all__ = ("crawl", "fetch_url", "get_links",)
