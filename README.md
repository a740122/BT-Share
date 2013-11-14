# funny resource share via BT

It is a funny bt search engine...hmm , not really funny if you cant find what you want XD...

Features(alpha)
--------
- seed search with the dht crawlers and brute force crawlers

tech detail
-----------
- FrontEnd
  - JQ
  - requirejs
  - bootstrap
  - less

- BackEnd
  - tornado
  - mondodb
  - redis
  - ...

TODO
----
* spider routine
  * script
  * take it on linode
  * better
    * scrapy
    * based on gevent
* dht protocol
  * make it work
  * write test
  * write document(wiki)
* distributed spiders
  * make it strong/clear/simple
  * write documents
  * write test
* mem cached
* security check
  * search input (go check wordpress)
  * xss
* manage
  * process monitor(maybe)
  * backend manage(refer the lixian.xunlei UI)
  * warm sys
* full text search(maybe sphinx?)
  * chinese search
  * description search
* community features
  * session support
  * the thrid login
  * comment(anonymous is ok)
  * share(twitter/weibo/google+)
  * IRC chat server demo??
* change linode py to pypy


DEV LOG
--------
* `2013.11.14`
  * tornado async request how-to
  * mongodb async request how-to
* `2013.11.11`
  * reconstruct model layers to hold data within the life of application
  * make a connection pool
  * redesing the seed table
    * page id
    * data transfer
  * add error handling, a weak type
* `2013.11.9-2013.11.10`
  * add model layer
  * fix page error bug
* `2013.11.1`
  * reconstruct the code and remove the gruntJS support to make it easy to build
* `2013.10.31` integrate the [mdht][1]
* `2013.09.08` get time to dev my spider
* `2013.4.17`  make it happen

[1]: https://github.com/zhkzyth/mdht
