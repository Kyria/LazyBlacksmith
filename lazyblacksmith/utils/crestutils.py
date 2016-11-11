# -*- encoding: utf-8 -*-
import config

from lazyblacksmith.extension.cache import LbCache
from lazyblacksmith.utils.pycrest import EVE
from requests.adapters import HTTPAdapter


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
    crest()
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
