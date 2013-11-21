import random
from logging import DEBUG
from twisted.internet import reactor

from database import MongoDb
from logger import logger
from mdht import constants
from mdht.mdht_node import MDHT
from config import ROOT_PATH


def main():
    #啟動500個節點監聽請求
    num = 0
    _port = constants.dht_port
    mdhtNodes= []

    db = MongoDb()
    logger.basicConfig(level=DEBUG)
    # _logger = logger.basicConfig(level=DEBUG, filename=ROOT_PATH+"/log/mdht.log")

    # distribute 500 nodes
    while  num<5:
        rand_id = random.getrandbits(160)

        #TODO change to factory and add logger/db support
        mdhtNodes.append(MDHT(rand_id, bootstrap_addresses=constants.bootstrap_addresses, port=_port, db=db))

        num += 1
        _port += 1

    reactor.run()

if __name__ == "main":
    main()
