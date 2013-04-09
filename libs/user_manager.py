#encoding:utf8
from bson.objectid import ObjectId


class UserManager(object):
    def __init__(self, database):
        #TODO should build a connection pool
        self.database = database['user']

    def get_user_by_id(self, _id):
        return self.database.find_one({'_id':ObjectId(_id)})

    def get_user_email_by_id(self, _id):
        if not _id:
            return "zhkzyth@localhost"
        return self.database.find_one({'id':ObjectId(_id)},{'email': 1})

    def get_user(self, email):
        if not email: return None
        return self.database.find_one({'email': email})

    def update_user(self, email, name):
        self.reset_add_task_limit(email)
        user = self.get_user(email) or {}
        if not user:
            user['email'] = email
            user['name'] = name
            self.database.save(user)

    # @mem_cache(expire=60*60)
    def get_id(self, email):
        if email == "bot@localhost":
            return 0
        user = self.get_user(email)
        if user:
            return user['_id']
        return None

    # @mem_cache(expire=60*60)
    def get_name(self, email):
        if email == "bot@localhost":
            return "bot"
        user = self.get_user(email)
        if user:
            return user['name']
        return None
