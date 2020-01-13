# -*- encoding: utf-8 -*-
import logging
import json

from concurrent.futures import ThreadPoolExecutor
from threading import Lock

import config

from lazyblacksmith.extension.esipy import esiclient_nocache as esiclient
from lazyblacksmith.extension.esipy.operations import (
    get_markets_region_id_orders
)
from lazyblacksmith.models import ItemPrice
from lazyblacksmith.models import Region
from lazyblacksmith.models import db
from lazyblacksmith.utils.time import utcnow

from ... import lbtsk

LOGGER = logging.getLogger('lbtasks')
MOLOCK = Lock()


@lbtsk(name="market_orders_region_id")
def task_market_order_price(region_id: int):
    item_list = {'update': {}, 'insert': {}}

    # get the currently priced items
    item_id_list = [
        it[0] for it in db.session.query(
            ItemPrice.item_id
        ).filter_by(region_id=region_id)
    ]

    # get the first page to get the total number of page
    region_head = esiclient.head(
        get_markets_region_id_orders(
            region_id=region_id,
            order_type='all',
            page=1
        )
    )

    # if failed, stop
    if region_head.status != 200:
        LOGGER.error(
            'Failed to get headers for market_orders in region %d [HTTP: %d]',
            region_id,
            region_head.status
        )
        return

    # get all page content
    total_page = region_head.header['X-Pages'][0]
    #with ThreadPoolExecutor(max_workers=config.MARKET_ORDER_THREADS or total_page) as pool:
    #for page in range(1, total_page + 1):
    #    pool.submit(
    #        get_market_page,
    #        region_id,
    #        page,
    #        item_list,
    #        item_id_list
    #    )
    market_pages_tasks = get_market_page.map([
        (region_id, page, item_list, item_id_list)
        for page in range(1, total_page + 1)
    ])
    print(len(item_list))
    market_pages_tasks.get(blocking=True)
    print(len(item_list))
    print(item_list)

@lbtsk(name="market_orders_page_region_id")
def get_market_page(
        region_id: int,
        page: int,
        price_list: dict,
        priced_items: list):
    """ tt """

    operation = get_markets_region_id_orders(
        region_id=region_id,
        order_type='all',
        page=page
    )

    LOGGER.info('Region: %d, page: %d - Fetching data', region_id, page)
    response = esiclient.request(operation, raw_body_only=True)
    region_orders = json.loads(response.raw)

    if response.status != 200:
        LOGGER.error(
            'Request failed [%s, %s, %d]\nPayload: %s',
            operation[0].url,
            operation[0].query,
            response.status,
            response.raw,
        )
        return

    if not region_orders:
        return

    LOGGER.info('Region: %d, page: %d - Parsing results', region_id, page)
    for order in region_orders:
        update_itemlist_from_order(
            region_id,
            price_list,
            priced_items,
            order,
        )
    return True


def update_itemlist_from_order(region_id, item_list, item_id_list, order):
    item_id = order['type_id']

    # values if we already have this item in database or not
    # we need custom field label for update, as we don't want the
    # region_id item_id to be updated but we need them in where clause
    if item_id in item_id_list:
        stmt_type = 'update'
        region_id_label = 'u_region_id'
        item_id_label = 'u_item_id'
    else:
        stmt_type = 'insert'
        region_id_label = 'region_id'
        item_id_label = 'item_id'

    # acquire lock, as we don't want other thread to update at the same time
    with MOLOCK:
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

            current_item['sell_price'] = min(
                current_item['sell_price'],
                order['price']
            )
        else:
            current_item['buy_price'] = max(
                current_item['buy_price'],
                order['price']
            )
