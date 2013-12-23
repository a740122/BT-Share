#!/usr/bin/env python
# encoding: utf-8
"""
A single funcs to download and parse bt files.

TODO use gevent to make it faster.
TODO use a middle ware to make it stronger.
"""
import os
import hashlib
import requests
import socket
from requests.exceptions import RequestException,Timeout
from pymongo import Connection

from config import MONGO,UPDATE_NUM,REQUEST_TIMEOUT
from torrentparser import TorrentParser,ParsingError
from log_manager import LogManager

# TOOD single file
mongo = Connection(host=MONGO['host'], port=MONGO['port'])
db = mongo[MONGO['db']]

logger = LogManager("application.log")

# TODO implement it in C
tp = TorrentParser.get_instance()

#parse torrent file
def parse_torrent_file(file):
    try:
        tp.parse_torrent(file)
        return {
            "name": tp.get_torrent_name(),
            "file_list": tp.get_files_details(),
            "creation_date": tp.get_creation_date(),
            "tracker_url": tp.get_tracker_url(),
            "client_name": tp.get_client_name(),
            # TODO how to get torrent description?
            "description": None,
            "parse_result":'ok'
        }
    except ParsingError:
        logger.error("torrent file(%s) seems broken." % file)
    except:
        logger.exception("unexpected error raised.")

    return {"parse_result": 'bad'}

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

def check_path(path):
    """
    check torrent path ,if not exit,just make a one
    """
    if not os.path.exists(os.path.abspath('%s/%s'%('torrents', path))):
        os.mkdir(os.path.abspath('%s/%s'%('torrents', path)))

# TODO make it as a middle layer
def get_server_list(info_hash):
    """
    we try serveral place to get torrents
    """
    upper_hash  = info_hash.upper()
    urls = []
    urls.append('http://torrage.com/torrent/%s.torrent'%upper_hash)
    urls.append('http://torcache.net/torrent/%s.torrent'%upper_hash)
    urls.append(format_btbox_url(upper_hash))
    urls.append('https://zoink.it/torrent/%s.torrent'%upper_hash)
    return urls

def format_btbox_url(upper_hash):
    """
    btbox request such a url to get a torrent
    """
    header = upper_hash[0:2]
    tail   = upper_hash[-2:]
    return "http://bt.box.n0808.com/" + header + "/" + tail + "/" + upper_hash + ".torrent"

def format_magnet_link(maghash, tracker_url):
    """
    Return the magnet url of torrent file
    """
    magnet = "magnet:?xt=urn:btih:%s" % maghash
    if tracker_url:
        magnet += "&tr=%s" % tracker_url
    return magnet

def get_file(info_hash):
    """
    Use requests lib to download files.
    TODO make it faster and safer.
    """
    # whether we have got the torrent
    done = False

    _info_hash = hex(long(info_hash))[2:].rstrip("L")

    fetch_list = get_server_list(_info_hash)

    db.sources.update({'_id':info_hash}, {'$set':{'download':1}})

    for _url in fetch_list:

        if done == True:
            break

        try:

            result = requests.get(_url, timeout=REQUEST_TIMEOUT)

            if result.status_code == 200:

                _path = save_file_to_disk(result.content, info_hash)
                _abspath = os.path.abspath('%s/%s'%('torrents', _path.get('path')))
                abspath = "%s/%s" % (_abspath, _path.get('file_name'))

                result = parse_torrent_file(abspath)

                if result['parse_result'] == 'ok':
                    done = True

                    magnet_link = format_magnet_link(_info_hash, result['tracker_url'])

                    db.source_info.update({'_id':_info_hash}, {'$set':{'download':1,
                                                                       'name': result['name'],
                                                                       'description': result['description'],
                                                                       'magnet_link': magnet_link,
                                                                       'file_path':'%s/%s/%s'%('torrents',_path.get('path'), _path.get('file_name')),
                                                                       'file_list': result['file_list'],
                                                                       'creation_date': result['creation_date'],
                                                                       'tracker_url': result['tracker_url'],
                                                                       'client_name': result['client_name']
                                                                       }},
                                          upsert=True)
        #BUG: https://github.com/kennethreitz/requests/issues/1787
        except (Timeout,socket.timeout):
            # info_hash exist?
           logger.warning("request torrent %s timeout." % info_hash)
        except RequestException, e:
            # may get blocked ?
            logger.warning("request torrent %s raise exception.And reason is %s." % (info_hash, e.strerror))
        except:
            logger.exception("opps.Some unexpected exceptions just happend.")

    # TODO  may redownload again
    if done != True:
        db.sources.update({'_id':info_hash}, {'$set':{"state":'bad'}})
        logger.warning("request torrent %s fail." % info_hash)

def down_bt():
    """
    TODO find a algorithm to judge a update time
    """
    for item in db.sources.find({"download": {"$exists": False}}, fields={'_id':True}, limit=UPDATE_NUM):
        get_file(item.get('_id'))

if __name__ == "__main__":
    # write a crontab to run every x hours
    down_bt()
