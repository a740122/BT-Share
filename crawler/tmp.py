import urllib2
import os

def download_file(url):
    """"""
    headers = {
            'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Charset' : 'gb18030,utf-8;q=0.7,*;q=0.3',
            'Accept-Encoding' : 'gzip,deflate,sdch',
            'Accept-Language' : 'en-US,en;q=0.8',
            'Connection': 'keep-alive',
            'User-Agent': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; Trident/5.0)',
            'Referer' : url,
    }

    req = urllib2.Request(url, None, headers)
    resp = urllib2.urlopen(req)

    fname = os.path.basename(url)
    with open(fname, "wb") as f:
        while True:
            chunk = resp.read(1024)
            if not chunk: break
            f.write(chunk)

download_file("http://music.baidu.com/data/music/file?link=http://zhangmenshiting.baidu.com/data2/music/35418589/35324561234000128.mp3?xcode=186a237150f18354586ffe4ed485dcd5")
