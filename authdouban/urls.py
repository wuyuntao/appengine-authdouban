# -*- coding: UTF-8 -*-

from views import *

urlpatterns = (
    (r'^/authdouban/$', AuthAccount),
    (r'^/authdouban/request/$', AuthRequest),
    (r'^/authdouban/access/$', AuthAccess),
    (r'^/authdouban/complete/$', AuthComplete),
    (r'^/authdouban/failure/$', AuthFailure),
    (r'^/authdouban/delete/$', AuthDelete),
)
