# -*- encoding: utf-8 -*-
import config
import time

from lazyblacksmith.extension.celery_app import celery_app
from lazyblacksmith.models import ItemPrice
from lazyblacksmith.models import Region
from lazyblacksmith.models import db
from lazyblacksmith.utils.crestutils import get_all_items
from lazyblacksmith.utils.crestutils import get_by_attr
from lazyblacksmith.utils.crestutils import get_crest
from lazyblacksmith.utils.time import utcnow

from ratelimiter import RateLimiter

# divide by 2, as we may have mulitple pages in some cases (it still does 75/sec)
rate_limiter = RateLimiter(max_calls=config.CREST_REQ_RATE_LIM / 2, period=1)


def crest_order_price(region_crest, region_id, item_id_list):
    """
    Get and return the orders <type> (sell|buy) from
    a given region
    """

    # call the crest page and extract all items from every pages if required
    orders_crest = get_all_items(region_crest.marketOrdersAll())

    item_list = {'update': {}, 'insert': {}}
    for order in orders_crest:
        item_id = order.type

        # values if we already have this item in database or not
        if item_id in item_id_list:
            stmt_type = 'update'
            region_id_label = 'u_region_id'
            item_id_label = 'u_item_id'
        else:
            stmt_type = 'insert'
            region_id_label = 'region_id'
            item_id_label = 'item_id'

        # do we already looped on this item ?
        if item_id not in item_list[stmt_type]:
            item_list[stmt_type][item_id] = {
                'sell_price': None,
                'buy_price': 0,
                region_id_label: region_id,
                item_id_label: item_id,
                'updated_at': utcnow()
            }

        if not order.buy:
            # if we have already set this item, but on buy order, set price
            # because min() will always return "0" if we set it to 0 on init
            if item_list[stmt_type][item_id]['sell_price'] is None:
                item_list[stmt_type][item_id]['sell_price'] = order.price
                continue

            item_list[stmt_type][item_id]['sell_price'] = min(
                item_list[stmt_type][item_id]['sell_price'],
                order.price
            )
        else:
            item_list[stmt_type][item_id]['buy_price'] = max(
                item_list[stmt_type][item_id]['buy_price'],
                order.price
            )

    return item_list


@celery_app.task(name="schedule.update_market_price")
def update_market_price():
    """Celery task to upgrade prices through CREST"""
    crest = get_crest(cache=None)

    region_list = Region.query.filter(
        Region.id.in_(config.CREST_REGION_PRICE)
    ).all()

    print "Total | Delta | Delta SQL | Insert | Update | Region"
    print "----------------------------------------------------"
    time_start = time.time()

    for region in region_list:
        time_delta = time.time()

        region_crest = get_all_items(crest.regions())
        region_crest = get_by_attr(region_crest, 'name', region.name)
        region_crest = region_crest()

        item_id_list = [it[0] for it in db.session.query(ItemPrice.item_id).filter_by(region_id=region.id)]

        # use rate limited context to prevent too much call per seconds
        with rate_limiter:
            item_list = crest_order_price(region_crest, region.id, item_id_list)

        time_delta_sql = time.time()
        # check if we have any update to do
        if len(item_list['update']) > 0:
            update_stmt = ItemPrice.__table__.update() \
                                   .where(ItemPrice.item_id == db.bindparam('u_item_id')) \
                                   .where(ItemPrice.region_id == db.bindparam('u_region_id'))
            db.engine.execute(
                update_stmt,
                item_list['update'].values()
            )

        # check if we have any insert to do
        if len(item_list['insert']) > 0:
            # execute inserts
            db.engine.execute(
                ItemPrice.__table__.insert(),
                item_list['insert'].values()
            )

        print '%0.2fs | %0.2fs | %0.2fs | %d | %d | %s' % (
            time.time() - time_start,
            time_delta_sql - time_delta,
            time.time() - time_delta_sql,
            len(item_list['insert']),
            len(item_list['update']),
            region.name
        )
