# -*- encoding: utf-8 -*-
import config

from lazyblacksmith.extension.cache import cache
from lazyblacksmith.utils.pycrest import EVE
from lazyblacksmith.utils.pycrest.cache import APICache
from lazyblacksmith.utils.pycrest.errors import APIException

from requests.adapters import HTTPAdapter


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


def get_crest(cache=LbCache()):
    """ Return a CREST object initialized """
    transport_adapter = HTTPAdapter(
        pool_connections=20,
        pool_maxsize=100,
    )

    crest = EVE(
        client_id=config.CREST_CLIENT_ID,
        api_key=config.CREST_SECRET_KEY,
        redirect_uri="%s%s" % (
            config.CREST_REDIRECT_DNS, '/sso/crest/callback'
        ),
        user_agent=config.CREST_USER_AGENT,
        cache=cache,
        transport_adapter=transport_adapter,
    )
    try:
        crest()
    except APIException as e:
        print('Crest init failed: %s' % e)
    return crest


def get_by_attr(objlist, attr, val):
    """ Searches list of dicts for a dict with dict[attr] == val """
    matches = [getattr(obj, attr) == val for obj in objlist]
    index = matches.index(True)
    return objlist[index]


def get_all_items(page):
    """ Fetch data from all pages """
    ret = page.items
    while hasattr(page, 'next'):
        page = page.next()
        ret.extend(page.items)
    return ret
