# -*- encoding: utf-8 -*-
import config

from lazyblacksmith.extension.cache import cache
from lazyblacksmith.utils.pycrest import EVE


def get_crest():
    """ Return a CREST object initialized """
    crest = EVE(
        client_id=config.CREST_CLIENT_ID,
        api_key=config.CREST_SECRET_KEY,
        redirect_uri="%s%s" % (
            config.CREST_REDIRECT_DNS, '/sso/crest/callback'
        ),
        user_agent=config.CREST_USER_AGENT,
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


@cache.cached(timeout=3600*24)
def get_adjusted_price():
    crest = get_crest()

    item_adjusted_price = {}

    marketPrice = get_all_items(crest.marketPrices())
    for itemPrice in marketPrice:
        item_adjusted_price[itemPrice.type.id] = itemPrice.adjustedPrice

    return item_adjusted_price
