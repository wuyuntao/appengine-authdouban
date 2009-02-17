# -*- coding: UTF-8 -*-

from google.appengine.ext import db
import settings

class DoubanAccount(db.Model):
    """
    豆瓣授权帐户
    包括请求授权的 request key，未授权和已授权的 access key，
    以及已授权后的用户 ID

    """
    user = db.UserProperty(auto_current_user_add=True)
    request_key = db.StringProperty()
    request_secret = db.StringProperty()
    access_key = db.StringProperty()
    access_secret = db.StringProperty()
    douban_id = db.StringProperty()
    created = db.DateTimeProperty(auto_now_add=True)

    @classmethod
    def get_authenticated_accounts(cls, user):
        """
        显示最近创建的已授权的帐户

        """
        query = cls.all() \
                   .filter('user = ', user) \
                   .filter('request_key = ', 'ALREADY_AUTHENTICATED') \
                   .order('-created') \
                   .fetch(settings.MAX_STORED_ACCOUNTS)
        return query

    def set_request_key(self, key, secret):
        """ 保存 request key """
        self.request_key = key
        self.request_secret = secret
        self.put()

    def set_access_key(self, key, secret, douban_id):
        """
        保存已授权的 access key
        
        """
        self.access_key = key
        self.access_secret = secret
        self.douban_id = douban_id
        self.request_key = 'ALREADY_AUTHENTICATED'
        self.request_secret = 'ALREADY_AUTHENTICATED'
        self.put()
