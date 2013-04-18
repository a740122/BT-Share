#coding:utf8
import re
from datetime import datetime
from threading import Thread
from bs4 import BeautifulSoup
from hashlib import md5
from Queue import Queue

from crawler import Crawler
from database import Database
from logmanager import LogManager


class HTMLParseException(Exception):
    def __init__(self):
        Exception.__init__(self)


def mininova_spider():
    def callback(webPage):
        url, pageSource = webPage.getDatas()
        soup = BeautifulSoup(pageSource)
        #tmp var
        _ = ''
        #more robust
        param = {}
        #get id
        param['id'] = md5(url).hexdigest(),
        #get url
        param['url'] = url,
        #get name
        try:
            _ = soup.find(id="content").h1.string
        except:
            _ = 'unknown'
        finally:
            param['name'] = _
        #get size
        try:
            _ = soup.find(
                id='specifications'
                ).find_all("p")[2].get_text().strip().split('\n')[1].replace(u'\xa0', u' '),
        except:
            _ = 'unknown'
        finally:
            param['size'] = _
        #get description
        try:
            _ = re.compile(r'[\n\r\t]').sub(
                " ",soup.find(id='description').get_text()),
        except:
            _ = 'not description right now~XD'
        finally:
            param['description'] = _
        #get magnet_link
        try:
            _ = soup.find(id="download").find_all("a")[2]['href']
        except:
            #drop it or redo?
            return
        else:
            param['magnet_link'] = _
        query = {"id": param['id']}
        database = Database(db="bt_tornado")
        database.saveData(collection='seed', query=query, document=param)

    #args to init spider
    entryFilter = dict()
    entryFilter['Type'] = 'allow'
    entryFilter['List'] = [r'/tor/\d+', r'/today', r'/yesterday', r'/sub/\d+']

    yieldFilter = dict()
    # yieldFilter['Type'] = 'allow'
    # yieldFilter['List'] = [r'$']
    callbackFilter = dict()
    callbackFilter['List'] = [r'/tor/\d+', ]
    callbackFilter['func'] = callback

    args = dict(
        url=['http://www.mininova.org/today',
             'http://www.mininova.org/yesterday',
             'http://www.mininova.org/sub/35'],
        depth=3,
        threadNum=2,
        keyword='',
        entryFilter=entryFilter,
        yieldFilter=yieldFilter,
        callbackFilter=callbackFilter,
        db='bt_tornado',
        collection='link2search',
    )

    return args


class SpiderManager(object):
    def __init__(self, spiders):
        try:
            self.logger = LogManager(logFile='spider.log', logLevel=5, logTree="spider").logger
        except:
            #todo format the backtrace
            raise Exception, "can not init logger"

        self.queue = Queue()
        self.database = Database(db="bt_tornado")
        self.spiders = spiders

    def run(self):

        self.logger.info("the spider has been running!")
        #create a global thread num
        # global thread_num = len(spider_configs) + lock
        # or use the queue
        for num in range(len(self.spiders)):
            self.queue.put(num)
        # last_insert_id = self.database.get_last_insert_id(collection='seed')
        try:
            for spider in self.spiders:
                crawler = Crawler(spider, self.queue)
                crawler.start()
            self.queue.join()
            self.logger.info("spider tasks done!")
            #spiders have been walked,now we turn
            # self.grap_seed_file()
        except:
            self.logger.error("spider cannot run.")
        finally:
            pass

    def grap_seed_file(self, last_insert_id):
        #update the task list
        grap_seed_set = self.database['seed'].find(
            {"_id": {"$gt": last_insert_id}})
        creator = self.database['user'].find_one({'group': 'admin'})['email']
        self.logger.info("sync seeds with xunlei done!")


def main():
    """
       test case for our spider
    """
    spiders = [mininova_spider(), ]
    crawler = SpiderManager(spiders)
    crawler.run()

if __name__ == "__main__":
    main()
