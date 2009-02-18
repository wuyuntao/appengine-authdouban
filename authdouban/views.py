# -*- coding: UTF-8 -*-

import os
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from gdata.alt.appengine import run_on_appengine
from douban.service import DoubanService
import settings
from models import DoubanAccount

def douban_service():
    service = DoubanService(api_key=settings.DOUBAN_API_KEY,
                            secret=settings.DOUBAN_API_SECRET)
    return run_on_appengine(service)

def render_to_response(template_name, context={}):
    path = os.path.join(os.path.dirname(__file__), template_name)
    return template.render(path, context)

class AuthAccount(webapp.RequestHandler):
    """
    列出已授权帐户

    """
    def get(self, template_name='templates/authdouban/list_account.html'):
        user = users.get_current_user()
        accounts = DoubanAccount.get_authenticated_accounts(user=user)
        return self.response.out.write(render_to_response(template_name, { 'accounts': accounts }))

class AuthRequest(webapp.RequestHandler):
    """
    新建一个豆瓣授权帐户。
    向豆瓣请求 request key，将其保存到数据库之后，返回用户的授权链接

    """
    def get(self, template_name='templates/authdouban/create_account.html'):
        service = douban_service()
        key, secret = service.client.get_request_token()

        user = users.get_current_user()
        new_account = DoubanAccount(user=user)
        new_account.set_request_key(key, secret)

        callback_url = 'http://%s/authdouban/complete/' % self.request.host 
        auth_url = service.client.get_authorization_url(key, secret, callback_url)
        return self.redirect(auth_url)

class AuthComplete(webapp.RequestHandler):
    """
    用户完成授权后的回调，向豆瓣请求 access key
    如果经验证 access key 可以用来访问豆瓣，将其保存到数据库
    如果验证成功，返回用户授权成功页面
    如果验证失败，重定向到授权失败页面

    """
    def get(self, template_name='templates/authdouban/authentication_complete.html'):
        request_key = self.request.get('oauth_token')
        account = DoubanAccount.all().filter('request_key = ', request_key).get()

        if not account or account.request_key == 'ALREADY_AUTHENTICATED':
            reason = u'Request Key 不正确'
            return self.redirect('/authdouban/failure/?reason=%s' % reason)

        service = douban_service()
        key, secret, douban_id = service.client.get_access_token(account.request_key, account.request_secret)
        if key and secret and douban_id:
            account.set_access_key(key, secret, douban_id)
            return self.response.out.write(render_to_response(template_name, { 'douban_id': douban_id }))
        else:
            return self.redirect('/authdouban/failure/')

class AuthFailure(webapp.RequestHandler):
    """
    用户授权失败页面

    """
    def get(self, template_name='templates/authdouban/authentication_failure.html'):
        reason = self.request.get('reason')
        return self.response.out.write(render_to_response(template_name, { 'reason': reason }))

class AuthDelete(webapp.RequestHandler):
    """
    删除已授权帐户

    """
    def get(self, key, template_name='templates/authdouban/delete_account.html'):
        return self.response.out.write(render_to_response(template_name, { 'douban_id': DoubanAccount.get(key).douban_id }))

    def post(self, key):
        DoubanAccount.get(key).delete()
        return self.redirect('/authdouban/')
