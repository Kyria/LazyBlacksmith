# -*- encoding: utf-8 -*-
import pycrest
import config


def get_crest():
    """ Return a CREST object initialized """
    crest = pycrest.EVE()
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