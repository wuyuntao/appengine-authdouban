# -*- coding: UTF-8 -*-

from views import *

urlpatterns = (
    (r'^/account/douban/$', ListAccounts),
    (r'^/account/douban/authorize/$', AuthorizeAccount),
    (r'^/account/douban/authorize/complete/$', AuthorizationComplete),
    (r'^/account/douban/authorize/failure/$', AuthorizationFailure),
    (r'^/account/douban/delete/(.*)/$', DeleteAccount),
)
