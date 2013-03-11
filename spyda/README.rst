.. _Python Programming Language: http://www.python.org/
.. _Python Standard Library: http://docs.python.org/library/
.. _restclient: http://pypi.python.org/pypi/restclient
.. _cssselect: http://pypi.python.org/pypi/cssselect
.. _lxml: http://pypi.python.org/pypi/lxml/3.0.2
.. _url: http://pypi.python.org/pypi/url


Overview
--------

spyda is a simple tool and library written in the `Python Programming Language`_ to crawl a given url whilst allowing you to restrict results to a specified
domain and optionally also perform pattern matching against urls crawled. spyda will report on any urls it was unable to crawl along with their status code
and store successfully cralwed links and their content in a directory structure that matches the domain and urls searched.


Requirements
------------

- `restclient`_
- `cssselect`_
- `lxml`_
- `url`_


Supported Platforms
-------------------

- Linux, FreeBSD, Mac OS X
- Python 2.6, 2.7, 3.0

**Windows**: We acknowledge that Windows exists and make reasonable efforts
             to maintain compatibility. Unfortunately we cannot guarantee
             support at this time.
