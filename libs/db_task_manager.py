#encoding:utf-8
import logging
import thread
import random
import socket
import re
import pymongo

from StringIO import StringIO
from threading import Lock
from time import time
from libs.tools import url_unmask
from libs.lixian_api import LiXianAPI, determin_url_type
# from libs.cache import mem_cache
from tornado.options import options
from requests import RequestException
from bson.objectid import ObjectId
from db.database import Database

cus_logger = logging.getLogger("Main.db")

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
                cus_logger.error(repr(e))
                return default_return
            except socket.timeout, e:
                cus_logger.error(repr(e))
                return default_return
            except AssertionError, e:
                cus_logger.error(repr(e))
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
        self.database = Database()

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

    def _update_tasks(self, tasks):
        while tasks:
            nm_list = []
            bt_list = []
            for task in tasks[:100]:
                if task['task_type'] in ("bt", "magnet"):
                    bt_list.append(task['id'])
                else:
                    nm_list.append(task['id'])

            for res in self.xunlei.get_task_process(nm_list, bt_list):
                task = self.get_task(res['task_id'])
                if not task: continue
                task['status'] = res['status']
                task['process'] = res['process']
                if task['status'] == "failed":
                    task['invalid'] = True
                if res['cid'] and res['lixian_url']:
                    task['cid'] = res['cid']
                    task['lixian_url'] = res['lixian_url']

                if task['status'] in ("downloading", "finished"):
                    if not self._update_file_list(task):
                        task['status'] = "downloading"
                database['task'].update({'id': task['task_id']},{"$set":task})

            tasks = tasks[100:]

    def _update_task_list(self, limit=10, st=0, ignore=False):
        now = self.time()
        with self._last_update_task_lock:
            if now <= self._last_update_task and limit <= self._last_update_task_size:
                return
            self._last_update_task = self.time()
            self._last_update_task_size = limit

            tasks = self.xunlei.get_task_list(limit, st)
            for task in tasks[::-1]:
                db_task_status = database['task'].find_one({"id": task['task_id']},{"status":1})

                if db_task_status and db_task_status['status'] == "finished":
                    continue
                # update local db
                db_task = self.get_task(int(task['task_id']))
                #not exit before in local store,so create one
                if not db_task:
                    new_task = {
                        'id': task['task_id'],
                        'create_uid': self.uid,
                        'cid': task['cid'],
                        #TODO
                        'createtime':self.time(),
                        'updatetime':self.time(),
                        'creator': "",
                        'tags': "",
                        'url': task['url'],
                        'lixian_url': task['lixian_url'],
                        'taskname': task['taskname'] or "NULL",
                        'task_type': task['task_type'],
                        'status': task['status'],
                        'invalid': False,
                        'process': task['process'],
                        'size': task['size'],
                        'format': task['format'],
                    }
                    if not self._update_file_list(new_task):
                        new_task['status'] = "failed"
                        new_task['invalid'] = True
                    database['task'].save(new_task)
                else:
                    update_task = {}
                    update_task['lixian_url'] = task['lixian_url']
                    update_task['updatetime'] = self.time()
                    if db_task['status'] != task['status']:
                        update_task['status'] = task['status']
                    if db_task['status'] != "failed":
                        update_task['invalid'] = True
                    if db_task['process'] != task['process']:
                        update_task['process'] = task['process']
                    if not self._update_file_list(db_task):
                        update_task['status'] = "failed"
                        update_task['invalid'] = True
                    database['task'].update({'id':task['task_id']}, {"$set": update_task}, safe=True)

    def _update_file_list(self, task):
        if task['task_type'] == "normal":
            tmp_file = dict(
                    task_id = task['id'],
                    cid = task['cid'],
                    url = task['url'],
                    createtime = self.time(),
                    updatetime = self.time(),
                    lixian_url = task['lixian_url'],
                    title = task['taskname'],
                    status = task['status'],
                    dirtitle = task['taskname'],
                    process = task['process'],
                    size = task['size'],
                    format = task['format']
                    )
            files = [tmp_file, ]
        elif task['task_type'] in ("bt", "magnet"):
            try:
                files = self.xunlei.get_bt_list(task['id'], task['cid'])
            except Exception, e:
                cus_logger.error(repr(e))
                return False

        for file in files:
            db_file = database['file'].find_one({'id': file['task_id']})
            if not db_file:
                new_file = {
                    'id': file['task_id'],
                    'task_id': task['id'],
                    'cid': file['cid'],
                    'url': file['url'],
                    'createtime':self.time(),
                    'updatetime':self.time(),
                    '_lixian_url': file['lixian_url'],
                    'title': file['title'],
                    'dirtitle': file['dirtitle'],
                    'status': file['status'],
                    'process': file['process'],
                    'size': file['size'],
                    'format': file['format']
                }
                database['file'].save(new_file)
            else:
                update_file = {
                  '_lixian_url' : file['lixian_url'],
                  'status' : file['status'],
                  'process' : file['process'],
                  'updatetime':self.time()
                }
                database['file'].update({'id':file['task_id']}, {'$set':update_file}, safe=True, multi=True)
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
        return database['task'].find_one({"id": task_id})

    # @sqlalchemy_rollback
    def update_task(self, task_id, param):
        return database['task'].update({"id":int(task_id)},{"$set":param },safe=True)

    # @sqlalchemy_rollback
    def get_task_by_cid(self, cid):
        return database['task'].find_one({"cid":cid, "status": {"$ne": "failed"}})

    # @sqlalchemy_rollback
    def get_task_by_title(self, title):
        return database['task'].find_one({"taskname":title})

    def get_task_by_url(self,url):
        return database['task'].find_one({"url":url})


    # @sqlalchemy_rollback
    def get_task_list(self, offset=0, start_id=0, limit=30, q="", t="", a="", order='createtime', dir=pymongo.DESCENDING, all=False):
        self._last_get_task_list = self.time()
        query_param = {"$and":[]}
        # query or tags
        if q:
            query_param['$and'].append({'$or': [{'taskname':{"$regex":q}},{'tags':{"$regex":q}}]})
        if t:
            query_param['$and'].append({'tags':{"$regex":t}})
        # author query
        if a:
            query_param['$and'].append({'creator': a})

        # next page offset
        if start_id:
            query_param['$and'].append({'_id':{"$lt":ObjectId(start_id)}})

        # order or limit
        if not all:
            query_param['$and'].append({'invalid': False})
        #TODO
        query_param['$and'] = query_param['$and'] or [{}]
        result_iter = database['task'].find(query_param).sort([(order,dir)]).skip(offset).limit(limit)
        result = [value for value in result_iter]

        return result

    # @sqlalchemy_rollback
    def get_file_list(self, task_id, vip_info=None):
        task = self.get_task(task_id)
        if not task: return []

        if vip_info is None:
            vip_info = self.get_vip()
        #fix lixian url
        if not vip_info["tid"]:
            return []
        #TODO rewind?
        result = [x for x in database['file'].find({'task_id':task_id})]

        for file in result:
            file['lixian_url'] = file['_lixian_url']
        return result

    # @mem_cache(2*60*60)
    def get_tag_list(self):
        from collections import defaultdict
        tags_count = defaultdict(lambda: defaultdict(int))
        result_set = database['task'].find({"invalid":{"$ne":False}},{"tags":1})
        for result in result_set:
            for tag in result['tags']:
                tags_count[tag.lower()][tag] += 1
        result = dict()
        for key, value in tags_count.iteritems():
            items = value.items()
            key = max(items, key=lambda x: x[1])[0]
            result[key] = sum([x[1] for x in items])
        return sorted(result.iteritems(), key=lambda x: x[1], reverse=True)

    # @mem_cache(expire=5*60*60)
    # @sqlalchemy_rollback
    def get_task_ids(self):
        result = []
        for task in self.database['task'].find({}):
            result.append(task['id'])
        return result

    @catch_connect_error((-99, "connection error"))
    def add_task(self, url, title=None, tags=[], creator="", anonymous=False, need_miaoxia=True):
        def _update_task(task, title=title, tags=tags, creator=creator, anonymous=anonymous):
            if not task:
                return task
            if task['invalid'] and not anonymous:
                new_task = {}
                if title:
                    new_task['title'] = title or "NULL"
                if tags:
                    new_task['tags'] = tags
                new_task['creator'] = creator
                new_task['invalid'] = False
                database['task'].update({"id":task['task_id']}, {"$set": new_task}, safe=True)
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
            task = database['task'].find_one({"url":url})

            if task:
                return (1, _update_task(task))

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
            task = self.get_task_by_cid(info['cid'])
            if task:
                return (1, _update_task(task))

        # check title
        if title:
            info['title'] = title
        else:
            title = info.get('title', 'None')
        if not info['cid'] and \
                self.get_task_by_title(info['title']):
            info['title'] = "%s#%s@%s %s" % (options.site_name, _random(), self.time(), info['title'])

        # step 4: commit & fetch result
        result = add_task_with_info(url, info)
        if not result:
            return (0, "error")
        #update local db
        self._update_task_list(5)

        # step 5: checkout task&fix
        task = None
        if info.get('cid') and not task:
            task = self.get_task_by_cid(info['cid'])
        if info.get('title') and not task:
            task = self.get_task_by_title(info['title'])
        if url and isinstance(url, basestring) and not task:
            task = self.get_task_by_url(url)
        if not task:
            return (-5, "match task error")

        if task:
            custom_dic = {}
            if title:
                custom_dic['taskname'] = title
            if tags:
                custom_dic['tags'] = tags
            custom_dic['creator'] = creator
            custom_dic['invalid'] = anonymous
            if task['taskname'] is None:
                custom_dic['taskname'] = "None"
            database['task'].update({"id":task["id"]},{"$set":custom_dic},safe=True)
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
            need_update = database['task'].find({'$or': [{'status':'waiting'},{'status':'downloadig'},{'status':'paused'}]})
            if need_update:
                # tmp hack!
                tasks = []
                for value in need_update:
                    tasks.append(value)
                self._update_tasks(tasks)

            self._task_scheduling()

    def async_update(self):
        thread.start_new_thread(DBTaskManager.update, (self, ))
