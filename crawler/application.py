#coding:utf8
from datetime import datetime
from Queue import Queue
import os
import traceback
CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))

from crawler import Crawler
from database import Database
from logmanager import LogManager
import cus_mail
import util


class HTMLParseException(Exception):
    def __init__(self):
        Exception.__init__(self)


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
        for num in range(len(self.spiders)):
            self.queue.put(num)
        try:
            for spider in self.spiders:
                crawler = Crawler(spider, self.queue)
                crawler.start()
            self.queue.join()
        except:
            self.logger.error("spider cannot run.")
        finally:
            seed_num = self.database.db['seed'].count()
            textfile = CURRENT_DIR + '/log/spider.log'
            self.logger.info("now your seeds num is %s." % seed_num)
            try:
                fp = open(textfile, 'rb')
                content = util.tail(fp)
                fp.close()
                sub = 'bt-share-log-%s' % datetime.now()
                cus_mail.send_mail(['zhkzyth@gmail.com',],sub, content)
            except:
                self.logger.error(traceback.format_exc())

def main():
    """
       test case for our spider
    """
    spiders = [mininova_spider(), ]
    crawler = SpiderManager(spiders)
    crawler.run()

if __name__ == "__main__":
    main()
