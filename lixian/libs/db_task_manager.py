# -*- encoding: utf-8 -*-
# author: binux<17175297.hk@gmail.com>

import logging
import thread
import random
import socket
import re

from StringIO import StringIO
from threading import Lock
from time import time
from libs.tools import url_unmask
from libs.lixian_api import LiXianAPI, determin_url_type
from libs.cache import mem_cache
from tornado.options import options
from requests import RequestException

from db import database

TASK_ID_SAMPLE_SIZE = 10

ui_re = re.compile(r"ui=\d+")
ti_re = re.compile(r"ti=\d+")
def fix_lixian_url(url):
    url = ui_re.sub("ui=%(uid)d", url)
    url = ti_re.sub("ti=%(tid)d", url)
    return url

lixian_co_re = re.compile(r"&co=\w+")
def fix_lixian_co(url):
    return lixian_co_re.sub("", url)

def catch_connect_error(default_return):
    def warp(func):
        def new_func(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except RequestException, e:
                logging.error(repr(e))
                return default_return
            except socket.timeout, e:
                logging.error(repr(e))
                return default_return
            except AssertionError, e:
                logging.error(repr(e))
                return default_return
        new_func.__name__ = func.__name__
        return new_func
    return warp

class DBTaskManager(object):
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self._last_check_login = 0
        self._last_update_all_task = 0
        self._last_update_downloading_task = 0
        self._last_get_task_list = 0
        #fix for _last_get_task_list
        self.time = time

        self._last_update_task = 0
        self._last_update_task_size = 0
        self._last_update_task_lock = Lock()

        self._xunlei = LiXianAPI()
        verifycode = self._xunlei._get_verifycode(self.username)
        if not verifycode:
            with open('verifycode.jpg', 'w') as verifycode_fp:
                verifycode_fp.write(self._xunlei.verifycode())
            verifycode = raw_input('Please open ./verifycode.jpg and enter the verifycode: ')
        self.islogin = self._xunlei.login(self.username, self.password, verifycode)
        self._last_check_login = time()

    @property
    def xunlei(self):
        if self._last_check_login + options.check_interval < time():
            if not self._xunlei.check_login():
                self._xunlei.logout()
                self.islogin = self._xunlei.login(self.username, self.password)
            self._last_check_login = time()
        return self._xunlei

    @property
    def gdriveid(self):
        return self._xunlei.gdriveid

    @property
    def uid(self):
        return self._xunlei.uid

    def get_vip(self):
        return {"uid": self.uid,
                "gdriveid": self.gdriveid,
                "tid": 1
               }

    # @sqlalchemy_rollback
    def _update_tasks(self, tasks):
        session = Session()
        while tasks:
            nm_list = []
            bt_list = []
            for task in tasks[:100]:
                if task.task_type in ("bt", "magnet"):
                    bt_list.append(task.id)
                else:
                    nm_list.append(task.id)

            for res in self.xunlei.get_task_process(nm_list, bt_list):
                task = self.get_task(res['task_id'])
                if not task: continue
                task.status = res['status']
                task.process = res['process']
                if task.status == "failed":
                    task.invalid = True
                if res['cid'] and res['lixian_url']:
                    task.cid = res['cid']
                    task.lixian_url = res['lixian_url']

                if task.status in ("downloading", "finished"):
                    if not self._update_file_list(task):
                        task.status = "downloading"
                session.add(task)

            tasks = tasks[100:]
        session.commit()
        session.close()

    @sqlalchemy_rollback
    def _update_task_list(self, limit=10, st=0, ignore=False):
        now = self.time()
        with self._last_update_task_lock:
            if now <= self._last_update_task and limit <= self._last_update_task_size:
                return
            self._last_update_task = self.time()
            self._last_update_task_size = limit

            session = Session()
            tasks = self.xunlei.get_task_list(limit, st)
            for task in tasks[::-1]:
                db_task_status = session.query(db.Task.status).filter(
                        db.Task.id == task['task_id']).first()
                if db_task_status and db_task_status[0] == "finished":
                    continue

                db_task = self.get_task(int(task['task_id']))
                changed = False
                if not db_task:
                    changed = True
                    db_task = db.Task()
                    db_task.id = task['task_id']
                    db_task.create_uid = self.uid
                    db_task.cid = task['cid']
                    db_task.url = task['url']
                    db_task.lixian_url = task['lixian_url']
                    db_task.taskname = task['taskname'] or "NULL"
                    db_task.task_type = task['task_type']
                    db_task.status = task['status']
                    db_task.invalid = True
                    db_task.process = task['process']
                    db_task.size = task['size']
                    db_task.format = task['format']
                else:
                    db_task.lixian_url = task['lixian_url']
                    if db_task.status != task['status']:
                        changed = True
                        db_task.status = task['status']
                    if db_task.status == "failed":
                        db_task.invalid = True
                    if db_task.process != task['process']:
                        changed = True
                        db_task.process = task['process']

                session.add(db_task)
                if changed and not self._update_file_list(db_task, session):
                    db_task.status = "failed"
                    db_task.invalid = True
                    session.add(db_task)

            session.commit()
            session.close()

    @sqlalchemy_rollback
    def _update_file_list(self, task, session=None):
        if session is None:
            session = Session()
        if task.task_type == "normal":
            tmp_file = dict(
                    task_id = task.id,
                    cid = task.cid,
                    url = task.url,
                    lixian_url = task.lixian_url,
                    title = task.taskname,
                    status = task.status,
                    dirtitle = task.taskname,
                    process = task.process,
                    size = task.size,
                    format = task.format
                    )
            files = [tmp_file, ]
        elif task.task_type in ("bt", "magnet"):
            try:
                files = self.xunlei.get_bt_list(task.id, task.cid)
            except Exception, e:
                logging.error(repr(e))
                return False

        for file in files:
            db_file = session.query(db.File).get(int(file['task_id']))
            if not db_file:
                db_file = db.File()
                db_file.id = file['task_id']
                db_file.task_id = task.id
                db_file.cid = file['cid']
                db_file.url = file['url']
                db_file._lixian_url = file['lixian_url'] #fix_lixian_url(file['lixian_url'])
                db_file.title = file['title']
                db_file.dirtitle = file['dirtitle']
                db_file.status = file['status']
                db_file.process = file['process']
                db_file.size = file['size']
                db_file.format = file['format']
            else:
                db_file._lixian_url = file['lixian_url'] #fix_lixian_url(file['lixian_url'])
                db_file.status = file['status']
                db_file.process = file['process']

            session.add(db_file)
        return True

    def _restart_all_paused_task(self):
        task_ids = []
        for task in self.xunlei.get_task_list(options.task_list_limit, st=1):
            if task['status'] == "paused":
                task_ids.append(task['task_id'])
        if task_ids:
            self.xunlei.redownload(task_ids)

    def _task_scheduling(self):
        # as we can't get real status of a task when it's status is waiting, stop the task with lowest
        # speed. when all task is stoped, restart them.
        tasks = self.xunlei.get_task_list(options.task_list_limit, 1)
        downloading_tasks = []
        waiting_tasks = []
        paused_tasks = []
        for task in tasks:
            if task['status'] == "downloading":
                downloading_tasks.append(task)
            elif task['status'] == "waiting":
                waiting_tasks.append(task)
            elif task['status'] == "paused":
                paused_tasks.append(task)
        if downloading_tasks:
            self.xunlei.task_pause([x['task_id'] for x in downloading_tasks])
        if not waiting_tasks:
            self.xunlei.redownload([x['task_id'] for x in paused_tasks])

    # @sqlalchemy_rollback
    def get_task(self, task_id):
        return Session().query(db.Task).get(task_id)

    # @sqlalchemy_rollback
    def merge_task(self, task):
        session = Session()
        ret = session.merge(task)
        session.commit()
        session.close()
        return ret

    # @sqlalchemy_rollback
    def get_task_by_cid(self, cid):
        return database['task'].find_one({"cid":cid, "status": {"$ne": "failed"}})
        # return Session().query(db.Task).filter(db.Task.cid == cid).filter(db.Task.status != "failed")

    # @sqlalchemy_rollback
    def get_task_by_title(self, title):
        return database['task'].find_one({"taskname":title})
        # return Session().query(db.Task).filter(db.Task.taskname == title)

    def get_task_by_url(self,url):
        return database['task'].find_one({"url":url})


    # @sqlalchemy_rollback
    def get_task_list(self, start_task_id=0, offset=0, limit=30, q="", t="", a="", order=db.Task.createtime, dis=db.desc, all=False):
        session = Session()
        self._last_get_task_list = self.time()
        # base query
        query = session.query(db.Task)
        # query or tags
        if q:
            query = query.filter(db.or_(db.Task.taskname.like("%%%s%%" % q),
                db.Task.tags.like("%%%s%%" % q)))
        elif t:
            query = query.filter(db.Task.tags.like("%%|%s|%%" % t));
        # author query
        if a:
            query = query.filter(db.Task.creator == a)
        # next page offset
        if start_task_id:
            value = session.query(order).filter(db.Task.id == start_task_id).first()
            if not value:
                return []
            if dis == db.desc:
                query = query.filter(order < value[0])
            else:
                query = query.filter(order > value[0])
        # order or limit
        if not all:
            query = query.filter(db.Task.invalid == False)
        query = query.order_by(dis(order), dis(db.Task.id)).offset(offset).limit(limit)

        result = query.all()
        if result and start_task_id:
            for i, each in enumerate(result):
                if each.id == start_task_id:
                    result = result[i+1:]
                    if not result:
                        return self.get_task_list(start_task_id=start_task_id, offset=offset+i+1, limit=limit, q=q, t=t, a=a, order=order, dis=dis, all=all)
                    else:
                        return result
        session.close()
        return result

    @sqlalchemy_rollback
    def get_file_list(self, task_id, vip_info=None):
        task = self.get_task(task_id)
        if not task: return []

        if vip_info is None:
            vip_info = self.get_vip()

        #fix lixian url
        if not vip_info["tid"]:
            return []
        for file in task.files:
            file.lixian_url = file._lixian_url
            #file.lixian_url = fix_lixian_co(file.lixian_url)
        return task.files

    @mem_cache(2*60*60)
    @sqlalchemy_rollback
    def get_tag_list(self):
        from collections import defaultdict
        tags_count = defaultdict(lambda: defaultdict(int))
        for tags, in Session().query(db.Task.tags).filter(db.Task.invalid == False):
            for tag in tags:
                tags_count[tag.lower()][tag] += 1
        result = dict()
        for key, value in tags_count.iteritems():
            items = value.items()
            key = max(items, key=lambda x: x[1])[0]
            result[key] = sum([x[1] for x in items])
        return sorted(result.iteritems(), key=lambda x: x[1], reverse=True)

    @mem_cache(expire=5*60*60)
    @sqlalchemy_rollback
    def get_task_ids(self):
        result = []
        for taskid, in Session().query(db.Task.id):
            result.append(taskid)
        return result

    @catch_connect_error((-99, "connection error"))
    def add_task(self, url, title=None, tags=set(), creator="", anonymous=False, need_miaoxia=True):
        session = Session()
        def update_task(task, title=title, tags=tags, creator=creator, anonymous=anonymous):
            if not task:
                return task
            if task.invalid and not anonymous:
                new_task = {}
                if title:
                    new_task['title'] = title or "NULL"
                    # task.taskname = title or "NULL"
                if tags:
                    # task.tags = tags
                    new_task['tags'] = tags
                # task.creator = creator
                # task.invalid = False
                new_task['creator'] = creator
                new_task['invalid'] = False
                # # session.add(task)
                # session.commit()
                # _ = task.id
                database['task'].update({"_id":task['_id']}, new_task)
            return task

        def _random():
            return random.randint(100, 999)

        # step 1: determin type
        if isinstance(url, basestring):
            url_unmasked = url_unmask(url)
            if not isinstance(url_unmasked, unicode):
                for each in ("utf8", "gbk", "shift_jis", ):
                    try:
                        url = url_unmasked.decode(each)
                        break
                    except:
                        continue
            # task = session.query(db.Task).filter(db.Task.url == url).first()
            task = database['task'].find_one({"url":url})

            if task:
                return (1, update_task(task))

            url_type = determin_url_type(url)
            if url_type in ("bt", "magnet"):
                check = self.xunlei.bt_task_check
                add_task_with_info = self.xunlei.add_bt_task_with_dict
            elif url_type in ("normal", "ed2k", "thunder"):
                check = self.xunlei.task_check
                add_task_with_info = self.xunlei.add_task_with_dict
            else:
                return (-3, "space error")
        else:
            url_type = "torrent"
            check = self.xunlei.torrent_upload
            add_task_with_info = self.xunlei.add_bt_task_with_dict
            url = (url['filename'], StringIO(url['body']))

        # step 2: get info
        if url_type in ("bt", "torrent", "magnet"):
            if isinstance(url, tuple):
                info = check(*url)
            else:
                info = check(url)
            if not info: return (-1, "check task error")
            if need_miaoxia and not info.get('cid'):
                return (-2, "need miaoxia")
            if need_miaoxia and not self.xunlei.is_miaoxia(info['cid'],
                    [x['index'] for x in info['filelist'] if x['valid']][-20:]):
                return (-2, "need miaoxia")
        else:
            if need_miaoxia and not self.xunlei.is_miaoxia(url):
                return (-2, "need miaoxia")
            info = check(url)
            if not info:
                return (-3, "space error")

        # step 3: check info
        # for bt
        if 'filelist' in info:
            for each in info['filelist']:
                each['valid'] = 1
        # check cid
        if info.get('cid'):
            #TODO
            task = self.get_task_by_cid(info['cid'])
            if task.count() > 0:
                return (1, update_task(task[0]))

        # check title
        if title:
            info['title'] = title
        else:
            title = info.get('title', 'None')
        if not info['cid'] and \
                self.get_task_by_title(info['title']).count() > 0:
            info['title'] = "%s#%s@%s %s" % (options.site_name, _random(), self.time(), info['title'])

        # step 4: commit & fetch result
        result = add_task_with_info(url, info)
        if not result:
            return (0, "error")
        #TODO
        self._update_task_list(5)

        # step 5: checkout task&fix
        task = None
        if info.get('cid') and not task:
            # task = self.get_task_by_cid(info['cid']).first()
            task = self.get_task_by_cid(info['cid'])
        if info.get('title') and not task:
            # task = self.get_task_by_title(info['title']).first()
            task = self.get_task_by_title(info['title'])
        if url and isinstance(url, basestring) and not task:
            # task = session.query(db.Task).filter(db.Task.url == url).first()
            task = self.get_task_by_url(url)
        if not task:
            return (-5, "match task error")

        if task:
            custom_dic = {}
            if title:
                custom_dic['taskname'] = title
                # task.taskname = title
            if tags:
                custom_dic['tags'] = tags
                # task.tags = tags
        #     task.creator = creator
        #     task.invalid = anonymous
            custom_dic['creator'] = creator
            custom_dic['invalid'] = anonymous
            if task.taskname is None:
                task.taskname = "None"
            database.save(task)
        #     if task.taskname is None:
        #         task.taskname = "None"
        #     session.add(task)
        #     session.commit()
        #     _ = task.id
        # session.close()
        return (1, task)

    # @sqlalchemy_rollback
    def update(self):
        if self._last_update_all_task + options.finished_task_check_interval < time():
            self._last_update_all_task = time()
            self._update_task_list(options.task_list_limit)

        if self._last_update_downloading_task + \
                options.downloading_task_check_interval < self._last_get_task_list or \
           self._last_update_downloading_task + \
                options.finished_task_check_interval < time():
            self._last_update_downloading_task = time()
            need_update = Session().query(db.Task).filter(db.or_(db.Task.status == "waiting", db.Task.status == "downloading", db.Task.status == "paused")).all()
                                                  #.order_by(desc(db.Task.id)).limit(100).all()
            if need_update:
                self._update_tasks(need_update)

            self._task_scheduling()

    def async_update(self):
        thread.start_new_thread(DBTaskManager.update, (self, ))
