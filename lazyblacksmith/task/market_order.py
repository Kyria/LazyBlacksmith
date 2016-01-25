# -*- encoding: utf-8 -*-
import ratelim


@ratelim.greedy(150, 1)
def crest_order_price(type, crest_type, crest_region, station):
    """
    Get and return the orders <type> (sell|buy) from
    a given region for a given type
    """
    pass
