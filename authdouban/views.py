# -*- coding: UTF-8 -*-

import os
import urllib
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from gdata.alt.appengine import run_on_appengine
from douban.service import DoubanService
import settings
from models import DoubanAccount, DoubanProfile

def douban_service():
    service = DoubanService(api_key=settings.DOUBAN_API_KEY,
                            secret=settings.DOUBAN_API_SECRET)
    return run_on_appengine(service)

def render_to_response(handler, template_name, extra_context={}):
    path = os.path.join(os.path.dirname(__file__), template_name)
    context = {
        'login_url': users.create_login_url('/'),
    }
    user = users.get_current_user()
    if user:
        context.update({
            'user': user.nickname(),
            'email': user.email(),
            'logout_url': users.create_logout_url('/'),
        })
    if extra_context:
        context.update(extra_context)
    return handler.response.out.write(template.render(path, context))

class ListAccounts(webapp.RequestHandler):
    """
    列出已授权帐户

    """
    def get(self, template_name='templates/authdouban/list_account.html'):
        user = users.get_current_user()
        accounts = DoubanAccount.get_authenticated_accounts(user=user)
        return render_to_response(self, template_name, { 'douban_accounts': accounts })

class AuthorizeAccount(webapp.RequestHandler):
    """
    新建一个豆瓣授权帐户。
    向豆瓣请求 request key，将其保存到数据库之后，返回用户的授权链接

    """
    def get(self):
        service = douban_service()
        key, secret = service.client.get_request_token()

        user = users.get_current_user()
        new_account = DoubanAccount.create_unauthorized_account(user, key, secret)

        callback_url = 'http://%s/account/douban/authorize/complete/' % self.request.host
        auth_url = service.client.get_authorization_url(key, secret, callback_url)
        return self.redirect(auth_url)

class AuthorizationComplete(webapp.RequestHandler):
    """
    用户完成授权后的回调，向豆瓣请求 access key
    如果经验证 access key 可以用来访问豆瓣，将其保存到数据库
    如果验证成功，返回用户授权成功页面
    如果验证失败，重定向到授权失败页面

    """
    def get(self, template_name='templates/authdouban/complete.html'):
        request_key = self.request.get('oauth_token')
        account = DoubanAccount.all().filter('request_key = ', request_key).get()

        if not account or account.request_key == 'ALREADY_AUTHENTICATED':
            reason = urllib.quote_plus('Request Key 不正确')
            return self.redirect('/account/douban/authorize/failure/?reason=%s' % reason)

        service = douban_service()
        key, secret, douban_id = service.client.get_access_token(account.request_key, account.request_secret)
        if key and secret and douban_id:
            account.set_access_key(key, secret, douban_id)
            account.remove_duplicate_accounts()
            if settings.STORE_DOUBAN_PROFILE:
                entry = service.GetPeople('/people/%s' % douban_id)
                profile = DoubanProfile.insert_or_update(entry)
            return render_to_response(self, template_name, { 'douban_account': account })
        else:
            reason = urllib.quote_plus('获取 Access Key 失败')
            return self.redirect('/account/douban/authorize/failure/?reason=%s' % reason)

class AuthorizationFailure(webapp.RequestHandler):
    """
    用户授权失败页面

    """
    def get(self, template_name='templates/authdouban/failure.html'):
        reason = self.request.get('reason')
        return render_to_response(self, template_name, { 'reason': reason })

class DeleteAccount(webapp.RequestHandler):
    """
    删除已授权帐户

    """
    def get(self, key, template_name='templates/authdouban/delete_account.html'):
        context = {
            'douban_account': DoubanAccount.get(key),
        }
        return render_to_response(self, template_name, context)

    def post(self, key):
        DoubanAccount.get(key).delete()
        return self.redirect('/account/douban/')
