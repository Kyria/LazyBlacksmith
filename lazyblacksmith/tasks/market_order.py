# -*- encoding: utf-8 -*-
import config
import time

from esipy import EsiClient
from lazyblacksmith.extension.celery_app import celery_app
from lazyblacksmith.extension.esipy.esipy import transport_adapter
from lazyblacksmith.extension.esipy.operations import (
    get_markets_region_id_orders
)
from lazyblacksmith.models import ItemPrice
from lazyblacksmith.models import Region
from lazyblacksmith.models import db
from lazyblacksmith.utils.time import utcnow

from flask import json
from ratelimiter import RateLimiter

# (re)define some required objects
esiclient = EsiClient(
    transport_adapter=transport_adapter,
    cache=None,
    headers={'User-Agent': config.ESI_USER_AGENT}
)

# divide by 2, as we may have mulitple pages
# in some cases (it still does 75/sec)
rate_limiter = RateLimiter(max_calls=config.ESI_REQ_RATE_LIM, period=1)


@celery_app.task(name="get_region_order_price")
def esi_region_order_price(region_id, item_id_list):
    """
    Get and return the orders <type> (sell|buy) from
    a given region
    """

    # call the crest page and extract all items from every pages if required
    page = 0
    item_list = {'update': {}, 'insert': {}}
    order_number = 0

    while True:
        page += 1
        region_orders_res = esiclient.request(
            get_markets_region_id_orders(
                region_id=region_id,
                order_type='all',
                page=page
            ),
            raw_body_only=True
        )

        if region_orders_res.status != 200:
            region_orders_res = esiclient.request(
                get_markets_region_id_orders(
                    region_id=region_id,
                    order_type='all',
                    page=page
                ),
                raw_body_only=True
            )

        if region_orders_res.status != 200:
            region_orders_res = esiclient.request(
                get_markets_region_id_orders(
                    region_id=region_id,
                    order_type='all',
                    page=page
                ),
                raw_body_only=True
            )

        if region_orders_res.status != 200:
            continue

        region_orders = json.loads(region_orders_res.raw)

        if not region_orders:
            break

        for order in region_orders:
            order_number += 1
            item_id = order['type_id']

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

            current_item = item_list[stmt_type][item_id]

            if not order['is_buy_order']:
                if current_item['sell_price'] is None:
                    current_item['sell_price'] = order['price']
                    continue

                current_item['sell_price'] = min(
                    current_item['sell_price'],
                    order['price']
                )
            else:
                current_item['buy_price'] = max(
                    current_item['buy_price'],
                    order['price']
                )

    region = Region.query.get(region_id)

    # check if we have any update to do
    if len(item_list['update']) > 0:
        update_stmt = ItemPrice.__table__.update()
        update_stmt = update_stmt.where(
            ItemPrice.item_id == db.bindparam('u_item_id')
        ).where(
            ItemPrice.region_id == db.bindparam('u_region_id')
        )
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

    # print '%0.2fs | %0.2fs | %0.2fs | %d | %d | %s' % (
    #     time.time() - time_start,
    #     time_delta_sql - time_delta,
    #     time.time() - time_delta_sql,
    #     len(item_list['insert']),
    #     len(item_list['update']),
    #     region.name
    # )
    #
    # region.market_order_item_number = (
    #     len(item_list['insert']) + len(item_list['update'])
    # )
    # region.market_order_number = order_number
    # region.market_order_page = page - 1
    # db.session.commit()


@celery_app.task(name="schedule.update_market_price")
def update_market_price():
    """Celery task to upgrade prices through CREST"""
    region_list = Region.query.filter(
        Region.id.in_(config.ESI_REGION_PRICE)
    ).all()

    for region in region_list:
        item_id_list = [
            it[0] for it in db.session.query(
                ItemPrice.item_id
            ).filter_by(region_id=region.id)
        ]

        esi_region_order_price.s(region.id, item_id_list).apply_async(queue='celery')
