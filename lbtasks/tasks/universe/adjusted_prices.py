# -*- encoding: utf-8 -*-
""" Market adjusted prices tasks """
from lazyblacksmith.extension.esipy import esiclient
from lazyblacksmith.extension.esipy.operations import get_markets_prices
from lazyblacksmith.models import Item, ItemAdjustedPrice, db
from lazyblacksmith.models.enums import ActivityEnum

from ... import celery_app


@celery_app.task(name="adjusted_price")
def task_adjusted_price_base_cost():
    """Task that update the adjusted prices from the API then calculate the
    base cost for every blueprints.
    """
    prices = update_adjusted_price()
    if prices is not None:
        update_base_costs(prices)


def update_adjusted_price():
    """Get market prices from ESI and update the database.
    Raises exception if database cannot be updated.

    Returns:
        Dict: The update prices
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
    """Calculate the base cost for every blueprints

    Args:
        prices (dict): the price updated. Keys are item_id

    Returns:
        boolean: If the base costs were calculated correctly or not.
    """
    blueprints = Item.query.filter(
        Item.max_production_limit.isnot(None)
    ).all()

    for bp in blueprints:
        bp.base_cost = 0.0
        materials = bp.activity_materials.filter_by(
            activity=ActivityEnum.MANUFACTURING.aid
        ).all()

        for material in materials:
            if material.material_id in prices:
                bp.base_cost += (
                    prices[material.material_id]['price'] * material.quantity
                )

    db.session.commit()
    return True
