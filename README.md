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
* redesing the seed table
  * page id
  * data transfer
* dht protocol
* process monitor(maybe)
* full text search(maybe sphinx?)
  * chinese search
  * description search
* distributed spiders
* community features
  * the thrid login
  * comment(anonymous is ok)
  * share(twitter/weibo/google+)
  * IRC chat server demo??
* manage
  * backend manage(refer the lixian.xunlei UI)
  * warm sys

DEV LOG
--------
* add error handling, a weak type 2013.11.11
* add model layer 2013.11.10
* fix page error bug 2013.11.9-2013.11.10
* reconstruct the code and remove the gruntJS support to make it easy to build 2013.11.1
* integrate the [mdht][1] 2013.10.31
* get time to dev my spider 2013.09.08
* make it happen 2013.4.17

[1]: https://github.com/zhkzyth/mdht
