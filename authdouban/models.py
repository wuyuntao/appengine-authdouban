# -*- coding: UTF-8 -*-

from datetime import datetime, timedelta
from google.appengine.ext import db
import settings
from utils import douban_service, parse_urls, parse_id, force_unicode as u

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
    def create_unauthorized_account(cls, user, key=None, secret=None):
        new_account = cls(user=user)
        new_account.put()
        if key and secret:
            new_account.set_request_key(key, secret)
        return new_account

    @classmethod
    def get_authenticated_accounts(cls, user, douban_id=None):
        """ 显示最近创建的已授权的帐户 """
        query = cls.all() \
                   .filter('user = ', user) \
                   .filter('request_key = ', 'ALREADY_AUTHENTICATED') \
                   .order('-created')
        if douban_id is None:
            return query.fetch(settings.MAX_STORED_ACCOUNTS)
        else:
            return query.filter('douban_id = ', douban_id).get()

    def get_douban_profile(self):
        """ 获取相应的豆瓣用户档案 """
        return DoubanProfile.get_by_douban_id(self.douban_id)
    douban_profile = property(get_douban_profile)

    def set_request_key(self, key, secret):
        """ 保存 request key """
        self.request_key = key
        self.request_secret = secret
        self.put()

    def set_access_key(self, key, secret, douban_id):
        """ 保存已授权的 access key """
        self.access_key = key
        self.access_secret = secret
        self.douban_id = douban_id
        self.request_key = 'ALREADY_AUTHENTICATED'
        self.request_secret = 'ALREADY_AUTHENTICATED'
        self.put()

    def remove_duplicate_accounts(self):
        """ 删除 ID 重复的授权帐户 """
        accounts = self.all() \
                       .filter('user = ', self.user) \
                       .filter('request_key = ', 'ALREADY_AUTHENTICATED') \
                       .filter('__key__ != ', self.key()) \
                       .filter('douban_id = ', self.douban_id) \
                       .fetch(1000)
        for account in accounts:
            account.delete()

    def remove_old_accounts(self):
        """ 删除超过保存限制的最早的授权帐户 """
        if settings.MAX_STORED_ACCOUNTS > 0:
            accounts = self.all() \
                           .filter('user = ', self.user) \
                           .filter('request_key = ', 'ALREADY_AUTHENTICATED') \
                           .order('-created') \
                           .fetch(1000, offset=settings.MAX_STORED_ACCOUNTS)
            for account in accounts:
                account.delete()


class DoubanProfile(db.Model):
    """
    豆瓣用户档案
    包括用户名、所在城市、简介、URL 和头像 URL 等信息

    """
    douban_id = db.StringProperty(required=True)
    user_name = db.StringProperty()
    screen_name = db.StringProperty()
    location = db.StringProperty()
    content = db.StringProperty()
    url = db.LinkProperty(required=True)
    image_url = db.LinkProperty()
    blog_url = db.LinkProperty()
    created = db.DateTimeProperty(auto_now_add=True)
    updated = db.DateTimeProperty(auto_now=True)

    @classmethod
    def get_by_douban_id(cls, douban_id):
        """
        按豆瓣 ID 获取用户档案
        如果超过了缓存的有效时限，更新档案

        """
        profile = cls.all().filter('douban_id = ', douban_id).get()
        if profile and profile.need_update():
            service = douban_service()
            # GData 不太支持 Unicode
            entry = service.GetPeople('/people/%s' % \
                                      douban_id.encode('utf-8'))
            profile.update(entry)
        return profile

    @classmethod
    def insert_or_update(cls, people_entry):
        """ 新建或者更新用户档案 """
        profile = cls.get_by_douban_id(parse_id(people_entry))
        if profile is None:
            profile = cls.insert(people_entry)
        else:
            profile.update(people_entry)
        return profile

    @classmethod
    def insert(cls, people_entry):
        """ 新建用户档案 """
        url, image_url, blog_url = parse_urls(people_entry)
        new_profile = DoubanProfile(douban_id=parse_id(people_entry), \
                                    user_name=u(people_entry.uid.text), \
                                    screen_name=u(people_entry.title.text), \
                                    location=u(people_entry.location.text), \
                                    content=u(people_entry.content.text), \
                                    url=url, \
                                    image_url=image_url, \
                                    blog_url=blog_url)
        new_profile.put()
        return new_profile

    def update(self, people_entry):
        """ 更新用户档案 """
        url, image_url, blog_url = parse_urls(people_entry)
        self.user_name = u(people_entry.uid.text)
        self.screen_name = u(people_entry.title.text)
        self.location = u(people_entry.location.text)
        self.content = u(people_entry.content.text)
        self.url = url
        self.image_url = image_url
        self.blog_url = blog_url
        self.put()

    def need_update(self):
        """ 检查用户档案是否超过了缓存的有效时限 """
        if settings.MAX_CACHE_TIME > 0:
            return datetime.now() - self.updated > \
                            timedelta(hours=settings.MAX_CACHE_TIME)
        else:
            return False
