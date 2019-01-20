# -*- encoding: utf-8 -*-
import config
import logging
import time

from ..lb_task import LbTask

from lazyblacksmith.extension.celery_app import celery_app
from lazyblacksmith.extension.esipy.esipy import transport_adapter
from lazyblacksmith.extension.esipy.operations import (
    get_markets_region_id_orders
)
from lazyblacksmith.models import ItemPrice
from lazyblacksmith.models import Region
from lazyblacksmith.models import TaskState
from lazyblacksmith.models import db
from lazyblacksmith.utils.tasks import is_task_running
from lazyblacksmith.utils.time import utcnow

from esipy import EsiClient
from flask import json
from sqlalchemy.exc import SQLAlchemyError

# (re)define some required objects
esiclient = EsiClient(
    transport_adapter=transport_adapter,
    cache=None,
    headers={'User-Agent': config.ESI_USER_AGENT},
    retry_requests=True
)

logger = logging.getLogger('lb.tasks')


@celery_app.task(name="spawn_market_price_tasks", base=LbTask, bind=True)
def spawn_market_price_tasks(self):
    """Celery task to spawn market prices update tasks"""
    self.start()
    region_list = Region.query.filter(
        Region.id.in_(config.ESI_REGION_PRICE)
    ).all()

    for region in region_list:
        if not is_task_running(region.id,
                               task_update_region_order_price.__name__):
            item_id_list = [
                it[0] for it in db.session.query(
                    ItemPrice.item_id
                ).filter_by(region_id=region.id)
            ]

            task_id = "%s-%s-%s" % (
                utcnow().strftime('%Y%m%d-%H%M%S'),
                task_update_region_order_price.__name__,
                region.name
            )
            token_state = TaskState(
                task_id=task_id,
                id=region.id,
                scope=task_update_region_order_price.__name__,
            )
            db.session.add(token_state)
            db.session.commit()

            task_update_region_order_price.s(
                region.id,
                item_id_list
            ).apply_async(
                task_id=task_id
            )

    self.end(TaskState.SUCCESS)


@celery_app.task(name="update_region_order_price", base=LbTask, bind=True)
def task_update_region_order_price(self, region_id, item_id_list):
    """ Get the price from the API and update the database for a given region
    """
    self.start()
    fail = False

    # call the market page and extract all items from every pages if required
    item_list = {'update': {}, 'insert': {}}

    # get the first page to get the total number of page
    op = get_markets_region_id_orders(
        region_id=region_id,
        order_type='all',
        page=1
    )
    region_order_one = esiclient.request(op, raw_body_only=True)

    # if failed, stop
    if region_order_one.status != 200:
        logger.error('Request failed [%s, %s, %d]: %s' % (
            op[0].url,
            op[0].query,
            region_order_one.status,
            region_order_one.raw,
        ))
        self.end(TaskState.ERROR)
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

    # parse the response and save everything
    for req, response in [(op[0], region_order_one)] + order_list:
        region_orders = json.loads(response.raw)
        if response.status != 200:
            fail = True
            logger.error('Request failed [%s, %s, %d]: %s' % (
                req.url,
                req.query,
                response.status,
                response.raw,
            ))
            continue

        if not region_orders:
            continue

        for order in region_orders:
            update_itemlist_from_order(
                region_id,
                item_list,
                item_id_list,
                order
            )

    try:
        save_item_prices(item_list)

    except SQLAlchemyError as e:
        logger.error(
            'Something went wrong while trying to insert/update data: %s' % (
                e.message
            )
        )
        db.session.rollback()
        fail = True

    if not fail:
        self.end(TaskState.SUCCESS)
    else:
        self.end(TaskState.ERROR)


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

        current_item['sell_price'] = min(
            current_item['sell_price'],
            order['price']
        )
    else:
        current_item['buy_price'] = max(
            current_item['buy_price'],
            order['price']
        )


def save_item_prices(item_list):
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
            list(item_list['update'].values())
        )

    # check if we have any insert to do
    if len(item_list['insert']) > 0:
        # execute inserts
        db.engine.execute(
            ItemPrice.__table__.insert(),
            list(item_list['insert'].values())
        )

    db.session.commit()
