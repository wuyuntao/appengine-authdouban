# -*- coding: UTF-8 -*-

from views import *

urlpatterns = (
    (r'^/authdouban/$', AuthAccount),
    (r'^/authdouban/authorize/$', AuthRequest),
    (r'^/authdouban/complete/$', AuthComplete),
    (r'^/authdouban/failure/$', AuthFailure),
    (r'^/authdouban/delete/(.*)/$', AuthDelete),
)
