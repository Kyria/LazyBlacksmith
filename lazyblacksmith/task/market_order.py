# -*- encoding: utf-8 -*-
import ratelim

import config

import time

from lazyblacksmith.extension.celery_app import celery_app
from lazyblacksmith.models import ItemPrice
from lazyblacksmith.models import Region
from lazyblacksmith.models import db
from lazyblacksmith.utils.crestutils import get_all_items
from lazyblacksmith.utils.crestutils import get_by_attr
from lazyblacksmith.utils.crestutils import get_crest

import gevent

from sqlalchemy.exc import IntegrityError

from gevent import monkey
from gevent.pool import Pool
monkey.patch_all()


@ratelim.patient(10, 1)
def crest_order_price(crest_url, type_url, min_max_function, item, is_buy_order):
    """
    Get and return the orders <type> (sell|buy) from
    a given region for a given type
    """
    # call the crest page and extract all items from every pages if required
    crest_orders = crest_url(type=type_url)
    order_list = get_all_items(crest_orders)

    print time.time()
    # if no orders,
    if not order_list:
        return
    # get the item ID
    min_max = min_max_function(order_list, key=lambda order: order.price)

    if is_buy_order:
        item.buy_price = min_max.price
    else:
        item.sell_price = min_max.price

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()


@celery_app.task()
def update_market_price():
    """Celery task to upgrade prices through CREST"""
    print "[INIT CREST]"
    crest = get_crest()
    item_type_url = crest.itemTypes.href

    print "[GET DB INFO]"
    region = Region.query.filter(
        Region.id.in_(config.CREST_REGION_PRICE)
    ).all()[0]
    print region.name
    item_list = ItemPrice.query.all()

    # number in pool is the max per second we want.
    print "[CREATE POOL]"
    greenlet_pool = Pool(10)

    #for region in region_list:
    market_crest = (get_by_attr(get_all_items(crest.regions()), 'name', region.name))()
    buy_orders_crest = market_crest.marketBuyOrders
    sell_orders_crest = market_crest.marketSellOrders

    for item in item_list:
        type_url = '%s%s/' % (item_type_url, item.item_id)
        # greenlet spawn buy order getter
        greenlet_pool.spawn(
            crest_order_price,
            buy_orders_crest,
            type_url,
            max,
            item,
            True
        )

        # greenlet spawn sell order getter
        greenlet_pool.spawn(
            crest_order_price,
            sell_orders_crest,
            type_url,
            min,
            item,
            False
        )

    greenlet_pool.join
