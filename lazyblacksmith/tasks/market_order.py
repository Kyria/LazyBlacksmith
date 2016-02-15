# -*- encoding: utf-8 -*-
import config

from lazyblacksmith.extension.celery_app import celery_app
from lazyblacksmith.models import ItemAdjustedPrice
from lazyblacksmith.models import ItemPrice
from lazyblacksmith.models import Region
from lazyblacksmith.models import db
from lazyblacksmith.utils.crestutils import get_all_items
from lazyblacksmith.utils.crestutils import get_by_attr
from lazyblacksmith.utils.crestutils import get_crest


from ratelimiter import RateLimiter

from sqlalchemy.exc import IntegrityError

from gevent import monkey
from gevent.pool import Pool

monkey.patch_all()
rate_limiter = RateLimiter(max_calls=config.CREST_REQ_RATE_LIM / 2, period=1)


def crest_order_price(crest_url, type_url, min_max_function, item_id, region, is_buy_order):
    """
    Get and return the orders <type> (sell|buy) from
    a given region for a given type
    """

    # call the crest page and extract all items from every pages if required
    crest_orders = crest_url(type=type_url)
    order_list = get_all_items(crest_orders)

    # if no orders,
    if not order_list:
        return

    # extract min/max
    min_max = min_max_function(order_list, key=lambda order: order.price)

    # get item price from db
    item_price = ItemPrice.query.get(item_id)

    # if not in db, try to insert it
    if not item_price:
        try:
            item_price = ItemPrice(item_id=item_id, region_id=region.id)
            db.session.add(item_price)
            db.session.commit()
        except IntegrityError:
            # another thread might have inserted it, so we get the object again
            db.session.rollback()
            item_price = ItemPrice.query.get(item_id)

    # update price
    if is_buy_order:
        item_price.buy_price = min_max.price
    else:
        item_price.sell_price = min_max.price

    # and commit !
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()


@celery_app.task
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
