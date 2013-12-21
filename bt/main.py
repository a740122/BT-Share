#!/usr/bin/env python
# encoding: utf-8
# -*- coding:utf-8 -*-
import os
import hashlib
import sys
import requests
from requests.exceptions import RequestException,Timeout
from pymongo import Connection

from config import MONGO,UPDATE_NUM,REQUEST_TIMEOUT
from torrentparser import TorrentParser,ParsingError
from log_manager import LogManager

# TOOD single file
mongo = Connection(host=MONGO['host'], port=MONGO['port'])
db = mongo[MONGO['db']]

# TODO
logger = LogManager("application.log")

#parse torrent file
def parse_torrent_file(file):
    try:
        tp = TorrentParser(file)
        return {

            "file_name_list": tp.get_files_details(),
            "creation_date": tp.get_creation_date(),
            "tracker_url": tp.get_tracker_url(),
            "client_name": tp.get_client_name(),
            "parse_result":'ok'
        }
    except ParsingError:
        logger.error("torrent file(%s) seems broken." % file)
    except:
        logger.error(sys.exc_info()[0])

    return {"parse_result": 'imcomplete'}

def save_file_to_disk(content, info_hash):
    """
    save torrent seed to disk
    """
    _temp = file_path(info_hash)
    _path = os.path.abspath('%s/%s'%('torrents', _temp['path']))
    _file_name = _temp['file_name']
    open('%s/%s'%(_path, _file_name), 'wb').write(content)
    return _temp

# calculate the torrent saving path
def file_path(info_hash):
    _md5 = hashlib.md5(info_hash).hexdigest()
    check_path(_md5[0:2])
    check_path('%s/%s/'%(_md5[0:2], _md5[2:5]))
    return {'path':'%s/%s/'%(_md5[0:2], _md5[2:5]), 'file_name':'%s.torrent'%_md5}

#
def check_path(path):
    if not os.path.exists(os.path.abspath('%s/%s'%('torrents', path))):
        os.mkdir(os.path.abspath('%s/%s'%('torrents', path)))

def get_server_list(info_hash):
    upper_hash  = info_hash.upper()
    _url = 'http://torrage.com/torrent/%s.torrent'%upper_hash

    return [_url]

def get_file(info_hash):
    """
    Use requests lib to download files.
    TODO make it faster and safer.
    """
    # whether we have got the torrent
    done = False
    _info_hash = hex(long(info_hash))[2:].rstrip("L")

    fetch_list = get_server_list(_info_hash)

    for _url in fetch_list:
        if done == False:
            try:

                #TODO timeout should be controlled by config
                _content = requests.get(_url, timeout=REQUEST_TIMEOUT).content

                if 'File not found' not in _content:
                    done = True

                    _path = save_file_to_disk(_content, info_hash)
                    _abspath = os.path.abspath('%s/%s'%('torrents', _path.get('path')))
                    abspath = "%s/%s" % (_abspath, _path.get('file_name'))

                    result = parse_torrent_file(abspath)

                    if result['pares_result'] == 'ok':
                        db.temp.update({'_id':info_hash}, {'$set':{'download':1,
                                                                   'file_path':'%s/%s/%s'%('torrents',_path.get('path'), _path.get('file_name')),
                                                                   'state': 'ok',
                                                                   'file_names': result['file_name_list'],
                                                                   'creation_date': result['creation_date'],
                                                                   'tracker_url': result['tracker_url'],
                                                                   'client_name': result['client_name']
                                                                   }},
                                       upsert=True)
                    else:
                        # the torrent file was not parsed correctly.
                        # for now, just mark its status
                        # TODO handle the bad situation
                        db.source.update({'_id':info_hash}, {'$set':{'download':1,
                                                                   'file_path':'%s/%s/%s'%('torrents',_path.get('path'), _path.get('file_name')),
                                                                   'state': result['state'],
                                                                   }})
            except Timeout:
                # info_hash exist?
               logger.warning("request torrent %s timeout.should try again in the next run.")
            except RequestException, e:
                # may get blocked ?
               logger.warning("request torrent %s raise exception.And reason is " % e.args[1])
            except:
                db.source.update({'_id':info_hash}, {'$set':{'download':1,
                                                             'file_path':'%s/%s/%s'%('torrents',_path.get('path'), _path.get('file_name')),
                                                             'state': 'bad',
                                                            }})
                logger.error(sys.exc_info()[0])

def down_bt():
    """
    TODO find a algorithm to judge a update time
    """
    for item in db.sources.find({"download": {"$exists": False}}, fields={'_id':True}, limit=UPDATE_NUM):
        get_file(item.get('_id'))

if __name__ == "__main__":
    # I write a crontab to run every 6 hours
    down_bt()
