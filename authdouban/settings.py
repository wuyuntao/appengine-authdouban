# -*- coding: UTF-8 -*-

# 豆瓣 API key
DOUBAN_API_KEY = 'yourapikeyhere'
DOUBAN_API_SECRET = 'yourapisecrethere'
# 是否在服务器端缓存用户的豆瓣档案
STORE_DOUBAN_PROFILE = True
# 服务器端缓存用户档案的有效时限（小时）。如果设为0，则不更新用户档案
MAX_CACHE_TIME = 24
# 一个用户最多可以授权的豆瓣帐户，0 为无限制（但AppEngine最多只能返回1000条查询）
# 如果超过限制，自动删除最早的授权帐户
MAX_STORED_ACCOUNTS = 1
