#coding:utf8
import logging
import time
import re

import sys
import os
sys.path.insert(0,os.path.join(os.getcwd(), os.pardir))

from datetime import datetime
from threading import Thread

from crawler.crawler import Crawler
from crawler.database import Database

from bs4 import BeautifulSoup
from hashlib import md5

from libs.log_manager import LogManager

class SpiderManager(object):
    def __init__(self,args={}):
        try:
            self.logger = LogManager(logFile='spider.log', logLevel=5, logTree="Main.spider").logger
        except:
            #todo format the backtrace
            raise Exception, "can not init logger"

    def run(self,args={}):

        self.logger.info("the spider has been running!")

        def callback(webPage):
            self.logger.info("going to insert or update our local")

            url, pageSource = webPage.getDatas()
            soup = BeautifulSoup(pageSource)
            param = {
                'id': md5(url).hexdigest() or "",
                'url': url or "",
                'name': soup.find(id="content").h1.string or "unknown",
                'size': soup.find(
                    id='specifications'
                ).find_all(
                    "p"
                )[2].get_text().strip().split('\n')[1].replace(u'\xa0', u' '),
                'description': re.compile(r'[\n\r\t]').sub(
                    " ", soup.find(id='description').get_text()),
                'magnet_link': soup.find(id='download').find_all("a")[2]['href'],
            }
            database = Database()
            database.saveData(db='bt_tornado', collection='seed', document=param)

        #args to init spider
        entryFilter = dict()
        entryFilter['Type'] = 'allow'
        entryFilter['List'] = [r'/tor/\d+', r'/today']

        yieldFilter = dict()
        # yieldFilter['Type'] = 'allow'
        # yieldFilter['List'] = [r'$']
        callbackFilter = dict()
        callbackFilter['List'] = [r'/tor/\d+', ]
        callbackFilter['func'] = callback

        args = dict(
            url=['http://www.mininova.org/today', ],
            depth=3,
            threadNum=1,
            keyword='',
            entryFilter=entryFilter,
            yieldFilter=yieldFilter,
            callbackFilter=callbackFilter,
            db='bt_tornado',
            collection='link2search',
        )
        try:
           crawler = Crawler(args)
           crawler.start()
        except:
            logger = logging.getLogger("Main.spider")
            logger.error("spider cannot run.")
        finally:
            pass


def main():
    """
       test case for our spider
    """
    spider = SpiderManager()
    spider.run()


if __name__ == "__main__":
    main()
