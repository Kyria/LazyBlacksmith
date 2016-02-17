# -*- encoding: utf-8 -*-
from lazyblacksmith.extension.celery_app import celery_app
from lazyblacksmith.models import ItemAdjustedPrice
from lazyblacksmith.models import db
from lazyblacksmith.utils.crestutils import get_all_items
from lazyblacksmith.utils.crestutils import get_crest


@celery_app.task(name="schedule.update_adjusted_price")
def update_adjusted_price():
    # get all items id we know ()

    # crest stuff
    crest = get_crest()
    item_adjusted_price = []
    count = 0

    marketPrice = get_all_items(crest.marketPrices())
    for itemPrice in marketPrice:
        count += 1
        item_adjusted_price.append({
            'item_id': itemPrice.type.id,
            'price': itemPrice.adjustedPrice
        })

    db.engine.execute(
        ItemAdjustedPrice.__table__.insert(),
        item_adjusted_price
    )

    return count, count
