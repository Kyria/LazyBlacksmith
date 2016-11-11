# -*- encoding: utf-8 -*-
from flask_caching import Cache
from lazyblacksmith.utils.pycrest.cache import APICache

cache = Cache()


class LbCache(APICache):
    """ Custom APICache implementation for Lazyblacksmith
        used in pycrest
    """
    def put(self, key, value):
        cache.set(key, value)

    def get(self, key):
        return cache.get(key)

    def invalidate(self, key):
        cache.delete(key)
