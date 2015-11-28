# -*- encoding: utf-8 -*-
import config

from lazyblacksmith.utils.pycrest import EVE
from lazyblacksmith.cache import cache

from flask import url_for

def get_crest():
    """ Return a CREST object initialized """
    crest = EVE(
        client_id = config.CREST_CLIENT_ID, 
        api_key = config.CREST_SECRET_KEY, 
        redirect_uri = "%s%s" % (config.CREST_REDIRECT_DNS, '/sso/crest/callback'),
        user_agent = config.CREST_USER_AGENT,
    )
    crest()
    return crest

def get_by_attr(objlist, attr, val):
    ''' Searches list of dicts for a dict with dict[attr] == val '''
    matches = [getattr(obj, attr) == val for obj in objlist]
    index = matches.index(True)  # find first match, raise ValueError if not found
    return objlist[index]

def get_all_items(page):
    ''' Fetch data from all pages '''
    ret = page().items
    while hasattr(page(), 'next'):
        page = page().next()
        ret.extend(page().items)
    return ret

@cache.cached(timeout=3600*24)
def get_adjusted_price():
    crest = None
    if current_user.is_authenticated:
        crest = current_user.get_authed_crest()
    else:
        crest = get_crest()

    item_adjusted_price = {}

    marketPrice = get_all_items(crest.marketPrices())
    for itemPrice in marketPrice:
        item_adjusted_price[marketPrice['type']['id']] = marketPrice['adjustedPrice']

    return item_adjusted_price