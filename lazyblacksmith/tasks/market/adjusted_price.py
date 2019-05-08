# -*- encoding: utf-8 -*-
from ..lb_task import LbTask

from lazyblacksmith.extension.celery_app import celery_app
from lazyblacksmith.extension.esipy import esiclient
from lazyblacksmith.extension.esipy.operations import get_markets_prices
from lazyblacksmith.models import Activity
from lazyblacksmith.models import ItemAdjustedPrice
from lazyblacksmith.models import Item
from lazyblacksmith.models import TaskState
from lazyblacksmith.models import db


@celery_app.task(name="update_adjusted_price", base=LbTask, bind=True)
def task_update_adjusted_price_base_cost(self):
    """Task that update the adjusted prices from the API then calculate the
    base cost for every blueprints.
    """
    self.start()
    prices = update_adjusted_price()
    if prices is not None:
        if update_base_costs(prices):
            return self.end(TaskState.SUCCESS)
    return self.end(TaskState.ERROR)


def update_adjusted_price():
    """ Get market prices from ESI and update the database.
    Raises exception if database cannot be updated.

    Returns
    -------
    Dict
        the prices that were updated.

    """
    item_adjusted_price = {}
    count = 0
    market_price = esiclient.request(get_markets_prices())

    if market_price.status == 200:
        for item_price in market_price.data:
            count += 1
            item_adjusted_price[item_price.type_id] = {
                'item_id': item_price.type_id,
                'price': item_price.adjusted_price or 0.00
            }

        db.engine.execute(
            "TRUNCATE TABLE %s" % ItemAdjustedPrice.__tablename__
        )
        db.engine.execute(
            ItemAdjustedPrice.__table__.insert(),
            list(item_adjusted_price.values())
        )
        db.session.commit()
        return item_adjusted_price
    return None


def update_base_costs(prices):
    """ Calculate the base cost for every blueprints

    Parameters
    ----------
    prices : dict
        Description of parameter `prices`.

    Returns
    -------
    Boolean
        if the basecost were calculated correctly or not.
    """

    blueprints = Item.query.filter(
        Item.max_production_limit.isnot(None)
    ).all()

    for bp in blueprints:
        bp.base_cost = 0.0
        materials = bp.activity_materials.filter_by(
            activity=ActivityEnum.MANUFACTURING.id
        ).all()

        for material in materials:
            if material.material_id in prices:
                bp.base_cost += (
                    prices[material.material_id]['price'] * material.quantity
                )

    db.session.commit()
    return True
