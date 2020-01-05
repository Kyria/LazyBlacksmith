# -*- encoding: utf-8 -*-
import logging
import json

import config

from lazyblacksmith.extension.esipy import esiclient_nocache as esiclient
from lazyblacksmith.extension.esipy.operations import (
    get_markets_region_id_orders
)
from lazyblacksmith.models import ItemPrice
from lazyblacksmith.models import Region
from lazyblacksmith.models import MarketOrder
from lazyblacksmith.models import db

from ... import lbtsk

LOGGER = logging.getLogger(__file__)

@lbtsk(name="market_orders_region_id")
def task_market_orders(region_id: int):
    insert_orders_list = []
    # get the first page to get the total number of page
    op = get_markets_region_id_orders(
        region_id=region_id,
        order_type='all',
        page=1
    )
    region_order_one = esiclient.request(op, raw_body_only=True)

    # if failed, stop
    if region_order_one.status != 200:
        LOGGER.error(
            'Request failed [%s, %s]: %d\nPayload: %s',
            op[0].url,
            op[0].query,
            region_order_one.status,
            region_order_one.raw,
        )
        return

    # prepare all other pages
    total_page = region_order_one.header['X-Pages'][0]
    operations = []
    for page in range(2, total_page + 1):
        operations.append(get_markets_region_id_orders(
            region_id=region_id,
            order_type='all',
            page=page
        ))

    # check how many thread we will set
    if config.MARKET_ORDER_THREADS is not None:
        threads = config.MARKET_ORDER_THREADS
    else:
        threads = total_page

    # query all other pages and add the first page
    order_list = esiclient.multi_request(
        operations, raw_body_only=True, threads=threads)

    for req, response in [(op[0], region_order_one)] + order_list:
        region_orders = json.loads(response.raw)
        if response.status != 200:
            LOGGER.error(
                'Request failed [%s, %s]: %d\nPayload: %s',
                req.url,
                req.query,
                response.status,
                response.raw,
            )
            continue

        if not region_orders:
            LOGGER.warning(
                "Region %d result was empty [%s]",
                region_id, req.query
            )
            continue

        for order in region_orders:
            row = MarketOrder(**{
                'order_id': order['order_id'],
                'item_id': order['type_id'],
                'region_id': region_id,
                'system_id': order['system_id'],
                'price': order['price'],
                'is_buy_order': order['is_buy_order']
            })
            insert_orders_list.append(row)

    db.engine.execute("TRUNCATE TABLE %s" % MarketOrder.__tablename__)
    #db.engine.execute(
    #    MarketOrder.__table__.insert(),
    #    insert_orders_list
    #)
    db.session.bulk_save_objects(insert_orders_list)
    db.session.commit()
