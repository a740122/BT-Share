#!/usr/bin/env python
# encoding: utf-8
"""
testsoup.py

Created by <zhkzyth@gmail.com> on Mar 30, 2013
"""
html_doc = """
<html><head><title>The Dormouse's story</title></head>

<div id="test">
<p class="title"><b>The Dormouse's story</b></p>

<p class="story">Once upon a time there were three little sisters; and their names were
<a href="http://example.com/elsie" class="sister" id="link1">Elsie</a>,
<a href="http://example.com/lacie" class="sister" id="link2">Lacie</a> and
<a href="http://example.com/tillie" class="sister" id="link3">Tillie</a>;
and they lived at the bottom of a well.</p>

<p class="story">...</p>
</div>
"""

test_doc ="""<div id="download">


<a href="/get/13209521" title="Download &quot;[AUDCST067] K.Larm  J.Raninen - Free Bits EP techno acid MP3 320kbps.torrent&quot;" onclick="pageTracker._trackPageview('/get/id')"><img src="http://mnstat.com/images/download.png" class="usage-icon" alt="Download!" /></a>

<h2><a href="/get/13209521" title="Download &quot;[AUDCST067] K.Larm  J.Raninen - Free Bits EP techno acid MP3 320kbps.torrent&quot;" onclick="pageTracker._trackPageview('/get/id')">Download this torrent!</a></h2>&nbsp;or use the <a href="magnet:?xt=urn:btih:MFFUFIZRXGWJVAS4SCJNTG66FPB3XIZT&amp;tr=http://tracker.mininova.org/announce" title="Magnet link to &quot;[AUDCST067] K.Larm & J.Raninen - Free Bits EP (techno, acid, MP3,
320kbps)&quot;" onclick="pageTracker._trackPageview('/magnet/id')">magnet link</a>
<br />

<p id="seedsleechers"><span class="g">2</span> seeds, <span class="b">0</span> leechers</p>



<div class="clear-left"></div>
</div>
"""

a_doc = """

<div id="specifications">
<p>
<strong>Sponsored:</strong>
<a href="http://www.filecrest.com" target="_blank">Download Free Software</a>
</p>

<p>
<strong>Category:</strong>
<a href="/cat/5">Music</a> &gt; <a href="/sub/161">Techno</a>
</p>

<p>
<strong>Total size:</strong>
33.72&nbsp;megabyte</p>

<p>
<strong>Added:</strong>
23 hours ago by <a class="user" href="/user/sonicadam123">sonicadam123</a></p>


<p>
<strong>Share ratio:</strong>
<span id="shareratio"><img src="http://mnstat.com/images/sr10.gif" alt="Perfect" title="Perfect" /><span class="g">2</span> seeds, <span class="b">0</span> leechers</span>
</p>

<p>
<strong>Last updated:</strong>
<span id="lastupdated">59 minutes ago</span>
</p>

<p>
<strong>Downloads:</strong>
551</p>

</div><!-- #specifications-->

"""

from bs4 import BeautifulSoup
soup = BeautifulSoup(a_doc)
import pdb
pdb.set_trace()
