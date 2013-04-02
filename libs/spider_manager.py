#coding:utf8
import re
import sys
import os
from datetime import datetime
from threading import Thread
from bs4 import BeautifulSoup
from hashlib import md5
from Queue import Queue

sys.path.insert(0,os.path.join(os.getcwd(), os.pardir))

from crawler.crawler import Crawler
from libs.log_manager import LogManager
from db.database import Database

def mininova_spider(object):
    def callback(webPage):
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
        query = {"id":param['id']}
        database = Database()
        database.saveData(db='bt_tornado', collection='seed', query=query, document=param)

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

    return args


class SpiderManager(object):
    def __init__(self, db_task_manager):
        try:
            self.logger = LogManager(logFile='spider.log', logLevel=5, logTree="Main.spider").logger
        except:
            #todo format the backtrace
            raise Exception, "can not init logger"

        self.spider_configs = [mininova_spider(),]
        self.queue = Queue()
        self.database = Database()
        self.db_task_manager = db_task_manager

    def run(self, args):

        self.logger.info("the spider has been running!")
        #create a global thread num
        # global thread_num = len(spider_configs) + lock
        # or use the queue
        for num in len(spider_configs):
            self.put(num)
        last_insert_id = self.database.get_last_insert()
        try:
            for spider_config in self.spider_configs:
                crawler = Crawler(args, self.queue)
                crawler.start()
            self.queue.join()
            #spiders have been walked,now we turn
            self.grap_seed_file()
        except:
            self.logger.error("spider cannot run.")
        finally:
            pass

    def grap_seed_file(self, last_insert_id):
        #update the task list
        self.db_task_manager.add_seed_task(last_insert_id=last_insert_id)


def main():
    """
       test case for our spider
    """
    spider = SpiderManager()
    spider.run()


if __name__ == "__main__":
    main()
