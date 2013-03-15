#coding:utf8

from downloader import Downloader
from pymongo import Connection
from database import Database

from Queue import Queue, Empty as QueueEmpty

def main():
    #get db
    dbh = Connection(host="localhost", port=27017)


    #DO DOWNLOAD TASK
    download_queue = Queue()

    # create a thread pool and give them a queue
    for i in range(1):
        t = Downloader(download_queue)
        t.setDaemon(True)
        t.start()

    download_urls = dbh['testdemo'].fileUrl.find_one({},{"_id":0})

    for key in download_urls:
        download_queue.put(download_urls[key])

    # wait for the queue to finish
    download_queue.join()

    print "done"


if __name__ == '__main__':
    main()
