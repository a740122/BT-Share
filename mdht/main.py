#!/usr/bin/env python
# encoding: utf-8
import random
from logging import DEBUG
from twisted.internet import reactor

from logger import Logger
from mdht import constants
from mdht.mdht_node import MDHT
from config import ROOT_PATH


def main():
    #啟動500個節點監聽請求
    num = 0
    _port = constants.dht_port
    mdhtNodes= []

    Logger.basicConfig(level=DEBUG)
    # Logger.basicConfig(level=DEBUG, filename=ROOT_PATH+"/log/mdht.log")

    # distribute 500 nodes
    while  num<5:
        rand_id = random.getrandbits(160)

        mdhtNodes.append(MDHT(rand_id, bootstrap_addresses=constants.bootstrap_addresses, port=_port))

        num += 1
        _port += 1

    reactor.run()

if __name__ == "__main__":
    main()
