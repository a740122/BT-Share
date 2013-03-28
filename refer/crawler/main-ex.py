#coding:utf8

import logging
import time
from datetime import datetime
from threading import Thread

from crawler import Crawler
from database import Database

def congifLogger(logFile, logLevel):
    '''配置logging的日志文件以及日志的记录等级'''
    logger = logging.getLogger('Main')
    LEVELS={
        1:logging.CRITICAL,
        2:logging.ERROR,
        3:logging.WARNING,
        4:logging.INFO,
        5:logging.DEBUG,#数字最大记录最详细
        }
    formatter = logging.Formatter(
        '%(asctime)s %(threadName)s %(levelname)s %(message)s')
    try:
        fileHandler = logging.FileHandler(logFile)
    except IOError, e:
        return False
    else:
        fileHandler.setFormatter(formatter)
        logger.addHandler(fileHandler)
        logger.setLevel(LEVELS.get(logLevel))
        return True


class PrintProgress(Thread):
    '''每隔10秒在屏幕上打印爬虫进度信息'''

    def __init__(self, crawler):
        Thread.__init__(self)
        self.name = 'PrintProgress'
        self.beginTime = datetime.now()
        self.crawler = crawler
        self.daemon = True

    def run(self):
        while 1:
            if self.crawler.isCrawling:
                print '-------------------------------------------'
                print 'Crawling in depth %d' % self.crawler.currentDepth
                print 'Already visited %d Links' % self.crawler.getAlreadyVisitedNum()
                print '%d tasks remaining in thread pool.' % self.crawler.threadPool.getTaskLeft()
                print '-------------------------------------------\n'
                time.sleep(10)

    def printSpendingTime(self):
        self.endTime = datetime.now()
        print 'Begins at :%s' % self.beginTime
        print 'Ends at   :%s' % self.endTime
        print 'Spend time: %s \n'%(self.endTime - self.beginTime)
        print 'Finish!'


def main():
    # args = parser.parse_args()

    # init.
    yieldFilter = dict()
    yieldFilter['Type'] = 'allow'
    yieldFilter['List'] = [r'.*/data/music/.*']

    dbh = Database()
    urls = set()

    for dataset in dbh.getAllData(db='testdemo',collection='seed'):
        urls.add(dataset['url'])

    urls = ['http://music.baidu.com/song/7333126/download']

    args = dict(
        url = urls,
        depth = 2,
        logFile = 'spider.log',
        db = 'testdemo',
        collection = 'fileUrl',
        logLevel = 3,
        threadNum = 1,
        keyword = '',
        testSelf = False,
        entryFilter = [],
        yieldFilter = yieldFilter,
    )


    if not congifLogger(args['logFile'], args['logLevel']):
        print '\nPermission denied: %s' % args['logFile']
        print 'Please make sure you have the permission to save the log file!\n'
    elif args['testSelf']:
        Crawler(args).selfTesting(args)
    else:
        crawler = Crawler(args)
        printProgress = PrintProgress(crawler)
        printProgress.start()
        crawler.start()
        printProgress.printSpendingTime()

if __name__ == '__main__':
    main()
