#coding:utf8
import sys
import os
import logging

from config import SITE_ROOT


class LogManager(object):
    def __init__(self, logFile="", logLevel=5, logTree=""):
        logFile = SITE_ROOT+"/log/" + logFile
        try:
            self.logger = self._configLogger(
                logFile=logFile, logLevel=logLevel, logTree=logTree)
        except:
            # log init error should raie early
            print sys.exc_info()[0]
            raise

    def _configLogger(self, logFile="", logLevel=5, logTree=""):
        '''配置logging的日志文件以及日志的记录等级'''
        logger = logging.getLogger(logTree)
        LEVELS = {
            1: logging.CRITICAL,
            2: logging.ERROR,
            3: logging.WARNING,
            4: logging.INFO,
            5: logging.DEBUG,  # 数字最大记录最详细
        }
        formatter = logging.Formatter(
            '%(asctime)s %(threadName)s %(levelname)s %(message)s')

        done = False

        while not done:
            try:
                fileHandler = logging.FileHandler(logFile)
            except IOError as e:
                if e.args[0] == 2 and e.filename:
                    # "Most likely the full path to the \
                    # file doesn't exit,so we will create one."
                    fp = e.filename[:e.filename.rfind("/")]

                    if not os.path.exists(fp):
                        os.makedirs(fp)
                else:
                    # "Most likely some other error...\
                    # let's just reraise for now"
                    raise
            else:
                done = True

        fileHandler.setFormatter(formatter)
        logger.addHandler(fileHandler)
        logger.setLevel(LEVELS.get(logLevel))
        return logger

    def __getattr__(self, name):
        return getattr(self.logger, name)
