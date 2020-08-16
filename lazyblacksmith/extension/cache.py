# -*- encoding: utf-8 -*-
from flask_caching import Cache
from esipy.cache import BaseCache
from esipy.cache import _hash


class LbCache(BaseCache):
    """ Custom BaseCache implementation for Lazyblacksmith
        used in esipy, to use the flask cache
    """
    def __init__(self, lb_cache):
        self.cache = lb_cache

    def set(self, key, value, expire=300):
        self.cache.set(_hash(key), value, expire)

    def get(self, key, default=None):
        cached = self.cache.get(_hash(key))
        return cached if cached is not None else default

    def invalidate(self, key):
        self.cache.delete(_hash(key))


CACHE = Cache()
LBCACHE = LbCache(CACHE)
