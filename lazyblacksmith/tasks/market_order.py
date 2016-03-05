# -*- encoding: utf-8 -*-
import config
import time

from lazyblacksmith.extension.celery_app import celery_app
from lazyblacksmith.models import ItemAdjustedPrice
from lazyblacksmith.models import ItemPrice
from lazyblacksmith.models import Region
from lazyblacksmith.models import db
from lazyblacksmith.utils.crestutils import get_all_items
from lazyblacksmith.utils.crestutils import get_by_attr
from lazyblacksmith.utils.crestutils import get_crest
from lazyblacksmith.utils.pycrest.errors import APIException
from requests.exceptions import Timeout

import gevent

from ratelimiter import RateLimiter

from gevent import monkey

monkey.patch_all()
rate_limiter = RateLimiter(max_calls=config.CREST_REQ_RATE_LIM / 2, period=1)


def crest_order_price(market_crest_url, type_url, item_id, region):
    """
    Get and return the orders <type> (sell|buy) from
    a given region for a given type
    """

    # call the crest page and extract all items from every pages if required
    try:
        buy_orders_crest = get_all_items(market_crest_url.marketBuyOrders(type=type_url))
        sell_orders_crest = get_all_items(market_crest_url.marketSellOrders(type=type_url))
    except APIException as api_e:
        if "503" in str(api_e):
            print "[%s] Error 503 happened ! Item ID: %s" % (time.strftime("%x %X"), item_id)
        else:
            print "%s Unexpected error. Item ID:  %s " % (time.strftime("%x %X"), item_id)
        return None
    except Timeout:
        print "[%s] Error: timeout while getting price from crest ! Item ID: %s" % (time.strftime("%x %X"), item_id)
        return None

    # if no orders found...
    if not sell_orders_crest or not buy_orders_crest:
        return

    # extract min/max
    sell_price = min(sell_orders_crest, key=lambda order: order.price)
    buy_price = max(buy_orders_crest, key=lambda order: order.price)

    return {
        'item_id': item_id,
        'sell_price': sell_price.price,
        'buy_price': buy_price.price,
        'region_id': region.id,
    }


@celery_app.task(name="schedule.update_market_price")
def update_market_price():
    """Celery task to upgrade prices through CREST"""
    crest = get_crest()
    item_type_url = crest.itemTypes.href

    region_list = Region.query.filter(
        Region.id.in_(config.CREST_REGION_PRICE)
    ).all()

    item_list = ItemAdjustedPrice.query.all()

    # number in pool is the max per second we want.
    greenlet_pool = []

    raw_sql_query = """
        INSERT INTO %s (item_id, region_id, sell_price, buy_price)
        VALUES (:item_id, :region_id, :sell_price, :buy_price)
        ON DUPLICATE KEY UPDATE sell_price = :sell_price, buy_price = :buy_price
    """ % ItemPrice.__tablename__

    # loop over regions
    for region in region_list:
        market_crest = (get_by_attr(get_all_items(crest.regions()), 'name', region.name))()
        # donner market_crest en param
        # récup sell et buy
        # return dict avec tout dedans
        # recup la liste de tous les order
        # bulk insert.

        # loop over items
        for item in item_list:
            type_url = '%s%s/' % (item_type_url, item.item_id)

            # use rate limited contexte to prevent too much greenlet spawn per seconds
            with rate_limiter:
                # greenlet spawn buy order getter
                greenlet_pool.append(gevent.spawn(
                    crest_order_price,
                    market_crest,
                    type_url,
                    item.item_id,
                    region
                ))

        gevent.joinall(greenlet_pool)
        results = [greenlet.value for greenlet in greenlet_pool if greenlet.value]
        db.engine.execute(
            raw_sql_query,
            results
        )
        greenlet_pool = []
