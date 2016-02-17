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

from ratelimiter import RateLimiter

from gevent import monkey
from gevent.pool import Pool

monkey.patch_all()
rate_limiter = RateLimiter(max_calls=config.CREST_REQ_RATE_LIM / 2, period=1)


def crest_order_price(crest_url, type_url, min_max_function, item_id, region, is_buy_order):
    """
    Get and return the orders <type> (sell|buy) from
    a given region for a given type
    """

    raw_sql_query = """
        INSERT INTO %s (item_id, region_id, sell_price, buy_price)
        VALUES (%s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE %s = %s
    """

    # call the crest page and extract all items from every pages if required
    try:
        crest_orders = crest_url(type=type_url)
        order_list = get_all_items(crest_orders)
    except APIException as api_e:
        if "503" in str(api_e):
            print "[%s] Error 503 happened !" % time.strftime("%x %X")
        else:
            print "%s Unexpected error : %s " % (time.strftime("%x %X"), api_e)
    except Timeout:
        print "[%s] Error: timeout while getting price from crest !" % time.strftime("%x %X")

    # if no orders,
    if not order_list:
        return

    # extract min/max
    min_max = min_max_function(order_list, key=lambda order: order.price)

    # update price
    if is_buy_order:
        db.engine.execute(raw_sql_query % (
            ItemPrice.__tablename__,
            item_id,
            region.id,
            None,
            min_max.price,
            'buy_price',
            min_max.price,
        ))

    else:
        db.engine.execute(raw_sql_query % (
            ItemPrice.__tablename__,
            item_id,
            region.id,
            min_max.price,
            None,
            'sell_price',
            min_max.price,
        ))


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
    greenlet_pool = Pool(config.CREST_REQ_RATE_LIM)

    # loop over regions
    for region in region_list:
        market_crest = (get_by_attr(get_all_items(crest.regions()), 'name', region.name))()
        buy_orders_crest = market_crest.marketBuyOrders
        sell_orders_crest = market_crest.marketSellOrders

        # loop over items
        for item in item_list:
            type_url = '%s%s/' % (item_type_url, item.item_id)

            # use rate limited contexte to prevent too much greenlet spawn per seconds
            with rate_limiter:
                # greenlet spawn buy order getter
                greenlet_pool.spawn(
                    crest_order_price,
                    buy_orders_crest,
                    type_url,
                    max,
                    item.item_id,
                    region,
                    True
                )

                # greenlet spawn sell order getter
                greenlet_pool.spawn(
                    crest_order_price,
                    sell_orders_crest,
                    type_url,
                    min,
                    item.item_id,
                    region,
                    False
                )

    greenlet_pool.join()
